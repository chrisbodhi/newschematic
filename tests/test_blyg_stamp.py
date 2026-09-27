import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import blyg_stamp as bs  # noqa: E402


def write_post(content_dir: Path, name: str, front_matter: str, body: str) -> Path:
    path = content_dir / name
    path.write_text(f"+++\n{front_matter}+++\n{body}", encoding="utf-8")
    return path


class TmpRepoTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.content_dir = Path(self.tmp.name) / "content" / "blyg"
        self.content_dir.mkdir(parents=True)
        self.ledger_path = Path(self.tmp.name) / "data" / "blyg" / "ledger.json"

    def tearDown(self):
        self.tmp.cleanup()


class IdFormatTests(unittest.TestCase):
    def test_generated_id_is_26_crockford_chars(self):
        for _ in range(200):
            blyg_id = bs.generate_blyg_id()
            self.assertEqual(len(blyg_id), 26)
            self.assertTrue(bs.is_valid_blyg_id(blyg_id), blyg_id)
            for c in blyg_id:
                self.assertIn(c, bs.CROCKFORD_ALPHABET)

    def test_ids_do_not_collide_in_practice(self):
        ids = {bs.generate_blyg_id() for _ in range(1000)}
        self.assertEqual(len(ids), 1000)

    def test_rejects_wrong_length(self):
        self.assertFalse(bs.is_valid_blyg_id("abc"))
        self.assertFalse(bs.is_valid_blyg_id("a" * 25))
        self.assertFalse(bs.is_valid_blyg_id("a" * 27))

    def test_rejects_excluded_letters(self):
        # Crockford excludes i, l, o, u.
        for bad in "ilou":
            candidate = bad * 26
            self.assertFalse(bs.is_valid_blyg_id(candidate))

    def test_first_char_never_uses_top_two_bits(self):
        # 26 chars * 5 bits = 130 bits of capacity for 128 bits of entropy,
        # so the first char can only ever be one of the first 8 alphabet
        # symbols (0-7), never 8-31.
        first_chars = {bs.generate_blyg_id()[0] for _ in range(500)}
        allowed = set(bs.CROCKFORD_ALPHABET[:8])
        self.assertTrue(first_chars.issubset(allowed), first_chars - allowed)


class FrontMatterSplitTests(unittest.TestCase):
    def test_byte_exact_with_leading_and_trailing_blank_lines(self):
        text = (
            '+++\ntitle = "Raw Test"\ndate = "2020-01-01T00:00:00Z"\n'
            'draft = false\n+++\n'
            '\n\nLine one.\n\nLine two with trailing spaces.   \n\n\n'
        )
        fm, body = bs.split_front_matter(text)
        self.assertEqual(body, "\n\nLine one.\n\nLine two with trailing spaces.   \n\n\n")

    def test_byte_exact_no_leading_blank_no_trailing_newline(self):
        text = (
            '+++\ntitle = "Raw Test 2"\ndraft = false\n+++\n'
            'No leading blank line, and no trailing newline at all.'
        )
        fm, body = bs.split_front_matter(text)
        self.assertEqual(body, "No leading blank line, and no trailing newline at all.")

    def test_missing_delimiters_raise(self):
        with self.assertRaises(bs.BlygStampError):
            bs.split_front_matter("no front matter here")


