+++
date = "2025-10-16T07:33:27-05:00"
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

A momentum-exchange tether in lunar orbit can deliver a payload to low earth orbit (LEO) with [] times less [fuel than a rocket](https://newschematic.org/blog/how-brutal-is-the-rocket-equation/). The savings multiply when we consider that we do not have to send fuel (mass) from the earth for this return trip. I'm developing a simulation tool called Almagest to run tether calculations. Almagest is the foundational piece of software for a cislunar tether network, for everything from planning to web-based simulations, even for the embedded systems that will power the tethers themselves.

* * *

For a payload of 100 kg (about the weight of an average refridgerator), we need a delta-v of [] km/s to go from a low lunar orbit to low earth orbit. Currently, that means we have to schlep enough fuel from here to there to come back here again, about [] kg of [whatever fuel from last time]. This doesn't even account for the extra mass of the bigger rocket we need to transport that fuel. With a momentum-exchange tether in a lunar orbit, that delta-v for our payload is already ready and parked in orbit, waiting to send us regolith for study, [processed resources](that company getting helium-3), or even an astronaut. Let's see how what size tether system we need in place for this payload.

[maths maths maths]

* * *

Since we must obey the laws of economics as much as the laws of physics, we have to also consider the energy needed to reboost the tether after it returns that 100kg payload back home. We can take our time in getting back up to our target orbit; an ion engine can make up for the []m altitude drop over thousands of seconds (compared to a 350s Isp burst from a rocket), or about [] trips around the lunar equator.[^1]

[maths for impulse calculation for an ion booster]


Almagest is a Rust crate that I've started developing. The approach I'm taking will allow Almagest to be used in various contexts. Once it's set, the core logic won't have to be rewritten in other languages, thanks for the ability of LLVM to translate Rust source code into numerous contexts &mdash; servers, embedded, and even web targets via WebAssembly. By ensuring that the code is written without the standard library and that the crate is built using the `no_std` directive, we can target any computing platform that LLVM supports.

That's thinking about tomorrow, though. Today, we can build and run simple models that can calculate the core concepts that drive momentum-exchange tethers. And since we must obey the laws of economics as much as the laws of physics, we have to demonstrate that the energy savings in any single usage of the tether are significant enough to warrant investment in such a long-lasting system.

[^1]: It should be noted that the moon has very few known stable orbits
