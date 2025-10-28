+++
date = "2025-10-13T07:33:27-05:00"
draft = true
categories = ["programming", "almagest",]
tags = ["rust", "aerospace", "space",]
comments = false
showcomments = false
showpagemeta = true
title = "A lunar calculation with Almagest"
[params]
  math = true
+++

**BLUF**

A momentum-exchange tether in Earth orbit can deliver a payload to the Moon with [] times less fuel than a rocket. The savings multiply when there's another tether around the Moon to send a payload back, if only for the fact that we do not have to send fuel (mass) for the return trip. I'm developing a simulation tool called Almagest to run tether calculations. Almagest is the foundational piece of software for this tether network, for everything from planning to web-based simulations, even for the embedded systems that will power the tethers themselves.

* * *

Almagest is a Rust crate that I've started developing. The approach I'm taking will allow Almagest to be used in various contexts. Once it's set, the core logic won't have to be rewritten in other languages, thanks for the ability of LLVM to translate Rust source code into numerous contexts &mdash; servers, embedded, and even web targets via WebAssembly. By ensuring that the code is written without the standard library and that the crate is built using the `no_std` directive, we can target any computing platform that LLVM supports.

That's thinking about tomorrow, though. Today, we can build and run simple models that can calculate the core concepts that drive momentum-exchange tethers. And since we must obey the laws of economics as much as the laws of physics, we have to demonstrate that the energy savings in any single usage of the tether are significant enough to warrant investment in such a long-lasting system.