class NewItemTests(TmpRepoTestCase):
    def test_new_item_gets_id_and_v1(self):
        write_post(
            self.content_dir, "first.md",
            'title = "First"\ndate = "2024-03-01T12:00:00Z"\ndraft = false\n',
            "Hello, blyg.\n",
        )
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        self.assertEqual(len(plans), 1)
        plan = plans[0]
        self.assertEqual(plan.kind, "new")
        self.assertTrue(bs.is_valid_blyg_id(plan.blyg_id))

        stamped = (self.content_dir / "first.md").read_text(encoding="utf-8")
        self.assertIn(f'blyg_id = "{plan.blyg_id}"', stamped)

        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        entry = ledger[plan.blyg_id]
        self.assertEqual(entry["version"], 1)
        self.assertEqual(entry["created"], "2024-03-01T12:00:00Z")
        self.assertEqual(entry["changelog"], [{"version": 1, "at": "2024-03-01T12:00:00Z", "note": None, "kind": "thread"}])
        self.assertEqual(entry["kind"], "thread")
        self.assertFalse(entry["withdrawn"])

    def test_naive_date_backfills_as_utc(self):
        write_post(
            self.content_dir, "naive.md",
            'title = "Naive Date"\ndate = "2013-11-12T05:04:39"\ndraft = false\n',
            "Old post, no offset.\n",
        )
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        entry = ledger[plans[0].blyg_id]
        self.assertEqual(entry["created"], "2013-11-12T05:04:39Z")

    def test_never_re_serializes_front_matter(self):
        original_fm = 'title = "Preserve Me"\ndate = "2024-01-01T00:00:00Z"\ndraft = false\ntags = ["a", "b",]\n'
        write_post(self.content_dir, "preserve.md", original_fm, "Body text.\n")
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        stamped = (self.content_dir / "preserve.md").read_text(encoding="utf-8")
        # Every original front-matter line survives untouched, in order,
        # with exactly one new blyg_id line added before the closing +++.
        expected_lines = ["+++"] + original_fm.rstrip("\n").split("\n") + [
            f'blyg_id = "{plans[0].blyg_id}"', "+++", "Body text.", ""
        ]
        self.assertEqual(stamped.split("\n"), expected_lines)


class DraftTests(TmpRepoTestCase):
    def test_draft_is_skipped_entirely(self):
        write_post(
            self.content_dir, "draft.md",
            'title = "Draft"\ndate = "2024-01-01T00:00:00Z"\ndraft = true\n',
            "Not published yet.\n",
        )
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        self.assertEqual(plans[0].kind, "draft-skip")
        self.assertIsNone(plans[0].blyg_id)

        stamped = (self.content_dir / "draft.md").read_text(encoding="utf-8")
        self.assertNotIn("blyg_id", stamped)
        self.assertEqual(json.loads(self.ledger_path.read_text(encoding="utf-8")) if self.ledger_path.exists() else {}, {})

    def test_index_md_is_never_treated_as_an_item(self):
        (self.content_dir / "_index.md").write_text("+++\ntitle = \"blyg\"\n+++\n", encoding="utf-8")
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        self.assertEqual(plans, [])


class IdempotencyAndBumpTests(TmpRepoTestCase):
    def _stamp_once(self, name="post.md", body="Original body.\n"):
        write_post(
            self.content_dir, name,
            'title = "Post"\ndate = "2024-01-01T00:00:00Z"\ndraft = false\n',
            body,
        )
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        return plans[0].blyg_id

    def test_second_run_with_no_change_is_a_noop(self):
        self._stamp_once()
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        self.assertEqual(plans[0].kind, "noop")
        ledger_before = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        plans_again = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        ledger_after = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(plans_again[0].kind, "noop")
        self.assertEqual(ledger_before, ledger_after)

    def test_repeated_stamp_is_fully_idempotent(self):
        blyg_id = self._stamp_once()
        for _ in range(5):
            bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(ledger[blyg_id]["version"], 1)
        self.assertEqual(len(ledger[blyg_id]["changelog"]), 1)

    def test_body_change_bumps_version(self):
        blyg_id = self._stamp_once(body="Original body.\n")
        path = self.content_dir / "post.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("Original body.", "Edited body."), encoding="utf-8")

        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        self.assertEqual(plans[0].kind, "bump")

        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        entry = ledger[blyg_id]
        self.assertEqual(entry["version"], 2)
        self.assertEqual(len(entry["changelog"]), 2)
        self.assertEqual(entry["changelog"][1]["version"], 2)
        self.assertIsNone(entry["changelog"][1]["note"])
        self.assertEqual(entry["last_hash"], bs.content_hash("Edited body.\n"))

    def test_front_matter_only_change_does_not_bump(self):
        # content_hash covers content_md (body) only, per §5.1 -- a
        # metadata-only edit (e.g. a tag) must not look like a new version.
        blyg_id = self._stamp_once()
        path = self.content_dir / "post.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace('title = "Post"', 'title = "Post (renamed)"')
        path.write_text(text, encoding="utf-8")

        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        self.assertEqual(plans[0].kind, "noop")

    def test_missing_ledger_entry_for_known_id_is_a_hard_error(self):
        blyg_id = self._stamp_once()
        self.ledger_path.write_text("{}", encoding="utf-8")
        with self.assertRaises(bs.BlygStampError):
            bs.run_stamp(self.content_dir, self.ledger_path, write=True)


