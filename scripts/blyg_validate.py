#!/usr/bin/env python3
"""Validate a built blyg surface (public/blyg/) against the ledger and
blygger-spec docs/protocol-v0.2.md (pinned at c5884b9).

This is the build-side half of docs/blyg/conformance.md: everything
scripts/blyg_stamp.py can't see because Hugo produces it -- the rendered
content_html above all -- plus a cross-check that every surface agrees
with data/blyg/ledger.json. CI runs it after `hugo --minify`, before
anything ships.

Usage:
    blyg_validate.py [--public-dir public] [--ledger-path data/blyg/ledger.json]

Exits 1 and lists every problem found; 0 when the surface conforms.
"""

from __future__ import annotations

import argparse
import datetime
import email.utils
import html.parser
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))

import blyg_stamp as bs  # noqa: E402

BLYG_NS = "https://blygger.org/ns/0.1"
ISO_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
GUID_RE = re.compile(r"^blyg:(" + bs.BLYG_ID_RE_SRC + r"):v([1-9][0-9]*)$")
PIN_RE = re.compile(r"^v([1-9][0-9]*)\.json$")
FEED_WINDOW = 50

# Attributes whose value is one URL, and the subset that embeds media.
URL_ATTRS = {"href", "src", "poster", "cite", "action", "formaction", "data",
             "background", "longdesc"}
