import contextlib
import datetime
import io
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
        self.assertEqual(bfi.main(["write", "--event", str(event),
                                   "--content-dir", str(self.content_dir)]), 0)
        [path] = self.content_dir.iterdir()
        self.assertTrue(path.name.endswith("-from-the-event.md"))

    def test_main_reports_an_empty_body(self):
        event = self.root / "event.json"
        event.write_text(json.dumps({"issue": {"number": 3, "title": "t", "body": None}}))
        self.assertEqual(bfi.main(["write", "--event", str(event),
                                   "--content-dir", str(self.content_dir)]), 2)



def event(action="opened", *, author="owner", labels=("blyg",), state="open",
          added=None, owner="owner", title="A thought"):
    ev = {"action": action,
          "issue": {"number": 5, "title": title, "state": state, "user": {"login": author},
                    "labels": [{"name": name} for name in labels]},
          "repository": {"owner": {"login": owner}}}
    if added is not None:
        ev["label"] = {"name": added}
    return ev


class SkipReasonTests(unittest.TestCase):
    def reason(self, ev, authors="", label="blyg", prefix=""):
        return bfi.skip_reason(ev, authors=authors, label=label, prefix=prefix)

    def test_owner_opening_a_labeled_issue_publishes(self):
        self.assertIsNone(self.reason(event()))

    def test_owner_adding_the_label_publishes(self):
        self.assertIsNone(self.reason(event("labeled", added="blyg")))

    def test_adding_some_other_label_does_not(self):
        self.assertIsNotNone(self.reason(event("labeled", labels=("blyg", "bug"), added="bug")))

    def test_unlabeled_issue_does_not(self):
        self.assertIsNotNone(self.reason(event(labels=("bug",))))

    def test_other_actions_do_not(self):
        for action in ("edited", "closed", "reopened", "unlabeled"):
            self.assertIsNotNone(self.reason(event(action)), action)

    def test_closed_issue_does_not(self):
        self.assertIsNotNone(self.reason(event("labeled", added="blyg", state="closed")))

    def test_strangers_do_not(self):
        self.assertIsNotNone(self.reason(event(author="someone")))

    def test_listed_authors_do_in_any_separator_or_case(self):
        for authors in ("someone", "a, Someone", "a\nsomeone\n", "a someone"):
            self.assertIsNone(self.reason(event(author="SomeOne"), authors=authors), authors)

    def test_the_owner_stays_allowed_alongside_listed_authors(self):
        self.assertIsNone(self.reason(event(), authors="someone"))

    def test_label_is_configurable_and_case_insensitive(self):
        ev = event("labeled", labels=("Microblog",), added="Microblog")
        self.assertIsNone(self.reason(ev, label="microblog"))
        self.assertIsNotNone(self.reason(ev))

    def test_prefixed_title_publishes_without_the_label(self):
        for title in ("blyg: A thought", "BLYG:A thought", "  Blyg:  A thought "):
            self.assertIsNone(self.reason(event(labels=(), title=title), prefix="blyg:"), title)

    def test_prefix_only_counts_at_the_start(self):
        self.assertIsNotNone(self.reason(event(labels=(), title="About blyg: things"),
                                         prefix="blyg:"))

    def test_no_prefix_configured_means_label_only(self):
        self.assertIsNotNone(self.reason(event(labels=(), title="blyg: A thought")))

    def test_prefixed_title_still_needs_an_allowed_author(self):
        self.assertIsNotNone(self.reason(event(labels=(), title="blyg: hi", author="someone"),
                                         prefix="blyg:"))

    def test_prefixed_title_still_needs_an_open_issue(self):
        self.assertIsNotNone(self.reason(event(labels=(), title="blyg: hi", state="closed"),
                                         prefix="blyg:"))

    def test_check_command_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "event.json"
            path.write_text(json.dumps(event()))
            self.assertEqual(bfi.main(["check", "--event", str(path)]), 0)
            path.write_text(json.dumps(event(author="someone")))
            self.assertEqual(bfi.main(["check", "--event", str(path)]), 1)
            self.assertEqual(bfi.main(["check", "--event", str(path),
                                       "--authors", "someone"]), 0)



class TitleTests(unittest.TestCase):
    def test_strip_prefix(self):
        self.assertEqual(bfi.strip_prefix("blyg: Pray for me", "blyg:"), "Pray for me")
        self.assertEqual(bfi.strip_prefix(" BLYG:Pray ", "blyg:"), "Pray")
        self.assertIsNone(bfi.strip_prefix("Pray for me", "blyg:"))
        self.assertIsNone(bfi.strip_prefix("blyg: Pray", ""))

    def test_publish_title_falls_back_to_the_whole_title(self):
        self.assertEqual(bfi.publish_title("Pray for me", "blyg:"), "Pray for me")
        self.assertEqual(bfi.publish_title("blyg: Pray for me", "blyg:"), "Pray for me")

    def test_write_and_title_commands_drop_the_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "event.json"
            ev = event(labels=(), title="blyg: Pray for me")
            ev["issue"]["body"] = "Body"
            path.write_text(json.dumps(ev))
            content_dir = Path(tmp) / "content" / "blyg"
            self.assertEqual(bfi.main(["write", "--event", str(path), "--prefix", "blyg:",
                                       "--content-dir", str(content_dir)]), 0)
            [item] = content_dir.iterdir()
            self.assertTrue(item.name.endswith("-pray-for-me.md"), item.name)


    def test_title_command_never_prints_an_empty_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "event.json"
            path.write_text(json.dumps(event(title="blyg:")))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(bfi.main(["title", "--event", str(path), "--prefix", "blyg:"]), 0)
            self.assertEqual(out.getvalue(), "blyg fragment from #5\n")


if __name__ == "__main__":
    unittest.main()
