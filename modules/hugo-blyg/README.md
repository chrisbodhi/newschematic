# hugo-blyg

A Hugo Module that builds the static publish-side surfaces of the
[Blygger protocol](https://github.com/blygger/blygger-spec) v0.2, Level 1
— `blyg.json` (manifest), `feed.xml`, `items/index.json` (archive index),
and `items/{id}.json` (canonical item documents) — from a section of
ordinary Hugo Markdown content plus a small JSON ledger.

Developed in-repo at `newschematic/modules/hugo-blyg`, wired in via a
local Go `replace` directive rather than a real module path, so it can be
pulled out into its own repository later by deleting one line
(`replace github.com/chrisbodhi/hugo-blyg => ./modules/hugo-blyg` in the
consuming site's `go.mod`) and pointing the import at wherever it lands.
Nothing in this directory references `newschematic.org` or any other
site-specific value — those all come in from the consuming site.

## What it owns vs. what the consuming site must provide

Hugo Modules merge an imported module's `layouts/`, `data/`, `static/`,
`archetypes/`, and `i18n/` into the site's own filesystem automatically.
They do **not** merge a module's own `hugo.toml`/`config.toml` — site-wide
configuration (`[outputFormats]`, `[mediaTypes]`, `[outputs]`, `[params]`)
has to be declared by whatever site imports this module. (Verified
empirically against Hugo 0.151.0 — see `docs/blyg/conformance.md` in the
consuming site for the write-up.)

So this module owns all the actual document-shaping logic —
`layouts/partials/blyg/item.html` builds one item document;
`layouts/blyg/section.blygmanifest.json` and
`layouts/blyg/section.blygfeed.xml` build the four surfaces — and the
site must add:

```toml
[module]
  [[module.imports]]
    path = "github.com/chrisbodhi/hugo-blyg"

[outputFormats]
  [outputFormats.blygmanifest]
    mediaType = "application/json"
    isPlainText = true          # load-bearing -- see note below
    baseName = "blyg"
  [outputFormats.blygfeed]
    mediaType = "application/rss+xml"
    baseName = "feed"
```

and a `go.mod` requiring/replacing this module, and a content section
(e.g. `content/blyg/_index.md`) whose own front matter opts into these
output formats and defines the render/list behavior for its items:

```toml
+++
title = "blyg"
outputs = ["blygmanifest", "blygfeed"]

[[cascade]]
  [cascade.target]
    kind = "page"
  [cascade.build]
    render = "never"   # no live HTML permalink pages yet
    list = "always"    # but still enumerable via .Pages
+++
```

`outputs` is set here, per-page, rather than in the site's global
`[outputs]` table — `[outputs] section = [...]` applies to *every*
section (e.g. a site's `/blog/`, too), and this module's output formats
have no business running there. The `content/llms.md` /
`outputs = ['llms']` pattern already used elsewhere in a consuming site
is the same idiom.

**`blygmanifest`'s `isPlainText = true` is not optional.** Without it,
Hugo runs the literal template text through `html/template`'s HTML
escaper — which corrupts a leading `<?xml ...?>` prolog and any
`<![CDATA[` marker even when the template contains no template actions
at all. This bit us during development; it matches Hugo's own built-in
JSON output format (`output.JSONFormat` in the Hugo source), which sets
the same flag for the same reason.

**`blygfeed` deliberately does not set it.** The escaping bug is real,
but Hugo's own embedded `rss.xml` template (`tpl/tplimpl/embedded/
templates/rss.xml` in the Hugo source) shows a narrower fix: stay on
`html/template` (the default), and mark just the two spots that would
otherwise get mangled as pre-escaped, rather than opting the whole
document out of autoescaping:

```gotemplate
{{ printf "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" | safeHTML }}
...
<description>{{ .description | transform.XMLEscape | safeHTML }}</description>
```

`section.blygfeed.xml` follows that idiom. The payoff: every other
interpolated value (titles, ids, the site's own base URL) gets Hugo's
ordinary contextual autoescaping automatically — one less place a future
edit has to remember to escape by hand, and it's what a maintainer
who's read Hugo's own RSS template will already expect to see.

## Content contract

- One Markdown page per item, anywhere under the section that sets
  `outputs`/`cascade` as above.
- `blyg_id` in front matter, once assigned (a one-time process external
  to this module — see the consuming site's `scripts/blyg_stamp.py`).
  A page without `blyg_id` is skipped from every blyg surface (with a
  build warning), not an error — lets a post exist in the section before
  it's been stamped.
- `blyg_withdrawn = true` marks it withdrawn; the ledger, not this
  module, decides whether that's a fresh transition (§9 endcap) — this
  module only ever reads the ledger's `withdrawn` flag, it never writes
  it.
- `blyg_kind = "fragment"` or `"thread"` (defaults to `"thread"` when
  absent). Threads always carry a `transclusions` array (currently
  always `[]`); fragments omit the key entirely (§10.3) — this module
  builds a different dict shape per kind rather than a placeholder
  value, since an empty `transclusions` on a fragment would itself be a
  spec violation, not a harmless default. Any other value, including
  `"withdrawn"`, fails the build: `"withdrawn"` is a wire-level state
  this module derives from `blyg_withdrawn` plus the ledger, never
  something a page authors directly.
- `draft = true` pages are already excluded from `.Pages` by Hugo itself
  under a normal (non-`--buildDrafts`) build; this module does nothing
  special for drafts.
- `title` is never read. The item document schema (§5) has no title
  field at all — fragments and threads are microblog-style, not
  headlined essays — so this module doesn't put one in `feed.xml`
  either; `<description>` alone satisfies RSS 2.0's "at least one of
  title/description" rule. The sole exception is the withdrawal event,
  where §7 is normative by name ("its withdrawal event, with title
  `withdrawn`") — that literal string is hardcoded, not read from any
  page.

## Conformance level

`blyg.json`'s `"level"` field (§3) comes from the consuming site's own
`[params.blyg].level`, defaulting to `1` when unset. This module only
accepts `1` — it fails the build on anything else, since claiming a
higher level on the wire without actually shipping that level's
surfaces (the blogroll, generation provenance disclosure, ...) would be
a false conformance claim, not a preference this module can just defer
to config.

## The ledger

`data/blyg/ledger.json`, keyed by id, one entry per item:
`{path, created, version, last_hash, withdrawn, changelog}`. Produced
and maintained by the consuming site's own stamp script — this module
only reads it, via `site.Data.blyg.ledger` (Hugo's standard
`data/<path>` → `site.Data.<path>` mapping). `content_hash` in the item
document is always the ledger's `last_hash`, never recomputed at build
time, since the two are guaranteed byte-identical by construction (the
stamp script hashes `.RawContent`-equivalent bytes the same way this
module reads `.RawContent` itself).

## The `resources.FromString` fan-out gotcha

`items/index.json` and every `items/{id}.json` are one-file-per-item, not
one-per-section, so they can't use Hugo's native "one output file per
(page, output format)" mechanism the way `blyg.json`/`feed.xml` do.
Instead they're published via
`{{ $r := resources.FromString "blyg/items/x.json" $content }}` — but
**that only actually writes the file once the resource is accessed**
(e.g. `$r.RelPermalink`, `$r.Content`). Creating the resource and never
touching it publishes nothing, silently. Every call site in this module
does `{{ $_ := $r.RelPermalink }}` immediately after creating one, purely
to force the write, discarding the value.

## Absolute URLs in `content_html`

The protocol requires `content_html` to be self-contained (§7). Render
hooks on the markdown image/link AST aren't enough on their own if the
consuming site has shortcodes that inject raw HTML with root-relative
URLs outside those AST nodes entirely (a real case in the site this was
built for — see its `docs/blyg/hazards.md`). `item.html` instead rewrites
the *fully rendered* HTML string directly: `(src|href)="/([^/"])` →
`${1}="{base}/${2}`, using a captured "not another slash" character
instead of a negative lookahead, because Hugo's regex engine (RE2) has
none. This catches shortcode-injected markup and ordinary markdown
images/links in one pass, so no render hooks are needed.

## Not yet built

Real fragments/transclusion, pinned per-version JSON files served from
`static/blyg/items/{id}/v{n}.json` (the consuming site's
`blyg_stamp.py pin <id>` writes them; this module doesn't read them
back), the blogroll (§11), generation provenance (§5.7), and any live
HTML permalink page for an item (§8.4) — all Level 1-adjacent but not
exercised by this site yet.
