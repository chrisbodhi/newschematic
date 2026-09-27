#!/usr/bin/env python3
"""Stamp content/blyg/*.md with blyg ids and maintain data/blyg/ledger.json.

See docs/blyg/conformance.md for the protocol rules this implements
(blygger-spec docs/protocol-v0.2.md, pinned at c5884b9).

Usage:
    blyg_stamp.py                 stamp everything, write changes
    blyg_stamp.py --note "..."    same, attaching a changelog note to every
                                   version this run creates
    blyg_stamp.py --amend         rewrite a still-unshipped latest version in
                                   place instead of bumping again (§5.2:
                                   draft saves are invisible) -- see
                                   plan_for_item for the exact rule
    blyg_stamp.py --dry-run       print planned changes, write nothing
    blyg_stamp.py --check         exit nonzero if stamping would change anything
    blyg_stamp.py pin <id>        promote the built items/{id}.json to a
                                   permanent pinned static file (§8)
"""

from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import json
import re
import secrets
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# The consuming site's root. These scripts ship inside the hugo-blyg module,
# so every default path is relative to where they're run from -- run them
# from the site root, as the site's workflows do.
REPO_ROOT = Path.cwd()
DEFAULT_CONTENT_DIR = REPO_ROOT / "content" / "blyg"
DEFAULT_LEDGER_PATH = REPO_ROOT / "data" / "blyg" / "ledger.json"
DEFAULT_PUBLIC_DIR = REPO_ROOT / "public"
DEFAULT_STATIC_DIR = REPO_ROOT / "static"
DEFAULT_PUBLISHED_REF = "origin/master"  # the branch a site deploys from; see --published-ref

AUTHORED_KINDS = ("fragment", "thread")
FRAGMENT_SOFT_CAP = 2000  # §5.3: publishers SHOULD cap fragments at 2,000 chars

CROCKFORD_ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"
BLYG_ID_RE_SRC = "[" + CROCKFORD_ALPHABET + "]{26}"

FRONT_MATTER_OPEN = "+++\n"

