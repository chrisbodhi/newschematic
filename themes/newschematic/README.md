# newschematic

A Hugo theme in the shape of a carefully letterpressed field guide. Paper-warm ground, ink-black type, oxblood signal. Serif throughout. Figure-numbered plates, italic section rules, registration marks in the corners.

Built around three content types — **essays** (long-form writing), **projects** (structured work with specs), and **plates** (figure-focused pages) — and a small vocabulary of shortcodes that make writing in the system feel natural.

## Quick start

```sh
# In an existing Hugo site:
cd themes
git clone https://github.com/chrisbodhi/newschematic-theme.git newschematic
cd ..
echo 'theme = "newschematic"' >> hugo.toml
hugo server
```

Or to run the example site directly:

```sh
cd exampleSite
hugo server --themesDir ../..
```

## Content types

The theme expects your content to live under three top-level sections:

```
content/
├── _index.md          # home page intro (optional)
├── about.md           # falls back to _default/single.html
├── essays/
│   ├── _index.md      # essays index page (optional)
│   └── my-essay.md
├── projects/
│   └── my-project.md
└── plates/
    └── my-plate.md
```

Each section uses the right archetype automatically:

```sh
hugo new essays/on-small-plates.md
hugo new projects/almagest.md
hugo new plates/request-lifecycle.md
```

## Front matter

### Essays

```yaml
title: "On the virtues of the small plate"
date: 2026-04-18
draft: false
deck: "Why a careful drawing still beats a dashboard."  # italic tagline
tags: ["craft", "diagrams"]
number: "xiv"         # optional essay number for running head
```

### Projects

```yaml
title: "Almagest"
deck: "A Rust crate for classical orbital mechanics."
status: "shipped"     # "in progress" | "shipped" | "archived" | "on hold"
stack: ["Rust", "nalgebra"]
repo: "https://github.com/chrisbodhi/almagest"
demo: ""              # optional
```

### Plates

```yaml
title: "The request lifecycle"
deck: "A small schematic of what happens between a tap and a response."
fig: "iii"            # figure number, Arabic or Roman
caption: "The five stages."
image: ""             # path to image, OR leave empty and put SVG/content in body
```

## Shortcodes

The theme ships five shortcodes that account for the distinctive visual moves in the identity system. Use them; don't reach for plain `<div>` and inline styles.

### `plate` — a bordered, figure-numbered container

```
{{</* plate fig="1" caption="The anatomy of a small plate." */>}}
<svg>...</svg>
{{</* /plate */>}}
```

Attributes: `fig`, `caption`, `dashed` (boolean), `src` + `alt` for direct image use.

### `pull` — a pull quote

```
{{</* pull */>}}
It is easier, now, to make a thousand bad diagrams than one good one.
{{</* /pull */>}}
```

Optional `cite` attribute for attribution.

### `drop` — a drop-cap opening paragraph

Wrap the entire first paragraph of an essay:

```
{{</* drop */>}}
There is a particular kind of drawing that engineers of a certain
generation could make in fifteen minutes...
{{</* /drop */>}}
```

### `break` — a section-break ornament

```
{{</* break /*/>}}                    # default: datum mark
{{</* break style="asterism" /*/>}}   # three centered asterisks
{{</* break style="rule" /*/>}}       # short centered hairline
```

### `mn` — marginalia / sidenote

```
...the main text with an aside{{</* mn */>}}The aside itself.{{</* /mn */>}} 
and then the sentence continues.
```

On screens ≥1100px the note floats into the outer margin as a proper sidenote; on narrower screens it renders inline between hairlines.

## Configuration

Minimal example:

```toml
baseURL = "https://newschematic.org/"
title = "newschematic"
theme = "newschematic"

[params]
  author = "Christopher"
  tagline = "A field guide to building things."
  colophon = "Set in Iowan Old Style and IBM Plex Mono."

[[menu.main]]
  name = "Essays"
  url = "/essays/"
  weight = 10

[markup.goldmark.renderer]
  unsafe = true   # required for inline SVG in markdown
```

The `unsafe = true` under `markup.goldmark.renderer` is important — it lets you drop inline SVG into a `plate` shortcode body, which is where most of the theme's visual weight actually lives.

## Customizing the identity

The entire visual system lives in CSS custom properties at the top of `assets/css/newschematic.css`. To retheme — make it greener, bluer, colder, warmer — override the tokens in a `static/css/custom.css` or by editing the file directly:

```css
:root {
  --ns-paper:   #F4EFE3;  /* ground */
  --ns-ink:     #1C1917;  /* type */
  --ns-oxblood: #6B1D1D;  /* signal color */
  --ns-sepia:   #5C4B3B;  /* secondary */
  --ns-verdigris: #3D5949; /* organic accent */
  --ns-goldleaf:  #A47831; /* honor accent */
  --ns-serif:   "Iowan Old Style", Palatino, Georgia, serif;
  --ns-mono:    "IBM Plex Mono", ui-monospace, monospace;
}
```

## Dark mode

Respects `prefers-color-scheme` by default and persists explicit user choice in localStorage. The toggle sits in the top-right of the masthead. Dark mode renders as sepia-on-ink (a reading lamp) rather than bright-on-black (a terminal) — this is intentional.

## What's here and what isn't

**Here.** Home (journal-style index grouped by year), essays with drop caps and figure-numbered plates and marginalia, projects with structured specs sidebars, plates as figure-focused pages, prev/next navigation, dark mode, RSS.

**Not here (yet).** Search, comments, pagination on home (it groups by year instead — see `layouts/index.html`), taxonomy pages beyond the defaults, OpenGraph images, sitemaps beyond Hugo's built-in.

## License

MIT.