class DryRunTests(TmpRepoTestCase):
    def test_dry_run_writes_nothing(self):
        write_post(
            self.content_dir, "post.md",
            'title = "Post"\ndate = "2024-01-01T00:00:00Z"\ndraft = false\n',
            "Body.\n",
        )
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=False)
        self.assertEqual(plans[0].kind, "new")
        self.assertFalse(self.ledger_path.exists())
        stamped = (self.content_dir / "post.md").read_text(encoding="utf-8")
        self.assertNotIn("blyg_id", stamped)

    def test_dry_run_never_generates_an_id(self):
        # An id is 128 random bits from a cryptographically strong source
        # (§5.1) -- a dry run must not generate one just to display it,
        # since a subsequent real run would never produce that same id
        # and showing one implies a stability that doesn't exist.
        write_post(
            self.content_dir, "post.md",
            'title = "Post"\ndate = "2024-01-01T00:00:00Z"\ndraft = false\n',
            "Body.\n",
        )
        plan = bs.run_stamp(self.content_dir, self.ledger_path, write=False)[0]
        self.assertIsNone(plan.blyg_id)
        self.assertIn("(pending)", bs.format_plan(plan))

    def test_dry_run_and_real_run_messages_differ(self):
        write_post(
            self.content_dir, "post.md",
            'title = "Post"\ndate = "2024-01-01T00:00:00Z"\ndraft = false\n',
            "Body.\n",
        )
        dry_plan = bs.run_stamp(self.content_dir, self.ledger_path, write=False)[0]
        real_plan = bs.run_stamp(self.content_dir, self.ledger_path, write=True)[0]
        self.assertNotEqual(bs.format_plan(dry_plan), bs.format_plan(real_plan))
        self.assertTrue(bs.is_valid_blyg_id(real_plan.blyg_id))
        self.assertIsNone(dry_plan.blyg_id)

    def test_dry_run_bump_and_withdraw_messages_say_would(self):
        write_post(
            self.content_dir, "post.md",
            'title = "Post"\ndate = "2024-01-01T00:00:00Z"\ndraft = false\n',
            "Body.\n",
        )
        bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        path = self.content_dir / "post.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("Body.", "Edited body."),
            encoding="utf-8",
        )
        plan = bs.run_stamp(self.content_dir, self.ledger_path, write=False)[0]
        self.assertEqual(plan.kind, "bump")
        self.assertIn("would bump", plan.detail)
        self.assertIsNone(plan.ledger_entry)

    def test_check_mode_reports_pending_changes(self):
        write_post(
            self.content_dir, "post.md",
            'title = "Post"\ndate = "2024-01-01T00:00:00Z"\ndraft = false\n',
            "Body.\n",
        )
        rc = bs.main([
            "--content-dir", str(self.content_dir),
            "--ledger-path", str(self.ledger_path),
            "--check",
        ])
        self.assertEqual(rc, 1)
        self.assertFalse(self.ledger_path.exists())