# §10.1: a line consisting solely of `![[` + a 26-character item id + `]]`
# (surrounding whitespace allowed) is a transclusion directive; `![[id@vN]]`
# is reserved and MUST be rejected at publish time. Anything else that
# merely looks similar is inert text.
DIRECTIVE_RE = re.compile(r"^\s*!\[\[(" + BLYG_ID_RE_SRC + r")(@v[0-9]+)?\]\]\s*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


class BlygStampError(Exception):
    """A hard error: never silently paper over these (missing files, etc)."""


def generate_blyg_id() -> str:
    """128 random bits, encoded as 26 lowercase Crockford base32 chars (§5.1)."""
    n = int.from_bytes(secrets.token_bytes(16), "big")
    chars = []
    for _ in range(26):
        chars.append(CROCKFORD_ALPHABET[n & 0b11111])
        n >>= 5
    return "".join(reversed(chars))


def is_valid_blyg_id(value: str) -> bool:
    if len(value) != 26:
        return False
    alphabet = set(CROCKFORD_ALPHABET)
    return all(c in alphabet for c in value)


def split_front_matter(text: str) -> tuple[str, str]:
    """Split a TOML-front-mattered file into (front_matter_toml, body).

    `body` is exactly what Hugo's .RawContent produces: the file's bytes
    after the closing `+++` delimiter line, untouched -- verified
    empirically against Hugo 0.151.0 (see docs/blyg/conformance.md),
    including the leading-newline and no-trailing-newline edge cases.
    """
    if not text.startswith(FRONT_MATTER_OPEN):
        raise BlygStampError("missing opening +++ front matter delimiter")
    idx = text.find("\n+++", len(FRONT_MATTER_OPEN))
    if idx == -1:
        raise BlygStampError("missing closing +++ front matter delimiter")
    fm = text[len(FRONT_MATTER_OPEN):idx]
    rest = text[idx + len("\n+++"):]
    if rest.startswith("\n"):
        body = rest[1:]
    else:
        body = rest
    return fm, body


def content_hash(body: str) -> str:
    """'sha256:' + hex(SHA-256(content_md as UTF-8)) (§5.1). Covers content_md only."""
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


EMPTY_CONTENT_HASH = content_hash("")


def find_directives(body: str) -> list[tuple[int, str, bool]]:
    """Every transclusion-directive line in `body`, as (line number,
    line, is_reserved_versioned_form). Lines inside fenced code blocks
    are inert text (§10.1) and skipped."""
    found = []
    fence: str | None = None
    for lineno, line in enumerate(body.split("\n"), start=1):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
                continue
        else:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not m.group(2).strip():
                fence = None
            continue
        d = DIRECTIVE_RE.match(line)
        if d:
            found.append((lineno, line.strip(), d.group(2) is not None))
    return found


def check_directives(path: Path, body: str) -> None:
    """Transclusion resolution (§10.2) isn't built yet, and every directive
    MUST resolve -- so any directive at all is a publish error for now,
    rather than shipping it as literal text with an empty `transclusions`."""
    for lineno, line, reserved in find_directives(body):
        if reserved:
            raise BlygStampError(
                f"{path}: body line {lineno}: {line!r} uses the reserved "
                f"![[id@vN]] form, which publishers MUST reject (§10.1)")
        raise BlygStampError(
            f"{path}: body line {lineno}: {line!r} is a transclusion "
            f"directive (§10.1), and every directive MUST resolve at publish "
            f"time (§10.2) -- resolution isn't implemented yet, so this "
            f"can't be published. Put it inside a code fence to keep it "
            f"as inert text.")


def parse_date_utc(value: str) -> datetime.datetime:
    """Parse a front-matter `date` string, defaulting to UTC when no offset
    is given -- matching Hugo's own behavior when no `timeZone` is
    configured (site has none; see docs/blyg/hazards.md)."""
    dt = datetime.datetime.fromisoformat(value)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def iso8601_utc(dt: datetime.datetime) -> str:
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def insert_blyg_id_line(text: str, blyg_id: str) -> str:
    """Insert `blyg_id = "..."` as its own line just before the closing
    +++, byte-identical otherwise. Never re-serializes the rest of the
    front matter."""
    idx = text.find("\n+++", len(FRONT_MATTER_OPEN))
    if idx == -1:
        raise BlygStampError("missing closing +++ front matter delimiter")
    return text[:idx] + f'\nblyg_id = "{blyg_id}"' + text[idx:]


@dataclass
class Item:
    path: Path
    rel_path: str
    front_matter: dict
    body: str
    blyg_id: str | None
    draft: bool
    withdrawn_flag: bool
    kind: str
    publish_at: datetime.datetime | None
    has_expiry: bool


def load_item(path: Path, content_dir: Path) -> Item:
    text = path.read_text(encoding="utf-8")
    fm_text, body = split_front_matter(text)
    try:
        fm = tomllib.loads(fm_text)
    except tomllib.TOMLDecodeError as exc:
        raise BlygStampError(f"{path}: invalid TOML front matter: {exc}") from exc
    lower = {k.lower(): v for k, v in fm.items()}
    kind = fm.get("blyg_kind", "thread")
    if kind not in AUTHORED_KINDS:
        raise BlygStampError(
            f"{path}: blyg_kind {kind!r} must be \"fragment\" or \"thread\" "
            f"(\"withdrawn\" is derived from blyg_withdrawn, never authored)")
    # Hugo decides "future" by publishDate (aliases pubdate, published),
    # falling back to date. Front-matter keys are case-insensitive to Hugo.
    when = next((lower[k] for k in ("publishdate", "pubdate", "published", "date")
                 if k in lower), None)
    return Item(
        path=path,
        rel_path=str(path.relative_to(content_dir.parent.parent)),
        front_matter=fm,
        body=body,
        blyg_id=fm.get("blyg_id"),
        draft=bool(lower.get("draft", False)),
        withdrawn_flag=bool(fm.get("blyg_withdrawn", False)),
        kind=kind,
        publish_at=parse_date_utc(str(when)) if when is not None else None,
        has_expiry=any(k in lower for k in ("expirydate", "unpublishdate")),
    )


def discover_items(content_dir: Path) -> list[Path]:
    if not content_dir.is_dir():
        return []
    return sorted(
        p for p in content_dir.glob("*.md")
        if p.name not in ("_index.md", "index.md")
    )


def load_ledger(ledger_path: Path) -> dict:
    if not ledger_path.exists():
        return {}
    with ledger_path.open(encoding="utf-8") as f:
        return json.load(f)


def save_ledger(ledger_path: Path, ledger: dict) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, sort_keys=True)
        f.write("\n")


