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
        self.assertEqual(entry["changelog"], [{"version": 1, "at": "2024-03-01T12:00:00Z", "note": None}])
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

    def _write_built_item(self, blyg_id: str, version: int):
        items_dir = self.public_dir / "blyg" / "items"
        items_dir.mkdir(parents=True, exist_ok=True)
        (items_dir / f"{blyg_id}.json").write_text(
            json.dumps({"id": blyg_id, "version": version}), encoding="utf-8"
        )

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

        ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        self.assertTrue(ledger[blyg_id]["changelog"][0]["pinned"])


class EndcapShapeTests(unittest.TestCase):
    def test_empty_content_hash_is_well_known(self):
        # sha256("") -- the endcap's content_md is always "".
        self.assertEqual(
            bs.EMPTY_CONTENT_HASH,
            "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )


if __name__ == "__main__":
    unittest.main()