class WithdrawalTests(TmpRepoTestCase):
    def _stamp_once(self):
        write_post(
            self.content_dir, "post.md",
            'title = "Post"\ndate = "2024-01-01T00:00:00Z"\ndraft = false\n',
            "Body.\n",
        )
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        return plans[0].blyg_id

    def _mark_withdrawn(self):
        path = self.content_dir / "post.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("draft = false\n", "draft = false\nblyg_withdrawn = true\n")
        path.write_text(text, encoding="utf-8")

    def test_withdrawal_is_exactly_one_endcap_bump(self):
        blyg_id = self._stamp_once()
        self._mark_withdrawn()

        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        self.assertEqual(plans[0].kind, "withdraw")

        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        entry = ledger[blyg_id]
        self.assertEqual(entry["version"], 2)
        self.assertTrue(entry["withdrawn"])
        self.assertEqual(entry["last_hash"], bs.EMPTY_CONTENT_HASH)
        self.assertEqual(len(entry["changelog"]), 2)
        self.assertEqual(entry["changelog"][1]["note"], "withdrawn")

    def test_withdrawal_does_not_repeat_on_subsequent_runs(self):
        blyg_id = self._stamp_once()
        self._mark_withdrawn()
        bs.run_stamp(self.content_dir, self.ledger_path, write=True)

        # Even if the underlying body keeps changing while withdrawn, no
        # further version bump should happen -- there's nothing to serve.
        path = self.content_dir / "post.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("Body.", "Body, edited while withdrawn."),
            encoding="utf-8",
        )
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        self.assertEqual(plans[0].kind, "noop")

        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(ledger[blyg_id]["version"], 2)

    def test_return_after_withdrawal_bumps_again(self):
        blyg_id = self._stamp_once()
        self._mark_withdrawn()
        bs.run_stamp(self.content_dir, self.ledger_path, write=True)

        path = self.content_dir / "post.md"
        text = path.read_text(encoding="utf-8").replace("blyg_withdrawn = true\n", "")
        path.write_text(text, encoding="utf-8")

        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        self.assertEqual(plans[0].kind, "return")

        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        entry = ledger[blyg_id]
        self.assertEqual(entry["version"], 3)
        self.assertFalse(entry["withdrawn"])
        self.assertEqual(entry["last_hash"], bs.content_hash("Body.\n"))
        self.assertEqual(entry["changelog"][-1]["note"], "returned")


class PinTests(TmpRepoTestCase):
    def setUp(self):
        super().setUp()
        self.public_dir = Path(self.tmp.name) / "public"
        self.static_dir = Path(self.tmp.name) / "static"

    def _stamp_once(self):
        write_post(
            self.content_dir, "post.md",
            'title = "Post"\ndate = "2024-01-01T00:00:00Z"\ndraft = false\n',
            "Body.\n",
        )
        plans = bs.run_stamp(self.content_dir, self.ledger_path, write=True)
        return plans[0].blyg_id

    def _write_built_item(self, blyg_id: str, version: int, **extra):
        items_dir = self.public_dir / "blyg" / "items"
        items_dir.mkdir(parents=True, exist_ok=True)
        doc = {
            "blyg": "0.2",
            "id": blyg_id,
            "kind": "thread",
            "origin": "https://example.org/blyg/",
            "created": "2024-01-01T00:00:00Z",
            "updated": "2024-01-01T00:00:00Z",
            "version": version,
            "content_md": "Body.\n",
            "content_html": "<p>Body.</p>\n",
            "content_hash": bs.content_hash("Body.\n"),
            "media": [],
            "transclusions": [],
            "changelog": [{"version": version, "at": "2024-01-01T00:00:00Z", "note": None}],
        }
        doc.update(extra)
        (items_dir / f"{blyg_id}.json").write_text(json.dumps(doc), encoding="utf-8")

    def test_pin_refuses_on_version_mismatch(self):
        blyg_id = self._stamp_once()
        self._write_built_item(blyg_id, version=99)

        parser = bs.build_parser()
        args = parser.parse_args([
            "--ledger-path", str(self.ledger_path),
            "--public-dir", str(self.public_dir),
            "--static-dir", str(self.static_dir),
            "pin", blyg_id,
        ])
        with self.assertRaises(bs.BlygStampError):
            bs.cmd_pin(args)

    def test_pin_copies_built_item_to_static(self):
        blyg_id = self._stamp_once()
        self._write_built_item(blyg_id, version=1)

        parser = bs.build_parser()
        args = parser.parse_args([
            "--ledger-path", str(self.ledger_path),
            "--public-dir", str(self.public_dir),
            "--static-dir", str(self.static_dir),
            "pin", blyg_id,
        ])
        rc = bs.cmd_pin(args)
        self.assertEqual(rc, 0)

        pinned = self.static_dir / "blyg" / "items" / blyg_id / "v1.json"
        self.assertTrue(pinned.exists())

        # §8's own shape: flat version/at/note/pinned, no changelog,
        # created, updated, or media key at all -- a pin is not a copy
        # of the live item document.
        pin_doc = json.loads(pinned.read_text(encoding="utf-8"))
        self.assertEqual(pin_doc["version"], 1)
        self.assertEqual(pin_doc["at"], "2024-01-01T00:00:00Z")
        self.assertIsNone(pin_doc["note"])
        self.assertTrue(pin_doc["pinned"])
        self.assertEqual(pin_doc["content_md"], "Body.\n")
        for absent in ("changelog", "created", "updated", "media"):
            self.assertNotIn(absent, pin_doc)

        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        self.assertTrue(ledger[blyg_id]["changelog"][0]["pinned"])

    def test_pin_refuses_a_withdrawn_item(self):
        blyg_id = self._stamp_once()
        path = self.content_dir / "post.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("draft = false\n", "draft = false\nblyg_withdrawn = true\n"),
            encoding="utf-8",
        )
        bs.run_stamp(self.content_dir, self.ledger_path, write=True)  # -> v2 endcap
        self._write_built_item(blyg_id, version=2, kind="withdrawn",
                                content_md="", content_html="")

        parser = bs.build_parser()
        args = parser.parse_args([
            "--ledger-path", str(self.ledger_path),
            "--public-dir", str(self.public_dir),
            "--static-dir", str(self.static_dir),
            "pin", blyg_id,
        ])
        with self.assertRaises(bs.BlygStampError):
            bs.cmd_pin(args)