@dataclass
class Plan:
    """One planned change to the ledger and/or a content file."""

    # "new" | "bump" | "amend" | "revert" | "withdraw" | "return" | "moved"
    # | "noop" | "draft-skip" | "future-skip"
    kind: str
    path: Path
    blyg_id: str | None = None
    detail: str = ""
    ledger_entry: dict | None = None
    write_blyg_id: bool = False
    warning: str | None = None


UNCHANGED_PLAN_KINDS = ("noop", "draft-skip", "future-skip")


def entry_state(entry: dict) -> tuple[str, bool, str]:
    return (entry["kind"], entry["withdrawn"], entry["last_hash"])


def desired_state(item: Item, entry: dict) -> tuple[str, bool, str]:
    """What the ledger should say for this file. While withdrawn, the
    body and the authored kind are invisible on the wire (the endcap is
    `kind: "withdrawn"` with empty content, §9), so neither can cause a
    new version until the item returns."""
    if item.withdrawn_flag:
        return (entry["kind"], True, EMPTY_CONTENT_HASH)
    return (item.kind, False, content_hash(item.body))


def wire_kind(state: tuple[str, bool, str]) -> str:
    kind, withdrawn, _ = state
    return "withdrawn" if withdrawn else kind


def transition(before_withdrawn: bool, after_withdrawn: bool) -> tuple[str, str | None]:
    """(plan kind, default changelog note) for a state change."""
    if after_withdrawn and not before_withdrawn:
        return "withdraw", "withdrawn"
    if before_withdrawn and not after_withdrawn:
        return "return", "returned"
    return "bump", None


def changelog_entry(version: int, at: str, note: str | None, kind: str) -> dict:
    # `kind` is ledger-private (the item document's changelog is stripped
    # back to version/at/note/pinned by modules/hugo-blyg): it's what lets
    # feed.xml label every past publish event with the kind it actually
    # had, e.g. `withdrawn` for an endcap the item has since returned from.
    return {"version": version, "at": at, "note": note, "kind": kind}


