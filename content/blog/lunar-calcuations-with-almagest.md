+++
date = "2025-10-07T17:33:27-05:00"
draft = false
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

That's thinking about tomorrow, though. Today, we can build and run simple models that can calculate the core concepts that drive momentum-exchange tethers. And since we must obey the laws of economics as much as the laws of physics, we have to demonstrate that
the energy savings in any single usage of the tether are significant enough to warrant investment in such a long-lasting system.

## Δv

Δv, or delta-v, is what keeps orbital [] up at night. Simply, this is the change in velocity that is necessary for []. One of the great promises of a momentum-exchange tether is that the system can transfer tremendous amounts of delta-v to a payload without paying exponential costs to do so[^1]. The tether system must also be able to maintain most of its momentum in order to remain viable.

However, we can't evaluate these numbers in a vacuum (ha). To really get a sense of the unreasonable effectiveness of tethers, we have to look at the rocket equation.

## Tsiolkovsky's Rocket Equation

\[
\begin{aligned}
\Delta v = v_e \times \ln\left(\frac{m_0}{m_f}\right)
\end{aligned}
\]

The delta-v is the exhaust velocity (how much force can we generate) times the natural log of the initial mass (rocket, payload, and fuel) divided by the final mass (rocket and payload without fuel). That natural logarithm is the tyranny we're seeking to escape, or at least lighten the burden it exerts on us. Let's think through how we can determine the mass ratio for a payload going from the Earth's surface to an altitude:

\[
\begin{aligned}
\frac{m_0}{m_f} = e^{\frac{\Delta v}{v_e}}
\end{aligned}
\]

Consider a tether system in a circular orbit at 400 km, with a tether length of 200 km. To reach an altitude of 200 km, where said payload could be picked up for delivery to a higher orbit, calculating a \(\Delta v\) of 5.27 km/s[^2] and assuming a \(v_e\) of 3.5 km/s[^3] for our delivery mechanism:


\[
\begin{aligned}
\frac{m_0}{m_f} = e^{\frac{5.27}{3.5}}
\end{aligned}
\]

Our delivery rocket has a mass ratio of 4.5.

If we eschew the tether system and directly deliver a payload directly to an orbit of 400 km (in the same orbit as the tether system), our mass ratio increases greatly.

\[
\begin{aligned}
\frac{m_0}{m_f} = e^{\frac{7.8}{3.5}}
\end{aligned}
\]

That's 9.3, _more than double the mass ratio_, which means that's more than twice the amount of fuel needed. And that's just to get to same orbit as the tether. What about direct insertion to the top of the tether's rotation[^4]?

\[
\begin{aligned}
\frac{m_0}{m_f} = e^{\frac{10.07}{3.5}}
\end{aligned}
\]

**17.76**.

[^1] "bowing to the tyranny of the rocket equation" link on substack
[^2] Briefly, the base of the tether system at \(400 km\) is traveling at about \(7.67 km/s\) to stay in orbit. At the lowest point (closest to Earth), the tether tip is traveling at the orbital speed minus the speed at which the tether is rotating (\(2.4 km/s\)). So, \(5.27 km/s\).
[^3] "...typical rocket exhaust velocity of v_e ≈ 3.5 km/s (reasonable for a kerosene/LOX engine)." TODO -- add citation
[^4] Similar to [^2], but instead of subtracting the tether tip speed, we add it: \(7.67 + 2.4\).
