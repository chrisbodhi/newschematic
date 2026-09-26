# Hazard inventory — `content/blog/` (Phase 0 recon)

**Not currently in scope.** Blyg items live in `content/blyg/`, which starts
empty — none of the 193 existing `content/blog/` posts are being converted
or stamped. This inventory is kept because it surfaces two implementation
requirements that apply to *any* content this site ever feeds through the
blyg pipeline, including future posts in `content/blyg/` that happen to use
the same shortcodes:

1. Render hooks on the markdown image/link AST are **not sufficient** to
   guarantee `content_html` is self-contained (§7's absolute-URL
   requirement). Two shortcodes inject raw HTML with root-relative URLs
   that a render hook never sees, because they bypass the markdown
   image/link nodes entirely:
   - `plate` (`themes/newschematic/layouts/shortcodes/plate.html`), when
     called with `src=`, renders `<img src="{{ $src | relURL }}">` —
     `relURL` always produces a root-relative URL.
   - `skyhook-viz` (`layouts/_shortcodes/skyhook-viz.html`) renders a
     `<noscript><img src="/img/…">` fallback and a
     `<script src="/js/skyhook-viz.js">`, both root-relative, plus three
     absolute `https://unpkg.com/...` script tags.

   Any blyg pipeline building `content_html` needs a string-level rewrite
   of the fully rendered HTML (`src="/` / `href="/` → absolute, skipping
   already-absolute and protocol-relative `//` URLs) as a safety net
   alongside markdown render hooks — see `docs/blyg/conformance.md`'s §7
   entry.

2. A live `<script>` tag or CDN-loaded interactive visualization in a
   post's body rides into `content_html` verbatim (per spec, that's
   conformant — §14 puts sanitization on the reader). It will simply not
   run for any reader that sanitizes syndicated HTML (most will), so
   interactive content degrades to nothing unless the post also has a
   `<noscript>` fallback. Worth having as a writing convention if
   `content/blyg/` posts ever want embedded visualizations.

## Findings, for the record (content/blog/, 193 posts, not converted)

| Hazard | Count | Files |
|---|---|---|
| Root-relative URLs, source-visible | 6 posts, 11 refs | `branding.md`, `dada-photo-boobooth.md`, `how-to-save-327-6-million-using-rust.md`, `kirby-krackle.md`, `org-mode-reference.md`, `starting-with-gpui.md` |
| Root-relative URLs, shortcode-injected (invisible to a source-only grep) | +1 post | `how-brutal-is-the-rocket-equation.md` via `skyhook-viz` |
| Live `<script>` outside any code fence | 1 post | `kirby-krackle.md` (line 71 — a real inline ES module import; two other `<script>` hits in this file and in `adding-goatcounter-to-hugo.md` are inside ` ```html ` documentation fences and never reach rendered output) |
| Live `<script>` via shortcode | +1 post | `how-brutal-is-the-rocket-equation.md` via `skyhook-viz` (4 tags: 3 external CDN + 1 root-relative local) |
| Real MathJax delimiters (`\(...\)`) | 1 post | `how-brutal-is-the-rocket-equation.md`. (One false positive in `backups.md` — a Windows path `C:\Users\[username]\...`, not math.) MathJax itself loads from the theme's `<head>` (`layouts/partials/extend_head.html`), which no feed reader fetches — so even if this post's markup were converted, its equations would render as literal unrendered LaTeX-ish text for blyg subscribers. |
| Shortcodes in use | 3 posts | `plate` (`kirby-krackle.md`, `starting-with-gpui.md`), `mn` (`starting-with-gpui.md`), `skyhook-viz` (`how-brutal-is-the-rocket-equation.md`) |
| Drafts | 3 | `lunar-calcuations-with-almagest.md`, `resumes-for-agents.md`, `what-your-commit-know.md` |
| Naive `date` (no UTC offset) | 172 of 193 (89%) | e.g. `"2013-11-12T05:04:39"`. No `timeZone` configured, so Hugo parses these as UTC by default — any future stamping code must replicate that exactly rather than use local system time. |
| CRLF line endings / non-UTF-8 bytes | 0 | clean |