def plan_for_item(item: Item, ledger: dict, *, write: bool,
                  now: datetime.datetime, note: str | None = None,
                  published: dict | None = None) -> Plan:
    """Plan one file. `published` is the ledger as of the last deploy,
    and is only passed with --amend: when it is, a latest version that
    ledger doesn't contain yet has never been served, so it is rewritten
    in place (or reverted) instead of bumped again -- §5.2's "draft saves
    are invisible to the protocol". Without it, every ledgered version is
    assumed shipped, which can only ever over-count versions, never
    rewrite one a reader may already have seen."""
    warning = None
    if not item.withdrawn_flag:
        check_directives(item.path, item.body)
        if item.kind == "fragment" and len(item.body) > FRAGMENT_SOFT_CAP:
            warning = (f"{item.path.name}: fragment content_md is {len(item.body)} "
                       f"characters; §5.3 says publishers SHOULD cap fragments "
                       f"at {FRAGMENT_SOFT_CAP}")

    if item.blyg_id is None:
        if item.draft:
            return Plan(kind="draft-skip", path=item.path, detail="draft: skipped")
        if item.withdrawn_flag:
            raise BlygStampError(
                f"{item.path}: blyg_withdrawn on a never-published item -- there "
                f"is nothing to withdraw (§9); delete the file instead")
        if item.publish_at is None:
            raise BlygStampError(f"{item.path}: no `date` field to backfill from")
        if item.publish_at > now:
            # Hugo won't build it yet, so it isn't published yet: stamping
            # it now would put a publish event in the ledger that no reader
            # can see. Stamp it once its date has passed.
            return Plan(kind="future-skip", path=item.path,
                        detail=f"future-dated ({iso8601_utc(item.publish_at)}): skipped")
        if item.has_expiry:
            raise BlygStampError(
                f"{item.path}: expiryDate would make Hugo stop building this item, "
                f"but items/{{id}}.json MUST stay 200 forever once published (§4)")
        created = iso8601_utc(item.publish_at)

        if not write:
            # Ids are 128 random bits from a cryptographically strong
            # source (§5.1) -- generating one here just to print it would
            # show a real-looking id that a subsequent real run will
            # never actually produce (there is nothing to make the two
            # calls agree, nor should there be). Show no id at all rather
            # than a misleading one.
            return Plan(kind="new", path=item.path, blyg_id=None,
                        detail=f"would assign a new id, v1 @ {created}",
                        warning=warning)

        new_id = generate_blyg_id()
        while new_id in ledger:  # 2^-128, but free to rule out
            new_id = generate_blyg_id()
        entry = {
            "path": item.rel_path,
            "created": created,
            "version": 1,
            "kind": item.kind,
            "last_hash": content_hash(item.body),
            "withdrawn": False,
            "changelog": [changelog_entry(1, created, note, item.kind)],
        }
        return Plan(kind="new", path=item.path, blyg_id=new_id,
                    detail=f"assign id, v1 @ {created}",
                    ledger_entry=entry, write_blyg_id=True, warning=warning)

    if not is_valid_blyg_id(item.blyg_id):
        raise BlygStampError(f"{item.path}: blyg_id {item.blyg_id!r} is not "
                              f"26 lowercase Crockford base32 characters")

    entry = ledger.get(item.blyg_id)
    if entry is None:
        raise BlygStampError(
            f"{item.path}: has blyg_id {item.blyg_id} with no ledger entry "
            f"-- refusing to guess a version history"
        )
    if "kind" not in entry:
        raise BlygStampError(
            f"ledger entry {item.blyg_id} has no `kind` -- it predates kind "
            f"tracking; add \"kind\" (the authored kind) to the entry and to "
            f"each changelog entry by hand")

    # Anything that makes Hugo stop building a ledgered item would turn
    # items/{id}.json into a 404, and §4 says it MUST stay 200 forever
    # once published. Withdrawal (§9) is the only exit.
    unbuildable = None
    if item.draft:
        unbuildable = "draft = true"
    elif item.publish_at is not None and item.publish_at > now:
        unbuildable = f"a future date ({iso8601_utc(item.publish_at)})"
    elif item.has_expiry:
        unbuildable = "an expiryDate"
    if unbuildable:
        raise BlygStampError(
            f"{item.path}: {item.blyg_id} is in the ledger, but {unbuildable} "
            f"would stop Hugo building it, and items/{{id}}.json MUST stay 200 "
            f"forever once published (§4). Use blyg_withdrawn = true instead. "
            f"(If this item has genuinely never shipped, remove its blyg_id "
            f"line and its ledger entry to turn it back into a draft.)")

    new_entry = copy.deepcopy(entry)
    if entry["path"] != item.rel_path:
        new_entry["path"] = item.rel_path

    current = entry_state(entry)
    desired = desired_state(item, entry)
    if desired == current:
        if new_entry != entry:
            return Plan(kind="moved", path=item.path, blyg_id=item.blyg_id,
                        detail=f"path {entry['path']} -> {item.rel_path} (no version change)",
                        ledger_entry=(new_entry if write else None), warning=warning)
        detail = "withdrawn: no-op" if entry["withdrawn"] else "unchanged"
        return Plan(kind="noop", path=item.path, blyg_id=item.blyg_id,
                    detail=detail, warning=warning)

    new_entry["kind"], new_entry["withdrawn"], new_entry["last_hash"] = desired
    at_now = iso8601_utc(now)

    pub = None
    shipped_version = entry["version"]
    if published is not None:
        pub = published.get(item.blyg_id)
        shipped_version = pub["version"] if pub else 0
    unshipped = entry["changelog"][shipped_version:]
    can_amend = bool(unshipped) and not any(e.get("pinned") for e in unshipped)

    if can_amend and pub is not None and desired == entry_state(pub):
        # Every unshipped version is undone: back to exactly what shipped.
        new_entry["version"] = pub["version"]
        new_entry["changelog"] = entry["changelog"][:pub["version"]]
        verb = "would revert" if not write else "revert"
        return Plan(kind="revert", path=item.path, blyg_id=item.blyg_id,
                    detail=f"{verb} unshipped v{entry['version']} -> shipped v{pub['version']}",
                    ledger_entry=(new_entry if write else None), warning=warning)

    if can_amend:
        if pub is None and desired[1]:
            raise BlygStampError(
                f"{item.path}: blyg_withdrawn on an item that has never shipped "
                f"-- there is nothing to withdraw (§9); remove its blyg_id line "
                f"and ledger entry (or the file) instead")
        base_withdrawn = pub["withdrawn"] if pub else False
        plan_kind, default_note = transition(base_withdrawn, desired[1])
        if pub is None:
            plan_kind = "new"
        old_note = unshipped[-1].get("note")
        version = shipped_version + 1
        at = entry["created"] if version == 1 else at_now
        new_entry["version"] = version
        new_entry["changelog"] = entry["changelog"][:shipped_version] + [
            changelog_entry(version, at,
                            note if note is not None else (default_note or old_note),
                            wire_kind(desired))
        ]
        verb = "would amend" if not write else "amend"
        return Plan(kind="amend", path=item.path, blyg_id=item.blyg_id,
                    detail=f"{verb} unshipped v{version} ({plan_kind}) @ {at}",
                    ledger_entry=(new_entry if write else None), warning=warning)

    plan_kind, default_note = transition(current[1], desired[1])
    version = entry["version"] + 1
    new_entry["version"] = version
    new_entry["changelog"] = entry["changelog"] + [
        changelog_entry(version, at_now, note if note is not None else default_note,
                        wire_kind(desired))
    ]
    if write:
        detail = {"withdraw": f"endcap v{version} @ {at_now}",
                  "return": f"v{version} @ {at_now}"}.get(
            plan_kind, f"bump v{entry['version']} -> v{version} @ {at_now}")
    else:
        detail = {"withdraw": f"would withdraw: endcap v{version} @ {at_now}",
                  "return": f"would return: v{version} @ {at_now}"}.get(
            plan_kind, f"would bump v{entry['version']} -> v{version} @ {at_now}")
    if current[0] != desired[0] and not desired[1]:
        detail += f" (kind {current[0]} -> {desired[0]})"
    return Plan(kind=plan_kind, path=item.path, blyg_id=item.blyg_id, detail=detail,
                ledger_entry=(new_entry if write else None), warning=warning)


