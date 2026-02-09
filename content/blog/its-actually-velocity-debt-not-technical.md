+++
date = "2026-02-02T07:33:27-05:00"
draft = false
categories = ["work"]
tags = ["collaboration"]
comments = false
showcomments = false
showpagemeta = true
title = "It's actually velocity debt, not technical debt"
description = "Once again, naming things is hard."
+++

There are many kinds of ~technical~ velocity debt [^1]. There are those decisions you, as an engineer, make in the moment to finish a piece of work. Given more time, energy, and space to think, those are decisions you would have made differently. There's the kind of debt that's unused code&mdash;a retired feature, ignored test specs, multiple implementations of the same helper method or component. Then, there's the kind of debt that we'll cover here, debt that isn't even directly yours, but it impacts you every single day: outdated dependencies.

Briefly, a dependency is code that you or your team doesn't own, but that you use. In practice, it involves going to a hosted registry, finding a library that someone else has published there, and then downloading it for your project. It might be something used for logging messages from your server, it might be a view library for building UI in a web app. An engineer selects the library based on its features, or its popularity (genuinely a good thing), or maybe its documentation. It may very well be the case that this library is the only alternative to writing (and maintaining the code) yourself. It looks like a shortcut, but it's a trade-off waiting to happen.

This is where the "debt" comes from. It becomes tied to velocity some sprints or quarters later, when your dependency is starting to hamper your progress in other areas of development. You start working around its limitations or operating assumptions that differ from your use-case. You add it to the list of other dependencies that are preventing you from upgrading your runtime, because it's no longer maintained. You write the same workaround in three different places because the "right" fix would require updating half your dependency tree.

It all adds up, as debts do. You might start to bring up the pain points in your sprint retrospectives [^2]. A savvy product manager will notice not only deadlines slipping, or compromises on releasing hobbled versions of planned features, but start to pull signal from the general complaining that surfaces when engineers get together and talk. Your savvy PM will be able to discern upgrade talk to solve pain points (read: completing features) from upgrade talk to chase resume-driven development [^3].

## Who needs to care about this

If you're pre-seed, you don't. Not yet. You care about product, about finding fit, about surviving. Your team is small enough that everyone knows where the pain points are, and you've got an intuitive sense of which ones are worth fixing now versus later. Later will come [^4].

But if you're Series A or beyond, you need to have a rhythm for this work. You need to iterate on features as quickly as possible because that's going to close deals as much as your sales motion will. The customers you're courting at this stage have options, and the team that can ship the integration, the feature, the fix fastest is the team that wins the contract. Velocity debt is now directly tied to revenue.

## Structure the cleanup

The way you address this isn't by letting engineers go off and refactor everything. That's the fear, right? That you give developers an inch of "cleanup time" and they'll disappear into the codebase for three sprints, emerging with a beautifully architected system that does exactly what the old one did, just slower. No.

You structure cleanup periods. You put time in every sprint, explicitly, for debt work. And your product manager is going to be on board with this, because if they're actually listening during retros instead of responding to Slack messages, they're hearing the pain points. They're hearing _why_ features aren't being delivered on time, or _why_ they're being delivered hobbled. And if they've got a brain between their ears, they understand that this isn't just how developers are. This is addressable.

The work itself needs to be ticketed and storied, given the same treatment as feature work. Block off the time. Then, in your retrospectives or whatever else you're doing to maintain a good OODA loop[^5], verify this work is actually happening. If it's not, interrogate. Use your five why's. Figure out why debt work keeps getting bumped for "urgent" feature requests and fix that, because that's its own kind of debt&mdash;process debt, maybe, but it compounds just the same.

## Measure before you cut

This isn't about vibes, recency bias, or scoring points on Hacker News. You need to take measurements, see where the actual slowdowns are, and identify where your tests could be fixed by upgrading to a version that doesn't have an outstanding bug in your test runner.

<!-- TODO: Add specific PR references here -->

I'm not just talking out of my ass here. This is something that's happened, repeatedly, and the pattern is consistent: you upgrade a library and suddenly three workarounds in your application code become unnecessary, a flaky test becomes reliable, and the build that took four minutes now takes two.

You also want to look at where upgrading will let you write cleaner code&mdash;not "clean" in the Uncle Bob sense necessarily, but clean in the sense that you're not working around limitations anymore. You're no longer having to maintain your own janky monkey patches just to get what you need out of a library that fixed your exact issue two major versions ago. It's a liberating feeling, making that upgrade.

