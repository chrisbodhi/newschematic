#!/usr/bin/env python3
"""Stamp content/blyg/*.md with blyg ids and maintain data/blyg/ledger.json.

See docs/blyg/conformance.md for the protocol rules this implements
(blygger-spec docs/protocol-v0.2.md, pinned at c5884b9).

Usage:
    blyg_stamp.py                 stamp everything, write changes
    blyg_stamp.py --dry-run       print planned changes, write nothing
    blyg_stamp.py --check         exit nonzero if stamping would change anything
    blyg_stamp.py pin <id>        promote the built items/{id}.json to a
                                   permanent pinned static file (§8)
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import secrets
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTENT_DIR = REPO_ROOT / "content" / "blyg"
DEFAULT_LEDGER_PATH = REPO_ROOT / "data" / "blyg" / "ledger.json"
DEFAULT_PUBLIC_DIR = REPO_ROOT / "public"
DEFAULT_STATIC_DIR = REPO_ROOT / "static"

CROCKFORD_ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"
BLYG_ID_RE_SRC = "[" + CROCKFORD_ALPHABET + "]{26}"

FRONT_MATTER_OPEN = "+++\n"


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


def now_iso8601_utc() -> str:
    return iso8601_utc(datetime.datetime.now(datetime.timezone.utc))


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


def load_item(path: Path, content_dir: Path) -> Item:
    text = path.read_text(encoding="utf-8")
    fm_text, body = split_front_matter(text)
    try:
        fm = tomllib.loads(fm_text)
    except tomllib.TOMLDecodeError as exc:
        raise BlygStampError(f"{path}: invalid TOML front matter: {exc}") from exc
    return Item(
        path=path,
        rel_path=str(path.relative_to(content_dir.parent.parent)),
        front_matter=fm,
        body=body,
        blyg_id=fm.get("blyg_id"),
        draft=bool(fm.get("draft", False)),
        withdrawn_flag=bool(fm.get("blyg_withdrawn", False)),
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

    kind: str  # "new" | "bump" | "withdraw" | "return" | "noop" | "draft-skip"
    path: Path
    blyg_id: str | None = None
    detail: str = ""
    ledger_entry: dict | None = None
    write_blyg_id: bool = False


def plan_for_item(item: Item, ledger: dict, *, write: bool) -> Plan:
    if item.draft:
        return Plan(kind="draft-skip", path=item.path, blyg_id=item.blyg_id,
                     detail="draft: skipped")

    if item.blyg_id is None:
        # New item: assign an id, seed the ledger from `date`.
        if "date" not in item.front_matter:
            raise BlygStampError(f"{item.path}: no `date` field to backfill from")
        created = iso8601_utc(parse_date_utc(str(item.front_matter["date"])))

        if not write:
            # Ids are 128 random bits from a cryptographically strong
            # source (§5.1) -- generating one here just to print it would
            # show a real-looking id that a subsequent real run will
            # never actually produce (there is nothing to make the two
            # calls agree, nor should there be). Show no id at all rather
            # than a misleading one.
            return Plan(kind="new", path=item.path, blyg_id=None,
                        detail=f"would assign a new id, v1 @ {created}")

        new_id = generate_blyg_id()
        entry = {
            "path": item.rel_path,
            "created": created,
            "version": 1,
            "last_hash": content_hash(item.body),
            "withdrawn": False,
            "changelog": [{"version": 1, "at": created, "note": None}],
        }
        return Plan(kind="new", path=item.path, blyg_id=new_id,
                    detail=f"assign id, v1 @ {created}",
                    ledger_entry=entry, write_blyg_id=True)

    if not is_valid_blyg_id(item.blyg_id):
        raise BlygStampError(f"{item.path}: blyg_id {item.blyg_id!r} is not "
                              f"26 lowercase Crockford base32 characters")

    entry = ledger.get(item.blyg_id)
    if entry is None:
        raise BlygStampError(
            f"{item.path}: has blyg_id {item.blyg_id} with no ledger entry "
            f"-- refusing to guess a version history"
        )

    # Withdrawal transition: front matter says withdrawn, ledger doesn't yet.
    if item.withdrawn_flag and not entry["withdrawn"]:
        new_version = entry["version"] + 1
        at = now_iso8601_utc()
        new_entry = dict(entry)
        new_entry["version"] = new_version
        new_entry["withdrawn"] = True
        new_entry["last_hash"] = EMPTY_CONTENT_HASH
        new_entry["changelog"] = entry["changelog"] + [
            {"version": new_version, "at": at, "note": "withdrawn"}
        ]
        verb = "would withdraw: endcap" if not write else "endcap"
        return Plan(kind="withdraw", path=item.path, blyg_id=item.blyg_id,
                    detail=f"{verb} v{new_version} @ {at}",
                    ledger_entry=(new_entry if write else None))

    # Return transition: ledger says withdrawn, front matter no longer does.
    if entry["withdrawn"] and not item.withdrawn_flag:
        new_version = entry["version"] + 1
        at = now_iso8601_utc()
        new_hash = content_hash(item.body)
        new_entry = dict(entry)
        new_entry["version"] = new_version
        new_entry["withdrawn"] = False
        new_entry["last_hash"] = new_hash
        new_entry["changelog"] = entry["changelog"] + [
            {"version": new_version, "at": at, "note": "returned"}
        ]
        verb = "would return:" if not write else ""
        return Plan(kind="return", path=item.path, blyg_id=item.blyg_id,
                    detail=f"{verb} v{new_version} @ {at}".strip(),
                    ledger_entry=(new_entry if write else None))

    # Steady withdrawn state: never re-hash or re-bump while withdrawn.
    if entry["withdrawn"]:
        return Plan(kind="noop", path=item.path, blyg_id=item.blyg_id,
                     detail="withdrawn: no-op")

    # Normal idempotency / bump-on-change.
    current_hash = content_hash(item.body)
    if current_hash == entry["last_hash"]:
        return Plan(kind="noop", path=item.path, blyg_id=item.blyg_id,
                     detail="unchanged")

    new_version = entry["version"] + 1
    at = now_iso8601_utc()
    new_entry = dict(entry)
    new_entry["version"] = new_version
    new_entry["last_hash"] = current_hash
    new_entry["changelog"] = entry["changelog"] + [
        {"version": new_version, "at": at, "note": None}
    ]
    verb = "would bump" if not write else "bump"
    return Plan(kind="bump", path=item.path, blyg_id=item.blyg_id,
                detail=f"{verb} v{entry['version']} -> v{new_version} @ {at}",
                ledger_entry=(new_entry if write else None))


def run_stamp(content_dir: Path, ledger_path: Path, *, write: bool) -> list[Plan]:
    ledger = load_ledger(ledger_path)
    plans: list[Plan] = []

    for path in discover_items(content_dir):
        item = load_item(path, content_dir)
        plan = plan_for_item(item, ledger, write=write)
        plans.append(plan)

        if not write:
            continue

        if plan.kind == "draft-skip" or plan.kind == "noop":
            continue

        if plan.ledger_entry is not None:
            ledger[plan.blyg_id] = plan.ledger_entry

        if plan.write_blyg_id:
            text = path.read_text(encoding="utf-8")
            path.write_text(insert_blyg_id_line(text, plan.blyg_id), encoding="utf-8")

    if write:
        save_ledger(ledger_path, ledger)

    return plans


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

    write = not (args.dry_run or args.check)
    plans = run_stamp(content_dir, ledger_path, write=write)

    changing = [p for p in plans if p.kind not in ("noop", "draft-skip")]

    for plan in plans:
        print(format_plan(plan))

    verb = "changed" if write else "would change"
    print(f"\n{len(plans)} item(s) scanned, {len(changing)} {verb}.")

    if args.check:
        return 1 if changing else 0
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

    sub = parser.add_subparsers(dest="command")
    pin_parser = sub.add_parser("pin", help="promote a built item version to a pinned static file")
    pin_parser.add_argument("id")
    pin_parser.add_argument("--dry-run", action="store_true")

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