def run_stamp(content_dir: Path, ledger_path: Path, *, write: bool,
              now: datetime.datetime | None = None, note: str | None = None,
              published: dict | None = None) -> list[Plan]:
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)
    ledger = load_ledger(ledger_path)
    plans: list[Plan] = []
    seen: dict[str, Path] = {}

    items = [load_item(path, content_dir) for path in discover_items(content_dir)]
    for item in items:
        if item.blyg_id is not None:
            if item.blyg_id in seen:
                raise BlygStampError(
                    f"{item.path} and {seen[item.blyg_id]} both carry blyg_id "
                    f"{item.blyg_id} -- ids are one item's permanent identity (§5.1)")
            seen[item.blyg_id] = item.path

    # §4: once published, items/{id}.json MUST stay 200 forever. A ledger
    # entry whose file is gone would silently drop out of every surface.
    for blyg_id, entry in sorted(ledger.items()):
        if blyg_id not in seen:
            raise BlygStampError(
                f"ledger entry {blyg_id} ({entry.get('path')}) has no file in "
                f"{content_dir} carrying its blyg_id -- a published item MUST "
                f"keep serving items/{blyg_id}.json forever (§4); restore the "
                f"file (withdraw it with blyg_withdrawn = true if it should go)")

    for item in items:
        plan = plan_for_item(item, ledger, write=write, now=now, note=note,
                             published=published)
        plans.append(plan)

        if not write or plan.kind in UNCHANGED_PLAN_KINDS:
            continue

        if plan.ledger_entry is not None:
            ledger[plan.blyg_id] = plan.ledger_entry

        if plan.write_blyg_id:
            text = item.path.read_text(encoding="utf-8")
            item.path.write_text(insert_blyg_id_line(text, plan.blyg_id), encoding="utf-8")

    if write:
        save_ledger(ledger_path, ledger)

    return plans


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def run_media_stamp(media_dir: Path, media_ledger_path: Path, *, write: bool,
                    published: dict | None = None) -> list[str]:
    """Track every file under the blyg media directory by content hash.

    §5.4: a media URL MUST always serve the same bytes once published, and
    §8 rule 4: media referenced by a pinned version MUST be retained
    forever. So a tracked file changing or disappearing is a hard error --
    publish a new file under a new name instead. With --amend (`published`
    given), a file the last deploy didn't carry yet may still change.
    """
    ledger = load_ledger(media_ledger_path)
    on_disk = {}
    if media_dir.is_dir():
        for p in sorted(media_dir.rglob("*")):
            if p.is_file() and not any(part.startswith(".") for part in p.relative_to(media_dir).parts):
                on_disk[p.relative_to(media_dir).as_posix()] = file_hash(p)

    def shipped(rel: str) -> bool:
        return published is None or rel in published

    changes = []
    for rel, recorded in sorted(ledger.items()):
        if rel not in on_disk:
            if shipped(rel):
                raise BlygStampError(
                    f"media/{rel} is gone -- published media MUST keep serving the "
                    f"same bytes forever (§5.4, §8 rule 4); restore it")
            changes.append(f"[drop       ] media/{rel} (never shipped)")
            del ledger[rel]
        elif on_disk[rel] != recorded:
            if shipped(rel):
                raise BlygStampError(
                    f"media/{rel} changed bytes -- a published media URL MUST always "
                    f"serve the same bytes (§5.4); restore it and publish the new "
                    f"version under a new file name")
            changes.append(f"[amend      ] media/{rel} (never shipped)")
            ledger[rel] = on_disk[rel]
    for rel, h in on_disk.items():
        if rel not in ledger:
            changes.append(f"[new        ] media/{rel}")
            ledger[rel] = h

    if write and (changes or media_ledger_path.exists()):
        save_ledger(media_ledger_path, ledger)
    return changes