EMBED_TAGS = {"img", "source", "video", "audio", "track", "embed", "object", "input"}
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)([^'\")]*)\1\s*\)")
SAFE_SCHEMES = ("http:", "https:", "mailto:", "tel:", "data:")


class Problems(list):
    def add(self, where: str, msg: str) -> None:
        self.append(f"{where}: {msg}")


def is_iso_z(value) -> bool:
    return isinstance(value, str) and bool(ISO_Z_RE.match(value))


class _HTMLCollector(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str, str]] = []  # (tag, attr, url)

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value is None:
                continue
            if name in URL_ATTRS:
                self.refs.append((tag, name, value.strip()))
            elif name == "srcset":
                for candidate in value.split(","):
                    parts = candidate.split()
                    if parts:
                        self.refs.append((tag, name, parts[0]))
            elif name == "style":
                for m in CSS_URL_RE.finditer(value):
                    self.refs.append((tag, "style url()", m.group(2).strip()))


def check_content_html(where: str, content_html: str, origin: str,
                       public_blyg: Path, problems: Problems) -> None:
    """§7: <description> HTML MUST be self-contained -- absolute media
    URLs, no dependence on the origin's stylesheets or scripts -- and
    §5.4: media MUST be immutable, which only files under the origin's
    media/ directory are held to (scripts/blyg_stamp.py)."""
    collector = _HTMLCollector()
    collector.feed(content_html)
    collector.close()
    origin_host = urlsplit(origin).netloc
    media_prefix = origin + "media/"

    for tag, attr, url in collector.refs:
        if url == "" or url.startswith("#"):
            continue  # in-document anchors (footnotes) travel with the HTML
        lowered = url.lower()
        if lowered.startswith("//"):
            url = "https:" + url
            lowered = url.lower()
        if not lowered.startswith(SAFE_SCHEMES):
            problems.add(where, f"<{tag} {attr}> has non-absolute URL {url!r} -- "
                                f"content_html MUST be self-contained (§7)")
            continue
        parts = urlsplit(url)
        on_origin = parts.netloc == origin_host
        if tag in ("script", "link") and on_origin:
            problems.add(where, f"<{tag}> loads {url} from the origin -- content_html "
                                f"MUST NOT depend on the origin's scripts or stylesheets (§7)")
        embedded = (tag in EMBED_TAGS and attr in ("src", "srcset", "poster", "data")) \
            or attr == "style url()"
        if embedded and on_origin:
            if not url.startswith(media_prefix):
                problems.add(where, f"<{tag} {attr}> embeds {url}, outside {media_prefix} -- "
                                    f"only blyg media/ files are held immutable (§5.4); "
                                    f"move it to static/blyg/media/")
            elif not (public_blyg / url[len(origin):].split("?")[0]).is_file():
                problems.add(where, f"<{tag} {attr}> embeds {url}, which isn't in the build")


def check_manifest(public_blyg: Path, problems: Problems) -> dict | None:
    path = public_blyg / "blyg.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.add("blyg.json", f"unreadable: {exc}")
        return None
    expect = {"blyg": "0.2", "feed": "feed.xml", "items": "items/index.json"}
    for key, value in expect.items():
        if manifest.get(key) != value:
            problems.add("blyg.json", f"{key} is {manifest.get(key)!r}, expected {value!r}")
    if manifest.get("level") != 1:
        problems.add("blyg.json", f"level is {manifest.get('level')!r}; only 1 is built")
    for key in ("generator", "site", "title"):
        if not isinstance(manifest.get(key), str) or not manifest[key]:
            problems.add("blyg.json", f"missing {key}")
    if not str(manifest.get("site", "")).endswith("/"):
        problems.add("blyg.json", "site must be the origin base URL, ending in /")
    if not is_iso_z(manifest.get("updated")):
        problems.add("blyg.json", f"updated {manifest.get('updated')!r} is not ISO 8601 UTC")
    if "blogroll" in manifest and not (public_blyg / "blogroll.opml").is_file():
        problems.add("blyg.json", "blogroll key present but blogroll.opml isn't served (§6.1)")
    if "author" in manifest and not isinstance(manifest["author"], dict):
        problems.add("blyg.json", "author must be an object")
    return manifest


def check_item(blyg_id: str, entry: dict, origin: str, public_blyg: Path,
               problems: Problems) -> dict | None:
    where = f"items/{blyg_id}.json"
    path = public_blyg / "items" / f"{blyg_id}.json"
    if not path.is_file():
        problems.add(where, "missing -- a published item MUST return 200 forever (§4)")
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        problems.add(where, f"not JSON: {exc}")
        return None

    if doc.get("blyg") != "0.2":
        problems.add(where, f"blyg is {doc.get('blyg')!r}, expected '0.2'")
    if doc.get("id") != blyg_id or not bs.is_valid_blyg_id(str(doc.get("id"))):
        problems.add(where, f"id {doc.get('id')!r} doesn't match file name / isn't a blyg id")
    if doc.get("origin") != origin:
        problems.add(where, f"origin {doc.get('origin')!r} != manifest site {origin!r}")
    for reserved in ("forked_from", "generated"):
        if reserved in doc:
            problems.add(where, f"carries {reserved!r}, which this publisher never emits (§5.6/§5.7)")

    kind = doc.get("kind")
    withdrawn = bool(entry.get("withdrawn"))
    expected_kind = "withdrawn" if withdrawn else entry.get("kind")
    if kind != expected_kind:
        problems.add(where, f"kind {kind!r}, ledger says {expected_kind!r}")
    if kind not in ("fragment", "thread", "withdrawn"):
        problems.add(where, f"kind {kind!r} is not a 0.2 kind (§5.3)")

    version = doc.get("version")
    if version != entry.get("version"):
        problems.add(where, f"version {version!r}, ledger says {entry.get('version')!r}")
    changelog = doc.get("changelog")
    if not isinstance(changelog, list) or not changelog:
        problems.add(where, "changelog missing or empty")
    else:
        if [c.get("version") for c in changelog] != list(range(1, len(changelog) + 1)):
            problems.add(where, "changelog versions aren't exactly 1..n (§5.2)")
        if changelog[-1].get("version") != version:
            problems.add(where, "latest changelog version != version")
        if doc.get("updated") != changelog[-1].get("at"):
            problems.add(where, "updated MUST equal the latest changelog entry's at (§5.2)")
        for c in changelog:
            if not is_iso_z(c.get("at")):
                problems.add(where, f"changelog v{c.get('version')} at {c.get('at')!r} isn't ISO 8601 UTC")
            extra = set(c) - {"version", "at", "note", "pinned"}
            if extra:
                problems.add(where, f"changelog v{c.get('version')} leaks ledger-private keys {sorted(extra)}")
            if "pinned" in c and c["pinned"] is not True:
                problems.add(where, f"changelog v{c.get('version')} pinned must be true or absent")
    for key in ("created", "updated"):
        if not is_iso_z(doc.get(key)):
            problems.add(where, f"{key} {doc.get(key)!r} isn't ISO 8601 UTC (§4)")

    content_md = doc.get("content_md", None)
    content_html = doc.get("content_html", None)
    if not isinstance(content_md, str) or not isinstance(content_html, str):
        problems.add(where, "content_md/content_html missing")
        return doc
    if doc.get("content_hash") != bs.content_hash(content_md):
        problems.add(where, "content_hash != sha256(content_md) (§5.1)")
    if doc.get("content_hash") != entry.get("last_hash"):
        problems.add(where, "content_hash != ledger last_hash (unstamped edit?)")

    if entry.get("kind") == "thread":
        if doc.get("transclusions") != []:
            problems.add(where, "threads MUST carry transclusions (always [] here) (§10.3)")
    elif "transclusions" in doc:
        problems.add(where, "fragments MUST omit transclusions (§10.3)")

    media = doc.get("media")
    if not isinstance(media, list):
        problems.add(where, "media must be an array")
        media = []
    if withdrawn:
        if content_md or content_html or media:
            problems.add(where, "withdrawal endcap MUST have empty content_md/content_html and media [] (§9)")
        return doc

    for lineno, line, _ in bs.find_directives(content_md):
        problems.add(where, f"content_md line {lineno} {line!r} is an unresolved transclusion directive (§10.2)")
    check_content_html(where, content_html, origin, public_blyg, problems)
    for m in media:
        url = m.get("url") if isinstance(m, dict) else None
        if not url or not m.get("mime"):
            problems.add(where, f"media entry {m!r} needs url and mime (§5.4)")
            continue
        rel = url[len(origin):] if url.startswith(origin) else url
        if "://" in rel or not (public_blyg / rel).is_file():
            problems.add(where, f"media {url} isn't served from the origin's media/")
    return doc


def check_index(public_blyg: Path, ledger: dict, docs: dict, problems: Problems) -> None:
    where = "items/index.json"
    try:
        index = json.loads((public_blyg / "items" / "index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.add(where, f"unreadable: {exc}")
        return
    rows = index.get("items")
    if not isinstance(rows, list):
        problems.add(where, "items must be an array")
        return
    ids = [r.get("id") for r in rows]
    if len(ids) != len(set(ids)):
        problems.add(where, "duplicate ids")
    missing = set(ledger) - set(ids)
    extra = set(ids) - set(ledger)
    for i in sorted(missing):
        problems.add(where, f"{i} is missing -- the index lists every item ever published (§6.2)")
    for i in sorted(extra):
        problems.add(where, f"{i} isn't in the ledger")
    updated = [r.get("updated") for r in rows]
    if updated != sorted(updated, reverse=True):
        problems.add(where, "not ordered by updated descending (§6.2)")
    if rows and index.get("updated") != max(updated):
        problems.add(where, "updated != newest item's updated")
    for r in rows:
        doc = docs.get(r.get("id"))
        if doc is None:
            continue
        for key in ("kind", "created", "updated", "version"):
            if r.get(key) != doc.get(key):
                problems.add(where, f"{r.get('id')} {key} {r.get(key)!r} != item document's {doc.get(key)!r}")


def check_pins(public_blyg: Path, ledger: dict, origin: str, problems: Problems) -> None:
    items_dir = public_blyg / "items"
    served = set()
    if items_dir.is_dir():
        for d in items_dir.iterdir():
            if not d.is_dir():
                continue
            for f in d.iterdir():
                m = PIN_RE.match(f.name)
                where = f"items/{d.name}/{f.name}"
                if not m:
                    problems.add(where, "unexpected file")
                    continue
                n = int(m.group(1))
                served.add((d.name, n))
                entry = ledger.get(d.name)
                if entry is None:
                    problems.add(where, "pin for an id not in the ledger")
                    continue
                if n > len(entry["changelog"]) or not entry["changelog"][n - 1].get("pinned"):
                    problems.add(where, "served, but the ledger doesn't record the pin")
                try:
                    doc = json.loads(f.read_text(encoding="utf-8"))
                except ValueError as exc:
                    problems.add(where, f"not JSON: {exc}")
                    continue
                if doc.get("id") != d.name or doc.get("version") != n or doc.get("pinned") is not True:
                    problems.add(where, "id/version/pinned don't match the path (§8)")
                if doc.get("kind") not in ("fragment", "thread"):
                    problems.add(where, "withdrawal endcaps MUST NOT be pinned (§8 rule 2)")
                if doc.get("content_hash") != bs.content_hash(doc.get("content_md", "")):
                    problems.add(where, "content_hash != sha256(content_md)")
                if doc.get("origin") != origin:
                    problems.add(where, "origin != manifest site")
                if "media" in doc:
                    problems.add(where, "pinned documents carry no media array (§8 rule 4)")
    for blyg_id, entry in ledger.items():
        for c in entry["changelog"]:
            if c.get("pinned") and (blyg_id, c["version"]) not in served:
                problems.add(f"items/{blyg_id}/v{c['version']}.json",
                             "ledger records a pin but the file isn't served -- MUST return 200 forever (§8)")


def check_feed(public_blyg: Path, ledger: dict, docs: dict, manifest: dict,
               origin: str, problems: Problems) -> None:
    where = "feed.xml"
    try:
        root = ET.parse(public_blyg / "feed.xml").getroot()
    except (OSError, ET.ParseError) as exc:
        problems.add(where, f"unparseable: {exc}")
        return
    if root.tag != "rss" or root.get("version") != "2.0":
        problems.add(where, "not an RSS 2.0 document (§7)")
    channel = root.find("channel")
    if channel is None:
        problems.add(where, "no <channel>")
        return
    q = lambda name: f"{{{BLYG_NS}}}{name}"  # noqa: E731
    if (channel.findtext(q("manifest")) or "").strip() != origin + "blyg.json":
        problems.add(where, "<blyg:manifest> MUST point at the manifest (§7)")
    for name in ("title", "link", "description"):
        if channel.find(name) is None:
            problems.add(where, f"channel lacks <{name}> (RSS 2.0)")

    entries = channel.findall("item")
    if len(entries) > FEED_WINDOW:
        problems.add(where, f"{len(entries)} entries; window is {FEED_WINDOW} (§7)")
    last_pub = None
    per_id: dict[str, list[int]] = {}
    for n, item in enumerate(entries, start=1):
        w = f"{where} item {n}"
        guid = item.find("guid")
        m = GUID_RE.match(guid.text or "") if guid is not None else None
        if not m or guid.get("isPermaLink") != "false":
            problems.add(w, "guid MUST be blyg:{id}:v{n} with isPermaLink=\"false\" (§7)")
            continue
        blyg_id, version = m.group(1), int(m.group(2))
        per_id.setdefault(blyg_id, []).append(version)
        if item.findtext(q("id")) != blyg_id or item.findtext(q("version")) != str(version):
            problems.add(w, "blyg:id / blyg:version disagree with the guid")
        entry, doc = ledger.get(blyg_id), docs.get(blyg_id)
        if entry is None or doc is None:
            problems.add(w, f"{blyg_id} isn't a built ledger item")
            continue
        if version > entry["version"]:
            problems.add(w, f"v{version} is newer than the item's v{entry['version']}")
            continue
        ledger_kind = entry["changelog"][version - 1].get("kind", entry["kind"])
        if item.findtext(q("kind")) != ledger_kind:
            problems.add(w, f"blyg:kind {item.findtext(q('kind'))!r}, but v{version} was {ledger_kind!r}")
        if item.findtext(q("created")) != doc.get("created"):
            problems.add(w, "blyg:created != item document's created")
        if item.findtext(q("item")) != f"{origin}items/{blyg_id}.json":
            problems.add(w, "blyg:item doesn't point at the item document")
        description = item.findtext("description") or ""
        # --minify trims the text node's edge whitespace; the HTML is the same.
        if description.strip() != doc.get("content_html", "").strip():
            problems.add(w, "description MUST carry the item's latest content_html (§7)")
        note = entry["changelog"][version - 1].get("note")
        title = item.findtext("title")
        if entry.get("withdrawn"):
            if title != "withdrawn" or description:
                problems.add(w, "a withdrawn item's entry has title `withdrawn` and empty description (§7)")
        elif note and title != note:
            problems.add(w, f"entry drops its changelog note {note!r} (§7)")
        if title is None and not description:
            problems.add(w, "RSS 2.0 items need a title or a description")
        try:
            pub = email.utils.parsedate_to_datetime(item.findtext("pubDate") or "")
        except (TypeError, ValueError):
            problems.add(w, "pubDate isn't RFC 822 (§7)")
            continue
        expected = datetime.datetime.fromisoformat(
            entry["changelog"][version - 1]["at"].replace("Z", "+00:00"))
        if pub != expected:
            problems.add(w, "pubDate != that version's changelog at")
        if last_pub is not None and pub > last_pub:
            problems.add(w, "entries aren't newest first (§7)")
        last_pub = pub

    for blyg_id, entry in ledger.items():
        if entry.get("withdrawn"):
            got = per_id.get(blyg_id, [])
            if len(got) > 1 or (got and got != [entry["version"]]):
                problems.add(where, f"withdrawn {blyg_id} MUST contribute exactly its withdrawal entry (§7)")


def validate(public_dir: Path, ledger_path: Path) -> Problems:
    problems = Problems()
    public_blyg = public_dir / "blyg"
    ledger = bs.load_ledger(ledger_path)
    manifest = check_manifest(public_blyg, problems)
    if manifest is None:
        return problems
    origin = manifest.get("site", "")

    docs = {}
    for blyg_id, entry in sorted(ledger.items()):
        doc = check_item(blyg_id, entry, origin, public_blyg, problems)
        if doc is not None:
            docs[blyg_id] = doc
    items_dir = public_blyg / "items"
    if items_dir.is_dir():
        for f in items_dir.glob("*.json"):
            if f.name != "index.json" and f.stem not in ledger:
                problems.add(f"items/{f.name}", "served, but not in the ledger")
    if docs and manifest.get("updated") != max(d.get("updated", "") for d in docs.values()):
        problems.add("blyg.json", "updated != newest item's updated")

    check_index(public_blyg, ledger, docs, problems)
    check_pins(public_blyg, ledger, origin, problems)
    check_feed(public_blyg, ledger, docs, manifest, origin, problems)
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--public-dir", default=str(bs.DEFAULT_PUBLIC_DIR))
    parser.add_argument("--ledger-path", default=str(bs.DEFAULT_LEDGER_PATH))
    args = parser.parse_args(argv)

    problems = validate(Path(args.public_dir), Path(args.ledger_path))
    for p in problems:
        print(f"error: {p}", file=sys.stderr)
    if problems:
        print(f"\n{len(problems)} blyg conformance problem(s).", file=sys.stderr)
        return 1
    print("blyg surface conforms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