Also, take the time to examine the blocking dependencies: the ones where a single outdated library is holding back a cascade of others. This might be particular to the Node.js ecosystem, where you've got the Pareto principle in full effect&mdash;80% of projects rely on 20% of the packages out there&mdash;but I suspect it's universal. Find the linchpin libraries and update those first. The unlocks cascade.

## Reduce the surface area

Think about it like this: if you've got four sidewalks to shovel every winter, and you want to save your back, you figure out how to get yourself down to one sidewalk. Maybe you're empty nesters, moving to a smaller house because you don't need so much house anymore. Okay, that analogy is getting away from me, but the point stands: fewer dependencies means fewer things to maintain, fewer things to update, fewer things to break.

The same logic applies to features. Cutting out features that aren't used anymore should be part of your company's development lifecycle, not just a product decision. This motion needs to be exercised regularly, especially early on when you still don't know exactly where you're going. If you're accumulating baggage as you iterate, that baggage is going to weigh you down. You're going to get weird pages in the middle of the night for code paths nobody remembers writing. Devs hate getting paged. Nobody likes getting paged. I bet doctors don't even like it, unless they're looking for an excuse to dip out of family time. But I don't know very many doctors. I don't leave my house.

Find those weird things you don't want to support anymore and cut them out. At one job, I organized a code deletion bug bash once for the whole org, and at the end, we printed out all the deleted code, compressed the lines as much as we could, and had a fire. It was good. Cathartic. Highly recommend.

## A note on security

Joe Armstrong, creator of Erlang, used to say that the easiest way to make your code faster is to wait ten years, because the hardware will get faster. The analog here: the easiest way to make your dependencies faster and more secure is to upgrade them when a new version is ready and vetted.

That "vetted" part matters. Supply chain attacks are real and getting more common. You don't want to be the first to adopt a compromised package. Wait for a patch release or two. Give it a few days to bake. And if you're operating at any real scale, you should be using some sort of enterprise package vetting service instead of just raw-dogging npm or whatever your package manager ecosystem provides.

## Celebrate the work

Here's the thing that most organizations get wrong: they treat paying down velocity debt as a necessary evil, something to be tolerated but not celebrated. Features get demos. Features get called out in all-hands. Features get people promoted. And the engineer who spent a sprint upgrading the build system, cutting deploy times in half, enabling the next six months of feature work to ship faster? They get a pat on the head, if they're lucky.

This is a leadership failure.

If you want velocity debt work to actually happen, you need to celebrate it the same way you celebrate shipping. Demo the upgrade. Show the before and after. Call out the engineer who deleted 40,000 lines of dead code by name, in front of everyone. Make it clear that this work matters, that it's seen, that it's valued. Because it is. It's the foundation that everything else gets built on, and the people who maintain that foundation deserve recognition, not just the people who hang drywall on top of it.

The best engineering organizations I've worked with understand this intuitively. The rest learn it the hard way, when their best infrastructure people leave for places that actually appreciate what they do.

## What you get

Faster feature delivery. Higher sales velocity. A codebase that doesn't fight you every time you try to add something new. Developers who aren't burned out from wrestling with half-decade-old workarounds. Fewer 3 AM pages for systems nobody understands anymore. A more secure posture against supply chain attacks.

And maybe most importantly: a team that believes the work they do matters, because you've shown them it does. Fix your shit, upgrade your shit, and watch what happens.

>Colophon for workflow: after a run, I rambled at [Whisper Memos](https://whispermemos.com) for some minutes with all of the thoughts I've had brewing on this subject. I then took the transcript and the outline I received, and started writing. After a few paragraphs of my first draft, I edited lightly, and then turned to Claude. I asked Claude to use the voice I established at the start and then to fill in the rest of the piece, following the outline (I already have a Skill trained based on my existing blogging, so that helped). Took another pass over the rest in [Zed](https://zed.dev) and published.

[^1]: Hat tip to [Marc LeBrun](https://www.linkedin.com/in/marclebrun/) for getting us all a better handle on what we're actually talking about when we're talking about developers belly-aching.
[^2]: Or whatever other process you use to reflect on your work and improve your meta-game. You _are_ improving your meta-game, right? `<Anakin grinning />` Right?
[^3]: You'll have to work that out with your manager. Something once a quarter or half seems reasonable, but I'm merely a lifelong IC.
[^4]: Fingers crossed, I'm rooting for you, this will all be a good problem to have, &c.
[^5]: Observe Orient Decide Act, h/t Col. John Boyd
