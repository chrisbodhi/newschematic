#!/usr/bin/env python3
"""Turn a GitHub issue into a new, unstamped content/blyg/*.md fragment.

Run by the publish-from-issue action (publish-from-issue/action.yml). The
issue body becomes the item body verbatim (bar line endings); the issue
title only names the file -- blyg items have no title field (§5), so it
never reaches the wire. Stamping (id, ledger entry) is left to
blyg_stamp.py, exactly as for a hand-written item.

An issue is marked for publishing by its label or, since not every
client can label an issue as it's filed (GitHub Mobile can't), by a
title prefix such as `blyg: `, which is dropped from the title.

Usage:
    blyg_from_issue.py check --event PATH [--authors LOGINS] [--label NAME]
                             [--prefix PREFIX]
        exit 0 if the `issues` event should publish, 1 (printing why)
        if not: the issue must be open, carry the label or the title
        prefix, and be filed by the repo owner or one of LOGINS
        (comma/space separated)
    blyg_from_issue.py title --event PATH [--prefix PREFIX]
        print the issue title without the prefix (for the commit and PR)
    blyg_from_issue.py write --event PATH [--prefix PREFIX]
        write the item from the event's issue, print its path
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


def parse_logins(value: str) -> set[str]:
    return {login.casefold() for login in re.split(r"[\s,]+", value) if login}


def strip_prefix(title: str, prefix: str) -> str | None:
    """`title` without a leading `prefix` (case-insensitive, surrounding
    whitespace ignored), or None if it doesn't start with one. An empty
    prefix never matches."""
    prefix = prefix.strip()
    title = title.strip()
    if not prefix or not title.casefold().startswith(prefix.casefold()):
        return None
    return title[len(prefix):].strip()


def publish_title(title: str, prefix: str) -> str:
    stripped = strip_prefix(title, prefix)
    return title.strip() if stripped is None else stripped


def skip_reason(event: dict, *, authors: str, label: str,
                prefix: str = "") -> str | None:
    """Why this `issues` event shouldn't publish, or None if it should.
    Logins, label names and the title prefix compare case-insensitively,
    as GitHub treats logins and labels."""
    issue = event["issue"]
    action = event.get("action")
    label = label.casefold()
    labeled = label in {lab["name"].casefold() for lab in issue.get("labels", [])}
    if action == "labeled":
        if event["label"]["name"].casefold() != label:
            return f"added label {event['label']['name']!r} isn't {label!r}"
    elif action == "opened":
        if not labeled and strip_prefix(issue["title"], prefix) is None:
            how = f" or titled {prefix.strip()!r}" if prefix.strip() else ""
            return f"issue #{issue['number']} isn't labeled {label!r}{how}"
    else:
        return f"`{action}` events don't publish"
    if issue.get("state") != "open":
        return f"issue #{issue['number']} is {issue.get('state')}"
    if "pull_request" in issue:
        return f"#{issue['number']} is a pull request"
    author = issue["user"]["login"]
    allowed = parse_logins(authors) | {event["repository"]["owner"]["login"].casefold()}
    if author.casefold() not in allowed:
        return f"{author} isn't the repo owner or a listed author"
    return None


def cmd_check(args: argparse.Namespace, event: dict) -> int:
    reason = skip_reason(event, authors=args.authors, label=args.label,
                         prefix=args.prefix)
    if reason is not None:
        print(f"skip: {reason}")
        return 1
    return 0


def cmd_write(args: argparse.Namespace, event: dict) -> int:
    issue = event["issue"]
    try:
        path = create_item(Path(args.content_dir),
                           title=publish_title(issue["title"], args.prefix),
                           body=issue.get("body"), number=issue["number"],
                           now=datetime.datetime.now(datetime.timezone.utc))
    except bs.BlygStampError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(path.relative_to(bs.REPO_ROOT) if path.is_relative_to(bs.REPO_ROOT) else path)
    return 0


def cmd_title(args: argparse.Namespace, event: dict) -> int:
    issue = event["issue"]
    print(publish_title(issue["title"], args.prefix) or f"blyg fragment from #{issue['number']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="should this issues event publish?")
    check.add_argument("--authors", default="",
                       help="logins allowed besides the repo owner (comma/space separated)")
    check.add_argument("--label", default="blyg")
    write = sub.add_parser("write", help="write the item from the event's issue")
    write.add_argument("--content-dir", default=str(bs.DEFAULT_CONTENT_DIR))
    title = sub.add_parser("title", help="print the issue title without the prefix")
    for p in (check, title, write):
        p.add_argument("--event", required=True, help="GitHub event payload (GITHUB_EVENT_PATH)")
        p.add_argument("--prefix", default="",
                       help="title prefix that marks an issue for publishing, e.g. 'blyg:'")
    args = parser.parse_args(argv)

    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    return {"check": cmd_check, "title": cmd_title, "write": cmd_write}[args.command](args, event)


if __name__ == "__main__":
    sys.exit(main())
