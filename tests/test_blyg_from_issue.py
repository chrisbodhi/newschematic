import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import blyg_from_issue as bfi  # noqa: E402
import blyg_stamp as bs  # noqa: E402

NOW = datetime.datetime(2026, 9, 27, 14, 5, 9, 123456, tzinfo=datetime.timezone.utc)


class SlugifyTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bfi.slugify("Hello, World!"), "hello-world")

    def test_folds_accents_and_drops_the_rest(self):
        self.assertEqual(bfi.slugify("Café über 🚀 naïve"), "cafe-uber-naive")

    def test_all_symbols_is_empty(self):
        self.assertEqual(bfi.slugify("🚀🚀 !!"), "")

    def test_cuts_long_titles_at_a_word_boundary(self):
        slug = bfi.slugify("word " * 30)
        self.assertLessEqual(len(slug), bfi.SLUG_MAX)
        self.assertFalse(slug.endswith("-"))
        self.assertTrue(all(part == "word" for part in slug.split("-")))


class CreateItemTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.content_dir = self.root / "content" / "blyg"
        self.ledger_path = self.root / "data" / "blyg" / "ledger.json"

    def tearDown(self):
        self.tmp.cleanup()

    def create(self, title="A thought", body="Some *words*.", number=7):
        return bfi.create_item(self.content_dir, title=title, body=body,
                               number=number, now=NOW)

    def test_writes_an_unstamped_fragment(self):
        path = self.create()
        self.assertEqual(path.name, "2026-09-27-a-thought.md")
        self.assertEqual(path.read_bytes(),
                         b'+++\ndate = "2026-09-27T14:05:09Z"\nblyg_kind = "fragment"\n'
                         b'+++\nSome *words*.\n')

    def test_title_never_reaches_the_item(self):
        text = self.create(title="Secret headline").read_text(encoding="utf-8")
        self.assertNotIn("Secret headline", text)

    def test_crlf_body_is_normalized_to_lf(self):
        path = self.create(body="one\r\ntwo\r\n\r\nthree\r\n\r\n")
        _, body = bs.split_front_matter(path.read_text(encoding="utf-8"))
        self.assertEqual(body, "one\ntwo\n\nthree\n")
        self.assertNotIn(b"\r", path.read_bytes())

    def test_empty_body_is_refused(self):
        for body in (None, "", "  \r\n "):
            with self.assertRaises(bs.BlygStampError):
                self.create(body=body)
        self.assertFalse(self.content_dir.exists() and any(self.content_dir.iterdir()))

    def test_filename_collisions_get_a_suffix(self):
        names = [self.create().name for _ in range(3)]
        self.assertEqual(names, ["2026-09-27-a-thought.md", "2026-09-27-a-thought-2.md",
                                 "2026-09-27-a-thought-3.md"])

    def test_unsluggable_title_falls_back_to_issue_number(self):
        self.assertEqual(self.create(title="🚀", number=42).name, "2026-09-27-issue-42.md")

    def test_stamps_as_a_new_v1_fragment(self):
        path = self.create()
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True,
                             now=NOW + datetime.timedelta(seconds=5))
        self.assertEqual([p.kind for p in plans], ["new"])
        entry = json.loads(self.ledger_path.read_text())[plans[0].blyg_id]
        self.assertEqual(entry["kind"], "fragment")
        self.assertEqual(entry["version"], 1)
        self.assertEqual(entry["created"], "2026-09-27T14:05:09Z")
        self.assertEqual(entry["changelog"][0]["note"], None)
        self.assertIn(f'blyg_id = "{plans[0].blyg_id}"', path.read_text(encoding="utf-8"))
        self.assertEqual(entry["last_hash"], bs.content_hash("Some *words*.\n"))

    def test_main_reads_the_event_payload(self):
        event = self.root / "event.json"
        event.write_text(json.dumps({"issue": {"number": 3, "title": "From the event",
                                                "body": "Body\r\n"}}))
        self.assertEqual(bfi.main(["--event", str(event),
                                   "--content-dir", str(self.content_dir)]), 0)
        [path] = self.content_dir.iterdir()
        self.assertTrue(path.name.endswith("-from-the-event.md"))

    def test_main_reports_an_empty_body(self):
        event = self.root / "event.json"
        event.write_text(json.dumps({"issue": {"number": 3, "title": "t", "body": None}}))
        self.assertEqual(bfi.main(["--event", str(event),
                                   "--content-dir", str(self.content_dir)]), 2)


if __name__ == "__main__":
    unittest.main()
