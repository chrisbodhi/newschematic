+++
title = "blyg"
outputs = ["blygmanifest", "blygfeed", "html"]

# Individual blyg items (fragments/threads under this section) never get
# their own HTML page in this phase (see hugo-blyg's docs/conformance.md) -- only
# the JSON/XML surfaces the protocol requires. `render = "never"` suppresses
# their output entirely; `list = "always"` keeps them fully enumerable via
# .Pages from the section-level templates that build blyg.json, feed.xml,
# items/index.json, and items/{id}.json. Scoped to `kind = "page"` so this
# section page itself (where those section-level templates actually run) is
# unaffected -- an unscoped cascade would suppress its own output too.
[[cascade]]
  [cascade.target]
    kind = "page"
  [cascade.build]
    render = "never"
    list = "always"
+++
