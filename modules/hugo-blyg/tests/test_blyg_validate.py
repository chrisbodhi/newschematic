import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import blyg_stamp as bs  # noqa: E402
import blyg_validate as bv  # noqa: E402

ORIGIN = "https://example.org/blyg/"
ID = "7c9wk2mhq0v3xj8tn5rzfd41bg"


class ContentHTMLTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.public_blyg = Path(self.tmp.name)
        (self.public_blyg / "media").mkdir()
        (self.public_blyg / "media" / "a.png").write_bytes(b"png")

    def tearDown(self):
        self.tmp.cleanup()

    def problems(self, content_html):
        problems = bv.Problems()
        bv.check_content_html("x", content_html, ORIGIN, self.public_blyg, problems)
        return problems

    def test_self_contained_html_passes(self):
        self.assertEqual(self.problems(
            f'<p><a href="https://other.example/">x</a> <a href="#fn:1">1</a>'
            f'<img src="{ORIGIN}media/a.png" srcset="{ORIGIN}media/a.png 2x">'
            f'<a href="mailto:a@b.c">m</a> <img src="data:image/png;base64,AA=="></p>'), [])

    def test_page_relative_link_fails(self):
        self.assertEqual(len(self.problems('<a href="other/page">x</a>')), 1)

    def test_root_relative_link_fails(self):
        self.assertEqual(len(self.problems('<a href="/about/">x</a>')), 1)

    def test_relative_srcset_candidate_fails(self):
        self.assertEqual(len(self.problems(
            f'<img src="{ORIGIN}media/a.png" srcset="{ORIGIN}media/a.png 1x, /blyg/media/a.png 2x">')), 1)

    def test_origin_image_outside_media_fails(self):
        self.assertEqual(len(self.problems('<img src="https://example.org/img/me.jpg">')), 1)

    def test_media_missing_from_build_fails(self):
        self.assertEqual(len(self.problems(f'<img src="{ORIGIN}media/nope.png">')), 1)

    def test_origin_script_and_stylesheet_fail(self):
        self.assertEqual(len(self.problems(
            '<script src="https://example.org/js/x.js"></script>'
            '<link rel="stylesheet" href="https://example.org/s.css">')), 2)

    def test_relative_css_url_fails(self):
        self.assertEqual(len(self.problems('<div style="background:url(/x.png)"></div>')), 1)


def item_doc(blyg_id, *, kind="thread", version=1, withdrawn=False, body="Body.\n",
             html="<p>Body.</p>", changelog=None):
    changelog = changelog or [{"version": v, "at": f"2026-01-0{v}T00:00:00Z", "note": None}
                              for v in range(1, version + 1)]
    md, h = ("", "") if withdrawn else (body, html)
    doc = {
        "blyg": "0.2", "id": blyg_id, "kind": "withdrawn" if withdrawn else kind,
        "origin": ORIGIN, "created": changelog[0]["at"], "updated": changelog[-1]["at"],
        "version": version, "content_md": md, "content_html": h,
        "content_hash": bs.content_hash(md), "media": [], "changelog": changelog,
    }
    if kind == "thread":
        doc["transclusions"] = []
    return doc


