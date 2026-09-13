+++
draft = false
categories = ["web", "fun", "project",]
tags = ["the king",]
comments = false
showcomments = false
showpagemeta = true
title = "The Kirby Krackle"
date = "2026-09-13T07:35:45-04:00"
+++

In honor of [Jack "The King" Kirby](https://kirbymuseum.org/biography/)'s birthday last month (he'd be 109 years old), here's `krackle.js`, a one-line `script` tag to give every click on every page that signature Kirby Krackle.

{{< plate fig="1" caption="The King in 1992. Photo by Suzy Skaar, via the <a href='https://kirbymuseum.org/free-culture-licensed-jack-kirby-photos/'>Jack Kirby Museum</a>, <a href='https://creativecommons.org/licenses/by-sa/3.0/'>CC BY-SA 3.0</a>." src="https://kirbymuseum.org/wp-content/uploads/2013/10/1992-JackKirby-SuzySkaar-gray-815x1024.jpg" alt="Jack Kirby photographed in 1992" />}}

Try it out by clicking anywhere in this page, and then read on for an overview of my process, the questions I abandoned, and what I think matters about making a toy like this.

{{< plate fig="2" caption="If you have JavaScript disabled, this is what you're missing." src="/img/krackle-hero.gif" alt="A krackle burst on a click, light theme" />}}

## First, how to use it

Inspect the [source](https://github.com/chrisbodhi/krackle) and try out [the demo page on GitHub pages](https://chrisbodhi.github.io/krackle/krackle-demo.html).

Add it to your HTML with this simple `script` tag:

```html
<script type="module">
  import { initKrackle } from "https://cdn.jsdelivr.net/gh/chrisbodhi/krackle@v0.3.0/krackle.esm.min.js";
  const krackle = initKrackle();
  // later, to tear down the canvas and listeners:
  // krackle.destroy();
</script>
```

This library does not depend on any frameworks or other imports. Indeed, both this page and the GitHub pages demo are static HTML sites.

{{< plate fig="3" caption="The negative-flash Krackle for dark themes." src="/img/krackle-dark.gif" alt="Dark mode support for the trend-followers (whom we once called 'hipsters')" />}}

## And now, to what matters

I also wanted to write up how I built this, and some of what I learned from Claude about building a library like this, with a brief brief to the LLM that whatever it builds should be performant. What I realized, though, is that this post was going to be me forcing myself to perform learning for the purposes of this note, and nothing more. I have been laboring under the mistaken illusion that I have to be more serious, even if building unserious things for my own amusement. To that end, I cut out the parts on optimization for browser animations, and focused purely on how to build the tool that let me better build what I had envisioned. I'm also left wondering (and maybe you'll wonder with me) why we aren't collectively having more fun with LLM's.

>Offload the things you don't want to do. Steer it to do those things better.
>Ask it to teach you the things you want to do, but don't yet know how.

## How it started

It was the naptime on the Fourth of July and I took out my phone to explore the idea for this extension. I had been reading a lot of _Fantastic Four_from the early '60's after re-re-watching the recent "First Steps." As I am wont to do, an idle thought ("what would the Kirby Krackle look like in a browser?") turned into a Claude chat. That chat turned into some TypeScript, which I later downloaded to my machine for fiddling. Side-note is that it would be rad to have a Claude Code sandbox that started in-app, but then was deployed to source control and a virtual server (NB: this is a very human workflow, and it's an open discussion as to how much we should be building for human-focused coding patterns and conventions).

As I started iterating in Claude Code on how the mechanism actually _felt_, I realized I couldn't prompt my way to success, that I would have to start tuning parameters by hand to evaluate the impact of changes. I'm more than used to making changes in my editor, popping over to the browser to inspect, going back to my editor, and repeating (_ad nauseam_, even). But, I wanted a tighter feedback loop (I'm greedy), so I had Claude refactor the code to work with a set of defaults for the Krackle config. The code would accept an override driven from changes made to a panel that I also had Claude build. Not knowing what all of the variable names meant, and thinking about sharing my process more broadly, I had Claude write info popups explaining the values' impact to the visualization.

{{< plate fig="4" caption="The Krackle tuner panel, with an info hint expanded." src="/img/krackle-tuner-panel.png" alt="The Krackle tuner panel, with the Ray Count info hint expanded" />}}

Even after I changed enough parameters to create an effect that reminded me less of Spot from "Spider-Man: Into the Spider-Verse," I still wasn't satisfied with the outcome. "Give me two options for on-screen flashes when clicking: white, like lightning; and a negative of the page and its contents." By not trying to emulate directly a static, two-dimensional fixed view medium, and instead exploring the possibilities of the target medium, I was able to get something that better conveyed the feeling of cosmic energy that the King communicated in his art. 

As we're seen time and time again, having a tight feedback loop is critical to letting the machine drive the work. Personally, I don't truck with many MCP tools, favoring CLI and scripts where possible. However, in this case, allowing Claude to refine its code and then check the visual rendering with the Chrome[^1] Dev Tools MCP was genuinely useful. That MCP server also allowed me to direct Claude to [create a skill for capturing animated gifs of its work](https://github.com/chrisbodhi/krackle/blob/trunk/.claude/skills/readme-gif/SKILL.md), both for me to evaluate, as well as for updating the repo's README.

## Have fun, do goofy things

Maybe it's because there's already a feeling of multiplayer-ness in our LLM chats that's preventing us from adopting tools that let multiple folks interact with an LLM in a shared session. This lack of audience is making us susceptible to staying stuck in a local maximum, and preventing us from one-upping each other into growth. I don't have any grand ideas about how to replace the mush of, e.g. short form video and the casinoification of everything with the MUSH (Multi-User Shared Hallucination) of an earlier era. But, I have a feeling that the path that gets us there goes through doing goofy shit and sharing it with our friends.


[^1]: My most contrarian take (not really) is that Safari is a fine browser

<!-- This snippet adds the Kirby Krackle to only this page on my blog -->
<script type="module">
  import { initKrackle } from "https://cdn.jsdelivr.net/gh/chrisbodhi/krackle@v0.3.0/krackle.esm.min.js";
  const krackle = initKrackle();
  // later, to tear down the canvas and listeners:
  // krackle.destroy();
</script>
