#!/usr/bin/env python3
"""Turn a GitHub issue into a new, unstamped content/blyg/*.md fragment.

Run by .github/workflows/blyg-issue.yml. The issue body becomes the item
body verbatim (bar line endings); the issue title only names the file --
blyg items have no title field (§5), so it never reaches the wire.
Stamping (id, ledger entry) is left to scripts/blyg_stamp.py, exactly as
for a hand-written item.

Usage:
    blyg_from_issue.py --event PATH   read title/body/number from a GitHub
                                       `issues` event payload, write the
                                       item, print its path
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import blyg_stamp as bs  # noqa: E402

SLUG_MAX = 60


def slugify(title: str) -> str:
    """ASCII, lowercase, hyphen-separated, cut at a word boundary."""
    ascii_title = (unicodedata.normalize("NFKD", title)
                   .encode("ascii", "ignore").decode("ascii"))
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
    if len(slug) > SLUG_MAX:
        cut = slug[:SLUG_MAX + 1].rfind("-")
        slug = slug[:cut if cut > 0 else SLUG_MAX].strip("-")
    return slug


def normalize_body(body: str) -> str:
    """Issues edited in the web UI arrive with CRLF line endings; the
    content hash covers content_md's exact bytes (§5.1), so settle on LF
    before stamping, matching the rest of the repo (docs/blyg/hazards.md)."""
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    return body.rstrip("\n") + "\n"


def item_path(content_dir: Path, date: datetime.datetime, title: str,
              number: int) -> Path:
    stem = f"{date:%Y-%m-%d}-{slugify(title) or f'issue-{number}'}"
    path = content_dir / f"{stem}.md"
    n = 2
    while path.exists():
        path = content_dir / f"{stem}-{n}.md"
        n += 1
    return path


def create_item(content_dir: Path, *, title: str, body: str | None, number: int,
                now: datetime.datetime) -> Path:
    if body is None or not body.strip():
        raise bs.BlygStampError(f"issue #{number} has an empty body -- nothing to publish")
    path = item_path(content_dir, now, title, number)
    front_matter = (f'date = "{bs.iso8601_utc(now)}"\n'
                    f'blyg_kind = "fragment"\n')
    content_dir.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(f"+++\n{front_matter}+++\n{normalize_body(body)}")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", required=True, help="GitHub event payload (GITHUB_EVENT_PATH)")
    parser.add_argument("--content-dir", default=str(bs.DEFAULT_CONTENT_DIR))
    args = parser.parse_args(argv)

    issue = json.loads(Path(args.event).read_text(encoding="utf-8"))["issue"]
    try:
        path = create_item(Path(args.content_dir), title=issue["title"],
                           body=issue.get("body"), number=issue["number"],
                           now=datetime.datetime.now(datetime.timezone.utc))
    except bs.BlygStampError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(path.relative_to(bs.REPO_ROOT) if path.is_relative_to(bs.REPO_ROOT) else path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