class SurfaceTests(unittest.TestCase):
    """A hand-built surface, validated end to end, then broken one way at a time."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.public = root / "public"
        self.blyg = self.public / "blyg"
        (self.blyg / "items").mkdir(parents=True)
        self.ledger_path = root / "ledger.json"
        self.docs = {ID: item_doc(ID)}
        self.ledger = {ID: {"path": "content/blyg/p.md", "created": "2026-01-01T00:00:00Z",
                            "version": 1, "kind": "thread", "withdrawn": False,
                            "last_hash": bs.content_hash("Body.\n"),
                            "changelog": [{"version": 1, "at": "2026-01-01T00:00:00Z",
                                           "note": None, "kind": "thread"}]}}
        self.feed_items = None

    def tearDown(self):
        self.tmp.cleanup()

    def write(self):
        self.ledger_path.write_text(json.dumps(self.ledger), encoding="utf-8")
        updated = max(d["updated"] for d in self.docs.values())
        (self.blyg / "blyg.json").write_text(json.dumps({
            "blyg": "0.2", "level": 1, "generator": "t", "site": ORIGIN, "title": "t",
            "feed": "feed.xml", "items": "items/index.json", "updated": updated}), encoding="utf-8")
        rows = sorted(({k: d[k] for k in ("id", "kind", "created", "updated", "version")}
                       for d in self.docs.values()), key=lambda r: r["updated"], reverse=True)
        (self.blyg / "items" / "index.json").write_text(
            json.dumps({"updated": updated, "items": rows}), encoding="utf-8")
        for i, d in self.docs.items():
            (self.blyg / "items" / f"{i}.json").write_text(json.dumps(d), encoding="utf-8")
        items = self.feed_items
        if items is None:
            items = []
            for i, d in self.docs.items():
                for c in reversed(self.ledger[i]["changelog"]):
                    items.append(self.feed_item(i, c["version"], d, title=c["note"]))
        (self.blyg / "feed.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" '
            'xmlns:blyg="https://blygger.org/ns/0.1"><channel><title>t</title>'
            f'<link>{ORIGIN}</link><description>d</description>'
            f'<blyg:manifest>{ORIGIN}blyg.json</blyg:manifest>{"".join(items)}'
            '</channel></rss>', encoding="utf-8")

    def feed_item(self, blyg_id, version, doc, *, title=None, description=None, kind=None):
        at = self.ledger[blyg_id]["changelog"][version - 1]["at"]
        pub = datetime.datetime.fromisoformat(at.replace("Z", "+00:00")).strftime(
            "%a, %d %b %Y %H:%M:%S GMT")
        kind = kind or self.ledger[blyg_id]["changelog"][version - 1]["kind"]
        desc = doc["content_html"] if description is None else description
        return (f'<item><guid isPermaLink="false">blyg:{blyg_id}:v{version}</guid>'
                + (f"<title>{escape(title)}</title>" if title else "")
                + f"<description>{escape(desc)}</description><pubDate>{pub}</pubDate>"
                f"<blyg:id>{blyg_id}</blyg:id><blyg:kind>{kind}</blyg:kind>"
                f"<blyg:version>{version}</blyg:version><blyg:created>{doc['created']}</blyg:created>"
                f"<blyg:item>{ORIGIN}items/{blyg_id}.json</blyg:item></item>")

    def problems(self):
        self.write()
        return bv.validate(self.public, self.ledger_path)

    def test_valid_surface_passes(self):
        self.assertEqual(self.problems(), [])

    def test_missing_item_document_fails(self):
        self.write()
        (self.blyg / "items" / f"{ID}.json").unlink()
        problems = bv.validate(self.public, self.ledger_path)
        self.assertTrue(any("200 forever" in p for p in problems), problems)

    def test_ledger_private_changelog_keys_must_not_leak(self):
        self.docs[ID]["changelog"][0]["kind"] = "thread"
        self.assertTrue(any("ledger-private" in p for p in self.problems()))

    def test_fragment_with_transclusions_fails(self):
        self.ledger[ID]["kind"] = "fragment"
        self.ledger[ID]["changelog"][0]["kind"] = "fragment"
        self.docs[ID]["kind"] = "fragment"
        self.assertTrue(any("omit transclusions" in p for p in self.problems()))

    def test_unresolved_directive_fails(self):
        body = f"![[{ID}]]\n"
        self.docs[ID] = item_doc(ID, body=body, html=f"<p>![[{ID}]]</p>")
        self.ledger[ID]["last_hash"] = bs.content_hash(body)
        self.assertTrue(any("directive" in p for p in self.problems()))

    def test_feed_must_keep_the_note(self):
        self.ledger[ID]["changelog"][0]["note"] = "first"
        self.docs[ID]["changelog"][0]["note"] = "first"
        self.feed_items = [self.feed_item(ID, 1, self.docs[ID])]
        self.assertTrue(any("changelog note" in p for p in self.problems()))

    def test_feed_description_must_be_latest_content(self):
        self.feed_items = [self.feed_item(ID, 1, self.docs[ID], description="<p>old</p>")]
        self.assertTrue(any("latest content_html" in p for p in self.problems()))

    def test_withdrawn_item_contributes_exactly_its_endcap(self):
        self.ledger[ID].update(version=2, withdrawn=True, last_hash=bs.EMPTY_CONTENT_HASH)
        self.ledger[ID]["changelog"].append(
            {"version": 2, "at": "2026-01-02T00:00:00Z", "note": "withdrawn", "kind": "withdrawn"})
        self.docs[ID] = item_doc(ID, version=2, withdrawn=True)
        self.docs[ID]["changelog"][1]["note"] = "withdrawn"
        endcap = self.feed_item(ID, 2, self.docs[ID], title="withdrawn", description="")
        self.feed_items = [endcap]
        self.assertEqual(self.problems(), [])
        self.feed_items = [endcap, self.feed_item(ID, 1, self.docs[ID], description="",
                                                  title="x")]
        self.assertTrue(any("exactly its withdrawal entry" in p for p in self.problems()))

    def test_past_event_kind_must_match_that_version(self):
        self.feed_items = [self.feed_item(ID, 1, self.docs[ID], kind="fragment")]
        self.assertTrue(any("blyg:kind" in p for p in self.problems()))

    def test_recorded_pin_must_be_served(self):
        self.ledger[ID]["changelog"][0]["pinned"] = True
        self.docs[ID]["changelog"][0]["pinned"] = True
        self.assertTrue(any("pin" in p for p in self.problems()))


if __name__ == "__main__":
    unittest.main()
