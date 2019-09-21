+++
title = "Adding Custom Meta Tags to Hugo"
date = "2019-09-21T14:34:56"
draft = false
categories = [
  "blogging",
  "hugo",
]
tags = [
  "meta",
]
comments = false
showcomments = false
showpagemeta = true
+++

After reading about [the Mozilla Foundation and Coil's announcement](https://foundation.mozilla.org/en/blog/100-million-investment-reshape-economics-web/), I decided I wanted to try an experiment and add a [Coil micropayment `meta` tag](https://coil.com/docs/#web-monetization) to my blog. I couldn't find an obvious way to do this with [Hugo](https://gohugo.io) or much information about it in their docs. I first tried just adding [the key-value pair to my `config.toml`](https://github.com/chrisbodhi/newschematic/blob/master/config.toml#L20).

```
# config.toml

monetization = "$coil.xrptipbot.com/zP3gu5RkRVSdjBhe_fu3XA"
```

The values didn't end up in the `<head>` tag on my site, though. Then, after skimming through Hugo's discussion forum, I hit upon the idea to check out [the theme](https://github.com/shenoybr/hugo-goa)'s `header.html` partial. I added a check and a spot for [the `monetization` meta parameter](https://github.com/chrisbodhi/hugo-goa/blob/master/layouts/partials/header.html#L12) on my fork:

```
<!-- themes/hugo-goa/layouts/partials/header.html -->

{{ with .Site.Params.meta.monetization }}<meta name="monetization" content="{{.}}">{{ end }}
```

Now the value is populated when I build my site!

A more long-term solution would be iterate through the values in `config.toml`'s `[params.meta]` section, and populate the site's `meta` tags based on those key-value pairs.