class EndcapShapeTests(unittest.TestCase):
    def test_empty_content_hash_is_well_known(self):
        # sha256("") -- the endcap's content_md is always "".
        self.assertEqual(
            bs.EMPTY_CONTENT_HASH,
            "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )



FM = 'title = "Post"\ndate = "2024-01-01T00:00:00Z"\ndraft = false\n'


class StampHelpers(TmpRepoTestCase):
    def stamp(self, **kw):
        return bs.run_stamp(self.content_dir, self.ledger_path, write=True, **kw)

    def ledger(self):
        return json.loads(self.ledger_path.read_text(encoding="utf-8"))

    def edit(self, name, old, new):
        path = self.content_dir / name
        path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")

    def first(self, name="post.md", fm=FM, body="Body.\n"):
        write_post(self.content_dir, name, fm, body)
        return self.stamp()[0].blyg_id


class PublishedItemsStayBuildableTests(StampHelpers):
    """§4: items/{id}.json MUST return 200 forever once published."""

    def test_draft_after_publish_is_a_hard_error(self):
        self.first()
        self.edit("post.md", "draft = false", "draft = true")
        with self.assertRaisesRegex(bs.BlygStampError, "MUST stay 200"):
            self.stamp()

    def test_future_date_after_publish_is_a_hard_error(self):
        self.first()
        self.edit("post.md", "2024-01-01", "2999-01-01")
        with self.assertRaisesRegex(bs.BlygStampError, "future date"):
            self.stamp()

    def test_expiry_date_is_a_hard_error(self):
        self.first()
        self.edit("post.md", "draft = false", 'draft = false\nexpiryDate = "2030-01-01"')
        with self.assertRaisesRegex(bs.BlygStampError, "expiryDate"):
            self.stamp()

    def test_future_dated_new_item_waits_unstamped(self):
        write_post(self.content_dir, "later.md",
                   'title = "Later"\ndate = "2999-01-01T00:00:00Z"\n', "Soon.\n")
        plans = self.stamp()
        self.assertEqual(plans[0].kind, "future-skip")
        self.assertEqual(self.ledger(), {})
        self.assertNotIn("blyg_id", (self.content_dir / "later.md").read_text(encoding="utf-8"))

    def test_publish_date_wins_over_date(self):
        write_post(self.content_dir, "p.md",
                   'title = "P"\ndate = "2020-01-01T00:00:00Z"\npublishDate = "2999-01-01T00:00:00Z"\n',
                   "x\n")
        self.assertEqual(self.stamp()[0].kind, "future-skip")

    def test_missing_file_for_ledger_entry_is_a_hard_error(self):
        blyg_id = self.first()
        (self.content_dir / "post.md").unlink()
        with self.assertRaisesRegex(bs.BlygStampError, blyg_id):
            self.stamp()

    def test_missing_file_is_caught_by_check_too(self):
        self.first()
        (self.content_dir / "post.md").unlink()
        rc = bs.main(["--content-dir", str(self.content_dir),
                      "--ledger-path", str(self.ledger_path), "--check"])
        self.assertEqual(rc, 2)

    def test_duplicate_blyg_id_is_a_hard_error(self):
        self.first()
        text = (self.content_dir / "post.md").read_text(encoding="utf-8")
        (self.content_dir / "copy.md").write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(bs.BlygStampError, "both carry"):
            self.stamp()

    def test_renamed_file_keeps_its_version(self):
        blyg_id = self.first()
        (self.content_dir / "post.md").rename(self.content_dir / "moved.md")
        plans = self.stamp()
        self.assertEqual(plans[0].kind, "moved")
        entry = self.ledger()[blyg_id]
        self.assertEqual(entry["version"], 1)
        self.assertEqual(entry["path"], "content/blyg/moved.md")


class TransclusionDirectiveTests(StampHelpers):
    """§10.1/§10.2: directives MUST resolve; `![[id@vN]]` MUST be rejected."""

    ID = "7c9wk2mhq0v3xj8tn5rzfd41bg"

    def test_directive_line_is_refused(self):
        write_post(self.content_dir, "t.md", FM, f"Intro.\n\n  ![[{self.ID}]]  \n")
        with self.assertRaisesRegex(bs.BlygStampError, "MUST resolve"):
            self.stamp()

    def test_versioned_directive_is_refused_as_reserved(self):
        write_post(self.content_dir, "t.md", FM, f"![[{self.ID}@v2]]\n")
        with self.assertRaisesRegex(bs.BlygStampError, "reserved"):
            self.stamp()

    def test_inert_forms_are_fine(self):
        body = (f"Inline ![[{self.ID}]] is text.\n\n"
                f"```\n![[{self.ID}]]\n```\n\n"
                f"~~~~md\n![[{self.ID}]]\n```\n![[{self.ID}]]\n~~~~\n\n"
                f"![[notanid]]\n![[{self.ID.upper()}]]\n")
        write_post(self.content_dir, "t.md", FM, body)
        self.assertEqual(self.stamp()[0].kind, "new")

    def test_directive_after_a_closed_fence_is_live(self):
        write_post(self.content_dir, "t.md", FM, f"```\ncode\n```\n![[{self.ID}]]\n")
        with self.assertRaises(bs.BlygStampError):
            self.stamp()

    def test_withdrawn_items_are_not_scanned(self):
        blyg_id = self.first()
        self.edit("post.md", "draft = false", "draft = false\nblyg_withdrawn = true")
        self.edit("post.md", "Body.", f"![[{self.ID}]]")
        self.assertEqual(self.stamp()[0].kind, "withdraw")
        self.assertTrue(self.ledger()[blyg_id]["withdrawn"])


class KindTests(StampHelpers):
    def test_kind_is_recorded(self):
        blyg_id = self.first(fm=FM + 'blyg_kind = "fragment"\n')
        entry = self.ledger()[blyg_id]
        self.assertEqual(entry["kind"], "fragment")
        self.assertEqual(entry["changelog"][0]["kind"], "fragment")

    def test_kind_change_is_a_new_version(self):
        blyg_id = self.first()
        self.edit("post.md", "draft = false", 'draft = false\nblyg_kind = "fragment"')
        plans = self.stamp()
        self.assertEqual(plans[0].kind, "bump")
        self.assertIn("thread -> fragment", plans[0].detail)
        entry = self.ledger()[blyg_id]
        self.assertEqual((entry["version"], entry["kind"]), (2, "fragment"))
        self.assertEqual([c["kind"] for c in entry["changelog"]], ["thread", "fragment"])

    def test_invalid_kind_is_refused(self):
        write_post(self.content_dir, "p.md", FM + 'blyg_kind = "withdrawn"\n', "x\n")
        with self.assertRaises(bs.BlygStampError):
            self.stamp()

    def test_endcap_changelog_kind_is_withdrawn(self):
        blyg_id = self.first()
        self.edit("post.md", "draft = false", "draft = false\nblyg_withdrawn = true")
        self.stamp()
        self.assertEqual(self.ledger()[blyg_id]["changelog"][-1]["kind"], "withdrawn")

    def test_kind_change_while_withdrawn_waits_for_return(self):
        blyg_id = self.first()
        self.edit("post.md", "draft = false", "draft = false\nblyg_withdrawn = true")
        self.stamp()
        self.edit("post.md", "draft = false", 'draft = false\nblyg_kind = "fragment"')
        self.assertEqual(self.stamp()[0].kind, "noop")
        self.edit("post.md", "blyg_withdrawn = true\n", "")
        self.assertEqual(self.stamp()[0].kind, "return")
        entry = self.ledger()[blyg_id]
        self.assertEqual((entry["version"], entry["kind"]), (3, "fragment"))

    def test_ledger_without_kind_is_refused(self):
        blyg_id = self.first()
        ledger = self.ledger()
        del ledger[blyg_id]["kind"]
        self.ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        with self.assertRaisesRegex(bs.BlygStampError, "predates kind"):
            self.stamp()


class NoteTests(StampHelpers):
    def test_note_lands_on_the_new_version_only(self):
        blyg_id = self.first()
        self.edit("post.md", "Body.", "Better body.")
        self.stamp(note="sharpened the claim")
        notes = [c["note"] for c in self.ledger()[blyg_id]["changelog"]]
        self.assertEqual(notes, [None, "sharpened the claim"])

    def test_note_overrides_the_withdrawal_default(self):
        blyg_id = self.first()
        self.edit("post.md", "draft = false", "draft = false\nblyg_withdrawn = true")
        self.stamp(note="no longer true")
        self.assertEqual(self.ledger()[blyg_id]["changelog"][-1]["note"], "no longer true")


class AmendTests(StampHelpers):
    """--amend: versions the last deploy never carried are rewritten, not
    bumped again (§5.2: draft saves are invisible to the protocol)."""

    def test_edit_of_a_shipped_version_still_bumps(self):
        blyg_id = self.first()
        shipped = self.ledger()
        self.edit("post.md", "Body.", "Edit.")
        plans = self.stamp(published=shipped)
        self.assertEqual(plans[0].kind, "bump")
        self.assertEqual(self.ledger()[blyg_id]["version"], 2)

    def test_second_unshipped_edit_amends(self):
        blyg_id = self.first()
        shipped = self.ledger()
        self.edit("post.md", "Body.", "Edit one.")
        self.stamp(published=shipped, note="typo")
        self.edit("post.md", "Edit one.", "Edit two.")
        plans = self.stamp(published=shipped)
        self.assertEqual(plans[0].kind, "amend")
        entry = self.ledger()[blyg_id]
        self.assertEqual(entry["version"], 2)
        self.assertEqual(len(entry["changelog"]), 2)
        self.assertEqual(entry["changelog"][1]["note"], "typo")
        self.assertEqual(entry["last_hash"], bs.content_hash("Edit two.\n"))

    def test_stacked_unshipped_versions_collapse(self):
        blyg_id = self.first()
        shipped = self.ledger()
        for n in range(3):  # three plain bumps, as if run without --amend
            self.edit("post.md", "Body" if n == 0 else f"B{n - 1}", f"B{n}")
            self.stamp()
        self.assertEqual(self.ledger()[blyg_id]["version"], 4)
        self.edit("post.md", "B2", "Final")
        self.stamp(published=shipped)
        entry = self.ledger()[blyg_id]
        self.assertEqual(entry["version"], 2)
        self.assertEqual([c["version"] for c in entry["changelog"]], [1, 2])

    def test_undoing_unshipped_edits_reverts_to_shipped(self):
        blyg_id = self.first()
        shipped = self.ledger()
        self.edit("post.md", "Body.", "Oops.")
        self.stamp(published=shipped)
        self.edit("post.md", "Oops.", "Body.")
        plans = self.stamp(published=shipped)
        self.assertEqual(plans[0].kind, "revert")
        self.assertEqual(self.ledger()[blyg_id], shipped[blyg_id])

    def test_never_shipped_item_stays_v1_at_its_date(self):
        blyg_id = self.first()
        self.edit("post.md", "Body.", "Edit.")
        plans = self.stamp(published={})
        self.assertEqual(plans[0].kind, "amend")
        entry = self.ledger()[blyg_id]
        self.assertEqual(entry["version"], 1)
        self.assertEqual(entry["changelog"][0]["at"], "2024-01-01T00:00:00Z")

    def test_withdrawing_a_never_shipped_item_is_refused(self):
        self.first()
        self.edit("post.md", "draft = false", "draft = false\nblyg_withdrawn = true")
        with self.assertRaisesRegex(bs.BlygStampError, "never shipped"):
            self.stamp(published={})

    def test_a_pinned_unshipped_version_is_never_rewritten(self):
        blyg_id = self.first()
        shipped = self.ledger()
        self.edit("post.md", "Body.", "Edit one.")
        self.stamp(published=shipped)
        ledger = self.ledger()
        ledger[blyg_id]["changelog"][-1]["pinned"] = True
        self.ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        self.edit("post.md", "Edit one.", "Edit two.")
        self.assertEqual(self.stamp(published=shipped)[0].kind, "bump")
        self.assertEqual(self.ledger()[blyg_id]["version"], 3)


class FragmentCapTests(StampHelpers):
    def test_long_fragment_warns_but_publishes(self):
        write_post(self.content_dir, "f.md", FM + 'blyg_kind = "fragment"\n', "x" * 2001)
        plan = self.stamp()[0]
        self.assertEqual(plan.kind, "new")
        self.assertIn("SHOULD cap", plan.warning)

    def test_long_thread_does_not_warn(self):
        write_post(self.content_dir, "t.md", FM, "x" * 5000)
        self.assertIsNone(self.stamp()[0].warning)


class MediaTests(TmpRepoTestCase):
    """§5.4: a media URL MUST always serve the same bytes once published."""

    def setUp(self):
        super().setUp()
        self.media_dir = Path(self.tmp.name) / "static" / "blyg" / "media"
        self.media_dir.mkdir(parents=True)
        self.media_ledger = Path(self.tmp.name) / "data" / "blyg" / "media.json"
        (self.media_dir / "a.png").write_bytes(b"one")
        bs.run_media_stamp(self.media_dir, self.media_ledger, write=True)

    def test_new_file_is_recorded(self):
        recorded = json.loads(self.media_ledger.read_text(encoding="utf-8"))
        self.assertEqual(recorded, {"a.png": "sha256:" + __import__("hashlib").sha256(b"one").hexdigest()})
        self.assertEqual(bs.run_media_stamp(self.media_dir, self.media_ledger, write=True), [])

    def test_changed_bytes_are_refused(self):
        (self.media_dir / "a.png").write_bytes(b"two")
        with self.assertRaisesRegex(bs.BlygStampError, "same bytes"):
            bs.run_media_stamp(self.media_dir, self.media_ledger, write=True)

    def test_deletion_is_refused(self):
        (self.media_dir / "a.png").unlink()
        with self.assertRaisesRegex(bs.BlygStampError, "gone"):
            bs.run_media_stamp(self.media_dir, self.media_ledger, write=True)

    def test_unshipped_file_may_still_change_with_amend(self):
        (self.media_dir / "a.png").write_bytes(b"two")
        changes = bs.run_media_stamp(self.media_dir, self.media_ledger, write=True, published={})
        self.assertEqual(len(changes), 1)


class PinDryRunTests(StampHelpers):
    def test_dry_run_before_or_after_the_subcommand_writes_nothing(self):
        blyg_id = self.first()
        public = Path(self.tmp.name) / "public"
        static = Path(self.tmp.name) / "static"
        items = public / "blyg" / "items"
        items.mkdir(parents=True)
        (items / f"{blyg_id}.json").write_text(json.dumps({
            "blyg": "0.2", "id": blyg_id, "kind": "thread", "version": 1,
            "origin": "https://example.org/blyg/", "content_md": "Body.\n",
            "content_html": "<p>Body.</p>", "content_hash": bs.content_hash("Body.\n"),
            "transclusions": [],
        }), encoding="utf-8")
        common = ["--ledger-path", str(self.ledger_path), "--public-dir", str(public),
                  "--static-dir", str(static)]
        for argv in (common + ["--dry-run", "pin", blyg_id],
                     common + ["pin", blyg_id, "--dry-run"]):
            self.assertEqual(bs.main(argv), 0)
            self.assertFalse((static / "blyg").exists(), argv)
            self.assertNotIn("pinned", self.ledger()[blyg_id]["changelog"][0])


if __name__ == "__main__":
    unittest.main()
