---
title: "On the virtues of the small plate"
date: 2026-04-18
draft: false
deck: "Why a careful drawing, hand-labeled, still beats a dashboard — and what that means for the tools we build next."
number: "xiv"
tags: ["craft", "diagrams", "tools"]
---

{{< drop >}}
There is a particular kind of drawing that engineers of a certain generation could make in fifteen minutes with a mechanical pencil, a straightedge, and a French curve. It fit on a letter-size sheet. It named every component. It answered the question being asked, and no others. It was, almost always, beautiful — not because it was drawn with the intention of being beautiful, but because the constraints under which it were made had beauty built into them.
{{< /drop >}}

I have been thinking about these drawings lately, for reasons that are probably obvious to anyone who has watched the last two years of generative-AI interface design and felt a small, specific grief about it.

{{< plate fig="1" caption="The anatomy of a small plate: one subject, two or three labels, a margin wide enough to breathe in." >}}
<svg viewBox="0 0 500 180" width="100%" style="display:block;">
  <rect x="10" y="10" width="480" height="160" fill="none" stroke="currentColor" stroke-width="0.5" stroke-dasharray="3 3"/>
  <circle cx="130" cy="90" r="42" fill="none" stroke="currentColor" stroke-width="0.5"/>
  <circle cx="130" cy="90" r="28" fill="none" stroke="currentColor" stroke-width="0.5"/>
  <circle cx="130" cy="90" r="3" fill="var(--ns-oxblood)"/>
  <path d="M172 90 L250 90 L250 50 L370 50" fill="none" stroke="currentColor" stroke-width="0.5"/>
  <circle cx="370" cy="50" r="2" fill="currentColor"/>
  <text x="376" y="54" font-family="IBM Plex Mono, monospace" font-size="10" fill="currentColor">A — the argument</text>
  <path d="M130 132 L130 150 L370 150" fill="none" stroke="currentColor" stroke-width="0.5"/>
  <circle cx="370" cy="150" r="2" fill="currentColor"/>
  <text x="376" y="154" font-family="IBM Plex Mono, monospace" font-size="10" fill="currentColor">B — the reader</text>
  <path d="M88 90 L40 90 L40 130" fill="none" stroke="currentColor" stroke-width="0.5"/>
  <circle cx="40" cy="130" r="2" fill="var(--ns-oxblood)"/>
  <text x="46" y="134" font-family="IBM Plex Mono, monospace" font-size="10" fill="var(--ns-oxblood)">C — the claim</text>
</svg>
{{< /plate >}}

The dashboard, as a form, is a kind of panic. It says: *I do not know what you care about, so here is everything.* The small plate, by contrast, is a gift — it has been edited. Someone decided, on your behalf, that these three things matter and the other eight do not, and signed their name to that decision in the corner.{{< mn >}}This is also, incidentally, what a good editor does to a draft — prunes, not adds.{{< /mn >}}

{{< pull >}}
It is easier, now, to make a thousand bad diagrams than one good one. This is a problem, but it is also an opportunity.
{{< /pull >}}

What I want from the next generation of tools — and what I am trying to build, in my small ways — is something that collapses the distance between the careful drawing and the running prose. A sheet you can read like a book and a book you can read like a sheet. Warm paper. Ink. A register mark in the corner, so you know someone was here.

{{< break />}}

## What the plate asks of you

The discipline of the small plate is not the drawing. The drawing is easy. The discipline is the editing that happens before the drawing — the decision about what to leave out. Most technical communication fails at this step, not at the step of rendering.

When you sit down to make a plate, three things have to be settled before you touch the page:

- The subject. One noun, not three. "The request lifecycle." Not "system architecture."
- The claim. What you want the reader to believe when they're done looking.
- The audience. Whose eyes, at what level of context, for what purpose.

The drawing follows from these three. If you can't answer them, the plate you make will be a dashboard with pretensions.

{{< break style="asterism" />}}

## A word about warmth

I should say why I keep insisting on warmth in a medium — technical documentation — that traditionally prizes its absence. The claim is not that warmth is necessary; the claim is that coldness is a *choice*, and it is usually a choice made by accident. The Swiss-modernist engineering diagram is a specific aesthetic that happens to have colonized the default. There is nothing inevitable about it.

A Johnston Underground sign is warm. A NASA publication from 1962 is warm. An illuminated manuscript marginalia is warm. These are all technical documents. The warmth costs nothing and gains something real: the sense that a person made the thing, and that it was made *for* someone.

This is the ambition of newschematic as a project, and of every small plate in it.