def load_published_json(ref: str, path: Path) -> dict:
    """The JSON file at `path` as of git `ref` -- i.e. as last deployed."""
    try:
        rel = path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        raise BlygStampError(f"--amend needs {path} to live inside {REPO_ROOT}") from None
    verify = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--verify",
                             "--quiet", f"{ref}^{{commit}}"], capture_output=True)
    if verify.returncode != 0:
        raise BlygStampError(
            f"--amend needs {ref} to tell which versions have shipped, and it "
            f"doesn't resolve here; fetch it first, or pass --published-ref")
    shown = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{ref}:./{rel}"],
                           capture_output=True, text=True)
    if shown.returncode != 0:
        return {}  # the file didn't exist yet at ref: nothing had shipped
    return json.loads(shown.stdout)


def format_plan(plan: Plan) -> str:
    if plan.blyg_id is not None:
        id_part = plan.blyg_id
    elif plan.kind == "new":
        id_part = "(pending)"  # assigned on write, not shown in a dry-run/check
    else:
        id_part = "(none)"
    return f"[{plan.kind:11s}] {plan.path.name:40s} {id_part}  {plan.detail}"


def cmd_stamp(args: argparse.Namespace) -> int:
    content_dir = Path(args.content_dir)
    ledger_path = Path(args.ledger_path)
    media_dir = Path(args.media_dir) if args.media_dir else Path(args.static_dir) / "blyg" / "media"
    media_ledger_path = (Path(args.media_ledger_path) if args.media_ledger_path
                         else ledger_path.parent / "media.json")

    write = not (args.dry_run or args.check)
    published = published_media = None
    if args.amend:
        published = load_published_json(args.published_ref, ledger_path)
        published_media = load_published_json(args.published_ref, media_ledger_path)

    # Media first: it validates without touching content, so a media
    # error never leaves content files half-stamped.
    media_changes = run_media_stamp(media_dir, media_ledger_path, write=write,
                                    published=published_media)
    plans = run_stamp(content_dir, ledger_path, write=write, note=args.note,
                      published=published)

    changing = [p for p in plans if p.kind not in UNCHANGED_PLAN_KINDS]

    for plan in plans:
        print(format_plan(plan))
    for line in media_changes:
        print(line)
    for plan in plans:
        if plan.warning:
            print(f"warning: {plan.warning}", file=sys.stderr)

    verb = "changed" if write else "would change"
    print(f"\n{len(plans)} item(s) scanned, {len(changing)} {verb}; "
          f"{len(media_changes)} media change(s).")

    if args.check:
        return 1 if (changing or media_changes) else 0
    return 0


