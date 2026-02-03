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

There are many kinds of ~technical~ velocity debt [^1]. There are those decisions you, as an engineer, make in the moment to finish a piece of work. Given more time, energy, and space to think, those are decisions you would have made differently. There's the kind of debt that's unused code &mdash; a retired feature, ignored test specs, multiple implementations of the same helper method or component. Then, there's the kind of debt that we'll cover here, debt that isn't even directly yours, but it impacts you every single day: outdated dependencies. 

or [[["Every line of code is legacy code, and it's all technical debt," some of your saltier colleages may say. They're right, but they're also wrong: every piece of lumber is no longer a tree, but that doesn't mean it can't be useful in its new configuration. We don't have time for a book-length treatise right now, so we're going to address a narrow subset of velocity debt: maintaining third-party dependencies.]]]

Briefly, a dependency is code that you or your team doesn't own, but that you use. In practice, it involves going to a hosted registry, finding a library that someone else has published there, and then downloading it for your project. It might be something used for logging messages from your server, it might be a view library for building UI in a web app. An engineer selects the library based on its features, or its popularity (genuinely a good thing), or maybe its documentation. It may very well be the case that this library is the only alternative to writing (and maintaining the code) yourself. It looks like a shortcut, but it's a trade-off waiting to happen.

This is where the "debt" comes from. It becomes tied to velocity some sprints or quarters later, when your dependency is starting to hamper your progress in other areas of development. You start working around its limitations or operating assumptions that differ from your use-case. You add it to the list of other dependencies that are preventing you from upgrading your runtime, because it's no longer maintained. You [].

It all adds up, as debts do. You might start to bring up the pain points in your sprint retrospectives [^2]. A savvy product manager will notice not only deadlines slipping, or compromises on releasing hobbled versions of planned features, but start to pull signal from the general complaining that surfaces when engineers get together and talk. Your savvy PM will be able to discern upgrade talk to solve pain points (read: completing features) from upgrade talk to chase resume-driven development [^3].



If you're already Series A or above, you need to make sure that you're able to iterate on features as quickly as possible because that's going to close deals as much as your sales motion. And addressing truths from the future, what you need to be doing is getting out of your own way. And you gonna do that by structuring cleanup periods. This is gonna be in every sprint, and your product manager is going to be on board.

Because when you do your retro or other sorts of self, if your PM's actually listening instead of responding to Slack messages, they are hearing the pain points and why the features aren't being delivered on time, how they want them, and they understand. If they're listening and if they've got a brain in between their ears, that this isn't something that just happens. This isn't just how developers are. This is something that's actually addressable.

If they can calm their shit down long enough for an answer to happen. And that isn't going to be letting them, developers, go off willy-nilly and just refactoring everything and refactor everything. This is going to be taking measurements, seeing what the slowdowns are, seeing where your tests could be fixed by upgrading. Because maybe there is an outstanding issue from your current old version of your test runner.

🚨 See existing PRs for references to this.

You know, I'm not just talking out of my ass. This is something that's happened and it's real. And we also want to look at where upgrading the library is going to let us write code cleaner, cleaner, not in necessarily the Bob sense, but cleaner in the sense that we're not having to work around limitations. We're not having to use our own janky monkey patches to be able to get what we want, what we need out of this library.

Just updating it, taking that time, running through your dependencies that are linked is gonna unlock that product development. We also wanna examine velocity debt cases where you have one library that is old and it's blocking other libraries that depend on it. I don't know if this is particular to the Node.js ecosystem where you've got like the Pareto principle where 80% of projects rely on 20% of the other projects that are out there in the ecosystem.

Them, so what you want to do is you want to cut down the surface area of what you need to maintain. I mean, like think about it like this, you know, if you have, I don't know, four sidewalks to shovel every winter and you want to save your back and figure out how to get yourself one sidewalk to shovel. I don't know, empty nesters downgrading, moving to a smaller house, and they don't need so much house. It's probably not a great analogy there either. The point still stands.

Other things to take into account when we're talking about velocity debt, talking about cutting out features that aren't used anymore. Early on in your product, this should be a company development life cycle, not product development. This should be a motion that is relied on that is exercised because you still don't know where you're going.

And if you're accumulating baggage as you're iterating, then that baggage is going to start weighing you down. You're going to get weird pages in the middle of the night for your devs. Devs hate getting paged. No one likes getting paged. I bet doctors don't even like it, unless they're looking for an excuse to dip out of family time. But I don't know very many doctors. I don't leave my house.

So, what you want to do is find those weird things that you don't want to support anymore and just cut them out. And that reminds me that we had a code deletion bug bash one time and at the end, we printed out all the deleted code, squished it down as much as we could, and had a fire. Uh, and it was fun, it was pretty good.

And then the other thing, um, that you want to figure out is working this into your sprints or however you break up work. You know, like does want to do this. On the whole, your engineers would like things to be faster, and as Joe, creator of Erlang, would say, the easiest way to make your code faster is to wait 10 years, because your hardware is going to get faster.

Analog to that is that, make your dependencies faster, and the fastest way to do that, the easiest way to do that is to upgrade them when a new version is ready and vetted. Supply chain attacks should be mentioned here, so like wait until you get like to a patch release or it's x days old. And also, you know, like in your enterprise, you want to be using some sort of service instead of just raw dogging npm or whatever your package manager ecosystem provides.

Definitely need to keep raw dogging npm in there. And then the other thing that we want to include is getting back to that thought. Your product people need to be encouraging this because you want to schedule this time, make sure this time is blocked off. It doesn't have to be just the upgrade dependencies; we addressing other tech debt.

But this needs to be ticketed and storied and given appropriate space. And in your retrospective or whatever else you're doing to make sure that you have a good OODA loop. Make sure that this work is being done. If it's not, interrogate. Using your five whys and figure out why it's not being done. Fix that shit and then upgrade your shit for maximum productivity, happiness, and increasing sense of fulfillment during your work hours. End of note.

So, one of the punchlines here at the end is going to be, if you're a pre-seed, you don't worry about this because you just care about product. And the team and the surface area is small enough that everyone knows what the problems are and has an intuitive sense on how to best solve them in terms of unlocks, what is the biggest pain point.


[^1]: Hat tip to [Marc LeBrun](https://www.linkedin.com/in/marclebrun/) for getting us all a better handle on what we're actually talking about when we're talking about developers belly-aching.
[^2]: Or whatever other process you use to reflect on your work and improve your meta-game. You _are_ improving your meta-game, right? `<Anakin grinning />` Right?
[^3]: You'll have to work that out with your manager. Something once a quarter or half seems reasonable, but I'm merely a lifelong IC.
