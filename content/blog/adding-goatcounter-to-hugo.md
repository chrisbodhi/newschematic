+++
title = "Adding Goatcounter to Hugo, Simply"
date = "2026-02-13T14:00:00-05:00"
draft = false
categories = []
tags = []
comments = false
showcomments = false
showpagemeta = true
+++

_NB: This is implemented on the [PaperMod theme](https://adityatelange.github.io/hugo-PaperMod/)_

I was curious about adding privacy-sensitive metrics to my blog. When I was exploring Codename Nootka (which became Kibra), I came across Goatcounter. After emailing back and forth with a couple of dozen folks and talking with a few more, I realized that Kibra didn't have the legs I wanted. Still, I filed away what I learned, including that Goatcounter exists.

I came across [another blog post on how to do this](https://dadul96.github.io/posts/counting_page_views_on_hugo_papermod_using_goatcounter/) but I didn't want to keep track of changes to the theme, deal with a fork or git module; dependency management gets easier when you have fewer dependencies to care about. After poking around more in how PaperMod is built and Hugo's affordances, I came across the `extend_footer.html` pattern.

Why not `extend_head.html`? Because we don't want to slow down page load speeds by loading anything non-critical (apologies to my growth colleagues, but tracking pages loads isn't critical; the content is).

So, adding `extend_footer.html` to this repo that uses the PaperMod theme allowed me to unlock privacy-focused analytics:

```html
<script
    data-goatcounter="https://YR_ACCOUNT.goatcounter.com/count"
    async
    src="//gc.zgo.at/count.js"
></script>
<noscript>
    <img
        src="https://YR_ACCOUNT.goatcounter.com/count?p={{ .Path | safeURL }}"
    />
</noscript>
```

Check out that tracking pixel! Truly, a hack for the ages.
