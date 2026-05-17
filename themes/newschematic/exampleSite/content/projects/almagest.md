---
title: "Almagest"
date: 2024-09-01
draft: false
deck: "A Rust crate for classical orbital mechanics. Keplerian elements, two-body propagation, coordinate transforms."
status: "shipped"
codename: "almagest"
stack: ["Rust", "nalgebra"]
repo: "https://github.com/chrisbodhi/almagest"
tags: ["rust", "orbital-mechanics", "open-source"]
---

Almagest is a small Rust crate for the kind of classical orbital mechanics a first-semester astrodynamics student would recognize: position and velocity from Keplerian elements, two-body propagation, the standard coordinate transforms between ECI, ECEF, and LVLH frames.

## Motivation

I wanted to compute satellite ground tracks for a side project and discovered that the Rust ecosystem for this had two modes: toy implementations missing whole chunks of reference material, or full-fat astrodynamics libraries with a learning curve measured in weeks.

## Approach

Almagest targets the gap. It aims to be *textbook-correct* — every function has a citation back to Vallado or Curtis — without being encyclopedic. You can read the whole crate in an afternoon.

## What's next

A port of the Lambert solver is the most-requested feature. I've had it on the todo list long enough that someone else might beat me to it, which would be fine.