def build_pin_document(built: dict, changelog_entry: dict) -> dict:
    """Shape a pin file (§8) from the live item document plus its own
    changelog entry. This is NOT a copy of the live document: §8's own
    example shows version/at/note/pinned as flat top-level fields (never
    a changelog array), and no created, updated, or media key at all --
    a pin is a frozen citation of one version, not a live item summary.
    """
    doc = {
        "blyg": built["blyg"],
        "id": built["id"],
        "kind": built["kind"],
        "version": changelog_entry["version"],
        "at": changelog_entry["at"],
        "note": changelog_entry["note"],
        "pinned": True,
        "origin": built["origin"],
        "content_md": built["content_md"],
        "content_html": built["content_html"],
        "content_hash": built["content_hash"],
    }
    if "transclusions" in built:
        doc["transclusions"] = built["transclusions"]
    return doc


def cmd_pin(args: argparse.Namespace) -> int:
    ledger_path = Path(args.ledger_path)
    public_dir = Path(args.public_dir)
    static_dir = Path(args.static_dir)

    ledger = load_ledger(ledger_path)
    entry = ledger.get(args.id)
    if entry is None:
        raise BlygStampError(f"no ledger entry for id {args.id}")

    if entry["withdrawn"]:
        raise BlygStampError(
            f"{args.id} is currently withdrawn -- its live version is a §9 "
            f"endcap, and withdrawal endcaps MUST NOT be pinned (§8 rule 2)"
        )

    built_path = public_dir / "blyg" / "items" / f"{args.id}.json"
    if not built_path.exists():
        raise BlygStampError(f"{built_path} does not exist -- build the site first")

    built = json.loads(built_path.read_text(encoding="utf-8"))
    built_version = built.get("version")
    ledger_version = entry["version"]
    if built_version != ledger_version:
        raise BlygStampError(
            f"built version {built_version!r} does not match ledger version "
            f"{ledger_version!r} for {args.id} -- rebuild the site before pinning"
        )

    changelog_entry = next(
        (e for e in entry["changelog"] if e["version"] == ledger_version), None
    )
    if changelog_entry is None:
        raise BlygStampError(
            f"no changelog entry for {args.id} v{ledger_version} -- ledger is inconsistent"
        )

    target_dir = static_dir / "blyg" / "items" / args.id
    target_path = target_dir / f"v{ledger_version}.json"
    pin_doc = build_pin_document(built, changelog_entry)

    print(f"pin {args.id} v{ledger_version} -> {target_path}")
    if args.dry_run:
        return 0

    target_dir.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(pin_doc, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")

    changelog_entry["pinned"] = True
    save_ledger(ledger_path, ledger)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-dir", default=str(DEFAULT_CONTENT_DIR))
    parser.add_argument("--ledger-path", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--public-dir", default=str(DEFAULT_PUBLIC_DIR))
    parser.add_argument("--static-dir", default=str(DEFAULT_STATIC_DIR))
    parser.add_argument("--dry-run", action="store_true",
                         help="print planned changes, write nothing")
    parser.add_argument("--check", action="store_true",
                         help="exit nonzero if stamping would change anything")
    parser.add_argument("--note", default=None,
                         help="changelog note for every version this run creates")
    parser.add_argument("--amend", action="store_true",
                         help="rewrite still-unshipped latest versions in place "
                              "instead of bumping again (needs --published-ref)")
    parser.add_argument("--published-ref", default=DEFAULT_PUBLISHED_REF,
                         help="git ref whose ledger is what has shipped "
                              "(default: %(default)s)")
    parser.add_argument("--media-dir", default=None,
                         help="default: <static-dir>/blyg/media")
    parser.add_argument("--media-ledger-path", default=None,
                         help="default: media.json next to --ledger-path")

    sub = parser.add_subparsers(dest="command")
    pin_parser = sub.add_parser("pin", help="promote a built item version to a pinned static file")
    pin_parser.add_argument("id")
    # SUPPRESS, not store_true's False default: a subparser's defaults
    # overwrite the parent namespace, so `--dry-run pin <id>` used to lose
    # its --dry-run here and write a real, irrevocable pin.
    pin_parser.add_argument("--dry-run", action="store_true", default=argparse.SUPPRESS)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "pin":
            return cmd_pin(args)
        return cmd_stamp(args)
    except BlygStampError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
