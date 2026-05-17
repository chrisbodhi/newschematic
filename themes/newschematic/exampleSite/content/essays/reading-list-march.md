---
title: "Reading list, March"
date: 2026-03-14
draft: false
deck: "Notes from a month of reading more robotics papers than I probably needed to."
tags: ["reading", "robotics"]
---

A short note on what I read this month and what stuck.

## Foundation models for robotics

The SayCan → RT-1 → RT-2 lineage is the arc most people know, but the paper I actually spent the most time with was *VoxPoser*, which frames the whole thing differently: instead of learning a policy, it uses the LLM to compose a cost function and lets an off-the-shelf optimizer do the actual trajectory work.

{{< pull >}}
The more I read in this space, the more the interesting questions feel like they're about composition, not scale.
{{< /pull >}}

That framing has stuck with me. It suggests a division of labor I find more honest than end-to-end learning: the model reasons about what *should* happen, and a well-understood classical system figures out *how*.
