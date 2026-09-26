# Blygger protocol v0.2 — publisher conformance checklist

Source: [`blygger/blygger-spec`](https://github.com/blygger/blygger-spec)
`docs/protocol-v0.2.md`, pinned at commit `c5884b9214b6972c3aed2fecf9aae68c9eab5267`.

This is every normative MUST / MUST NOT in §§4–10 (the publish side), turned
into a checklist, plus the §13 reader rules a validator needs to check
against. It is the spec against which `scripts/blyg_stamp.py` and the
`hugo-blyg` module templates (`modules/hugo-blyg/`) are built and reviewed.
An item checked here means the implementation satisfies it; it is not itself
proof — see the empirical notes inline where behavior was verified against
Hugo 0.151.0.

Scope for this repository: New Schematic publishes at Level 1 only, as a
single-author, non-multiplayer origin. Every item authors its `kind` via
`blyg_kind` in front matter (`"fragment"` or `"thread"`; defaults to
`"thread"`), and every thread currently carries `"transclusions": []`
(§10) — there is no local fragment corpus yet for a thread to actually
transclude. Real transclusion, the blogroll (§11), and generation
provenance (§5.7) are not exercised yet, so their rules are listed for
completeness but not all are load-bearing today.

## §4 — The publication surface

- [ ] The entire surface MUST be servable as plain static files.
- [ ] Publishers MUST serve `blyg.json` (manifest, §6.1), `feed.xml`
      (§7), `items/index.json` (archive index, §6.2), `items/{id}.json`
      (canonical item document, §5) for every ever-published item, and
      `items/{id}/v{n}.json` for pinned versions only (§8).
- [ ] File names within the surface (`blyg.json`, `feed.xml`, `items/…`)
      MUST NOT vary per deployment.
- [ ] `items/{id}.json` MUST return 404 for unknown ids and never-published
      drafts.
- [ ] `items/{id}.json` MUST return 200 permanently once the item has ever
      been published — including after withdrawal.
- [ ] `items/{id}/v{n}.json` MUST return 404 unless version n of item id is
      pinned, and MUST return 200 permanently once it is.
- [ ] All protocol timestamps MUST be ISO 8601 UTC (`…Z`), except the
      RFC 822 dates inside `feed.xml`.

## §5 — The item document (`items/{id}.json`)

- [ ] `id` MUST be 128 random bits, encoded as 26 lowercase Crockford
      base32 characters (alphabet `0123456789abcdefghjkmnpqrstvwxyz`, no
      padding), generated from a cryptographically strong source.
- [ ] Ids MUST NOT change across versions, withdrawal, or return.
- [ ] `content_hash` MUST be `"sha256:" + hex(SHA-256(content_md as
      UTF-8))`, computed per published version, covering `content_md`
      **only** — never `author`, media bytes, or `content_html`.
      *(Verified empirically: Hugo 0.151's `.RawContent` reproduces the
      file's post-front-matter bytes exactly, including leading/trailing
      newlines and a missing final newline — safe to hash directly.)*
- [ ] `version` MUST be a positive integer, incremented by exactly 1 per
      publish event. Draft saves are invisible to the protocol.
- [ ] Only the **latest** version's content is served in the item
      document; older content is withheld unless pinned (§8).
- [ ] `updated` MUST equal the latest changelog entry's `at`.
- [ ] `"kind"` is `"fragment"`, `"thread"` (§10), or `"withdrawn"` (§9) at
      this version. Authored via `blyg_kind` in front matter
      (`modules/hugo-blyg/layouts/partials/blyg/item.html`); the build
      fails rather than accept anything else, including `"withdrawn"`
      itself — that value is derived from `blyg_withdrawn` plus the
      ledger, never something a page authors directly.
- [ ] Threads carry `transclusions` (§10.3, currently always `[]` — no
      local fragment corpus yet to transclude); fragments omit the key
      entirely. Implemented as two different dict shapes, not a
      placeholder value, since an empty array on a fragment would itself
      be a spec violation.
- [ ] `media` entries: a media URL MUST always serve the same bytes once
      published (immutable).
- [ ] `author`, if present, MUST be accepted with any additional members;
      clients that store/re-emit item JSON MUST carry it verbatim, never
      synthesized or rewritten.
- [ ] `"forked_from"` MUST NOT be emitted at 0.2 (reserved for L2/0.3).
- [ ] The `generated` array, if used: MUST NOT carry instruction text or
      other pre-generation authoring state; is omitted entirely when a
      version involved no generation; a withdrawal endcap MUST NOT carry
      it. (Not used by New Schematic today — no generation-provenance
      workflow in scope.)
- [ ] If `generated` is used, the renderer MUST wrap each generated span
      in `content_html` as `<span class="blyg-tk-gen">…</span>` (inline)
      or `<div class="blyg-tk-gen">…</div>` (block) — a permanent wire
      token, never renamed.

## §6 — Manifest and archive index

- [ ] `blyg.json` carries `"blyg": "0.2"`, `level`, `generator`, `site`,
      `title`, `feed`, `items`, `updated`; `blogroll` key present only
      when a non-empty blogroll is served (not the case here).
      `level` comes from `[params.blyg].level` in `config.toml`
      (defaults to `1`); the build refuses any value other than `1`
      until this module actually ships the corresponding L2+ surfaces —
      config can lower ambition, never inflate the conformance claim on
      the wire.
- [ ] `items/index.json` lists **every** item ever published — including
      withdrawn items — with no window, ordered by `updated` descending.

## §7 — The feed (`feed.xml`)

- [ ] RSS 2.0 with the `blyg:` namespace `https://blygger.org/ns/0.1`
      (a permanent, opaque wire token — never tracks the protocol
      version).
- [ ] One `<item>` per publish event, newest first; window bounded
      (RECOMMENDED 50).
- [ ] GUIDs are per-version: `blyg:{id}:v{n}`, `isPermaLink="false"`.
- [ ] Entries render the item's **latest** content — a feed entry for an
      older publish event keeps its own `blyg:version`/note but its
      `<description>` MUST carry the latest version's HTML.
- [ ] A withdrawn item contributes **exactly one** entry (title
      `withdrawn`, empty description); its earlier publish events MUST be
      dropped from the window.
- [ ] Pinning emits no feed event.
- [ ] `<description>` HTML MUST be self-contained: absolute media URLs,
      no dependence on the origin's stylesheets or scripts.
      *(Empirical note: goldmark render hooks alone are not sufficient
      here — two of this site's shortcodes, `plate` with `src=` and
      `skyhook-viz`, inject `<img>`/`<script>` with root-relative URLs
      that never pass through the markdown image/link AST, so render
      hooks can't see them. A string-level rewrite of the fully rendered
      HTML is needed as a safety net; see `docs/blyg/hazards.md`.)*
- [ ] The opaque `author` object itself never appears in the XML; when
      `author.name` is present, publisher SHOULD emit `<dc:creator>`.
- [ ] `pubDate`/`lastBuildDate` use RFC 822; `blyg:*` timestamps stay
      ISO 8601.
- [ ] Publishers MUST emit `<blyg:manifest>`.
- [ ] Do not rely on literal `<![CDATA[…]]>` bytes surviving unchanged:
      `hugo --minify` unwraps CDATA into escaped entity text (decoded
      content is identical, wire bytes are not). Escape `content_html`
      as an ordinary XML text node instead of wrapping it in CDATA —
      behavior is then minify-invariant and immune to a literal `]]>`
      inside the content breaking a hand-rolled CDATA section.
- [ ] A literal `<?xml …?>` prolog in template text corrupts under
      Hugo's default `html/template` rendering even with zero template
      actions present (empirical, against Hugo 0.151.0). `blyg.json`'s
      output format sets `isPlainText = true` to avoid this entirely
      (matching Hugo's own built-in JSON output format). `feed.xml`'s
      does not — it follows Hugo's own embedded `rss.xml` template
      instead: stay on `html/template`, and mark just the prolog and
      `content_html` as pre-escaped (`safeHTML`, `transform.XMLEscape`)
      rather than opting the whole document out of autoescaping. Either
      way, the constraint is real; only the fix differs by surface. See
      `modules/hugo-blyg/README.md`.

## §8 — Pins (`items/{id}/v{n}.json`)

- [ ] Once pinned, the file MUST return 200 forever — including after
      withdrawal.
- [ ] Unpinned versions and unknown ids: 404.
- [ ] Withdrawal endcaps MUST NOT be pinned.
- [ ] Media referenced by any pinned version MUST be retained forever.
- [ ] Pinned documents carry no `media` array.
- [ ] No route may ever serve an unpinned older version, in any
      representation — a version display MUST NOT offer, imply, or hint
      at access to unpinned history.
- [ ] `blyg_stamp.py pin <id>` refuses to pin unless the built
      `public/blyg/items/{id}.json` version matches the ledger version.
- [ ] (If pinned pages are ever served) gated exactly like the JSON file;
      content is that version's publish-time `content_html`, verbatim;
      pinned pages MUST NOT appear in `feed.xml`, `items/index.json`, or
      add manifest vocabulary. *(Not built this phase — no live
      permalink pages yet; JSON/XML surfaces only.)*

## §9 — Withdrawal

- [ ] Withdrawing publishes a permanent endcap: version bump,
      `content_md = ""`, `content_html = ""`, `media = []`,
      `"kind": "withdrawn"`, `updated` set, changelog retained plus the
      endcap entry.
- [ ] For threads, the endcap also empties `transclusions` to `[]`.
- [ ] An endcap never carries a `generated` array.
- [ ] The item document stays 200 forever; pinned versions remain
      fetchable forever.
- [ ] Withdrawal is reversible: a later publish event (vN+1, with the
      item's authored kind) is the item returning under the same id.
- [ ] A ledger entry whose backing file is missing on disk is a hard
      error — `blyg_stamp.py` must never silently drop it.

## §10 — Threads and transclusion

*(Fragments can now be authored via `blyg_kind = "fragment"`, but none
transclude anything yet — every thread still emits `"transclusions": []`,
since resolving `![[id]]` directives at publish time isn't built. Rules
kept here for completeness and because the grammar is a **permanent
protocol surface**: any future post containing a bare `![[26-char-id]]`
line is a live transclusion directive whether or not this repo currently
resolves it.)*

- [ ] Transclusion targets MUST be fragments of the same origin (0.2,
      local-only).
- [ ] A line consisting solely of `![[` + a 26-character item id + `]]`
      is a transclusion directive; the same sequence elsewhere is inert
      text.
- [ ] `![[id@vN]]` is reserved: publishers MUST reject it at publish
      time.
- [ ] Every directive MUST resolve to a local, currently-published
      `kind: "fragment"` item — drafts, withdrawn items, unknown ids, and
      threads are publish errors.
- [ ] Resolution snapshots the target's latest published version, baked
      into the thread's `content_html` as
      `<blockquote class="blyg-transclusion" data-blyg-id="{id}"
      data-blyg-version="{n}">…</blockquote>` — no link inside.
      `blyg-transclusion` is a permanent wire token.
- [ ] `content_md` keeps the directives; republishing re-resolves every
      directive to the then-latest versions.
- [ ] Thread item documents carry a top-level `transclusions` array in
      directive order; fragments omit the key entirely; threads always
      carry it, even as `[]` for a withdrawn thread.
- [ ] Later edits, withdrawal, or pinning of a source fragment do **not**
      change a thread's already-baked snapshot (no cascade).
- [ ] No auto-pin: `transclusions[].version` may name a version with no
      fetchable per-version file.

## §13 — Reader conformance (informs the validator, not the publisher)

Kept here because §13 is what a validator checks a publisher's output
*against*; a bug on our side usually shows up as one of these failing.

- [ ] Rollup by `blyg:id`: highest `version` wins, ties broken by
      `updated`.
- [ ] A withdrawal endcap is roll-up-to-null; a later version under the
      same id is the item returning.
- [ ] Unknown kinds/JSON members/`blyg:*` XML elements/reserved
      constructs must not break parsing of the containing document —
      i.e. our own output must never force a reader to reject a whole
      document just to skip one field we got wrong.
- [ ] `items/index.json` (the reconciliation surface) must be complete
      and diffable against `feed.xml` — a reader offline for any
      duration must be able to recover losslessly from the index alone.
- [ ] Version numbers, never timestamps, drive rollup — our `version`
      counter must never skip or regress across a publish.
- [ ] A fetched document whose `version` is lower than a previously
      observed version is a protocol violation by us — `blyg_stamp.py`'s
      idempotency and monotonic versioning (§5.2) exist specifically to
      make this impossible to emit by accident.

## Design notes carried from Phase 0 recon

- Naive front-matter `date` values (no UTC offset — 89% of the existing
  `content/blog/` corpus, not relevant to `content/blyg/` since it starts
  empty, but the same date-parsing code path is shared) must be treated
  as UTC by `blyg_stamp.py`, matching Hugo's own default when no
  `timeZone` is configured (none is, here).
- `resources.FromString` + accessing the result (e.g. `.RelPermalink`)
  is the mechanism for fan-out files (`items/index.json`,
  `items/{id}.json`) — creating the resource without accessing it
  publishes nothing. See `modules/hugo-blyg/README.md` for the working
  pattern.
- Module-imported `layouts/` merge into the site's template lookup
  automatically; a module's own `hugo.toml` config (mediaTypes,
  outputFormats, outputs, params) does **not** — those must be declared
  in the consuming site's own config. `config.toml` carries the
  `[mediaTypes]`/`[outputFormats]` glue for this reason; `outputs =
  [...]` is set per-page on `content/blyg/_index.md`, scoped to the blyg
  section only, so `/blog/` and every other section are untouched.
