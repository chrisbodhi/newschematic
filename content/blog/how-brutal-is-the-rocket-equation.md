+++
date = "2025-10-10T07:33:27-05:00"
draft = false
categories = ["math", "physics",]
tags = ["aerospace", "space",]
comments = false
showcomments = false
showpagemeta = false
title = "How brutal is the rocket equation?"
[params]
  math = true
+++

## Δv

Δv, or delta-v, is what keeps orbital engineers up at night. Simply, delta-v is the change in velocity that is necessary for anything to happen in space. One of the great promises of a momentum-exchange tether is that the system can transfer tremendous amounts of delta-v to a payload without paying exponential costs to do so.[^1]

However, we can't evaluate these claims in a vacuum (ha). To really get a sense of the unreasonable effectiveness of tethers, let's first look at the rocket equation more deeply.

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

Our rocket bringing a payload to 200 km has a mass ratio of 4.5.

If we eschew the tether system and deliver a payload directly to an orbit of 400 km (in the same orbit as the tether system), our mass ratio increases greatly.

\[
\begin{aligned}
\frac{m_0}{m_f} = e^{\frac{7.8}{3.5}}
\end{aligned}
\]

That's 9.3, _more than double the mass ratio_, more than twice the amount of fuel needed. And that's just to get to same orbit as the tether. What about direct insertion to the top of the tether's rotation?[^4]

\[
\begin{aligned}
\frac{m_0}{m_f} = e^{\frac{10.07}{3.5}}
\end{aligned}
\]

**17.76**.

This visualization really cements the trade-off we make when we choose rockets as our sole vehicle for interstellar travel.

{{< skyhook-viz >}}

The Saturn-V rocket that first took Americans to the moon weighed 2.9 million kg. Going to an altitude of 185 km, nearly to the lower tip of our hypothetical tether system, the rocket could carry a payload of 140,000 kg. That's about 10 school buses! However, the ratio is abysmal &mdash; more than 95% of the mass is devoted to delivering less than 5% of the mass to low earth orbit.[^5] Even with Starship, one of the most innovative rockets created, the ratio for getting to LEO is worse (less than 4% [^6]).

The basic physics is inescapable.

[^1]: ["Submitting to the tyranny of the rocket equation"](https://chrisbodhi.substack.com/p/submitting-to-the-tyranny-of-the)

[^2]: Briefly, the base of the tether system at \(400 km\) is traveling at about \(7.67 km/s\) to stay in orbit. At the lowest point (closest to Earth), the tether tip is traveling at the orbital speed minus the speed at which the tether is rotating (\(2.4 km/s\)). So, \(5.27 km/s\).

[^3]: With [a 353-second specific impulse in vacuum](https://web.archive.org/web/20220322143903/https://www.astronautix.com/l/loxkerosene.html), we multiply by the standard rate of gravitational acceleration, convert to \(km/s\), and round up to get \(3.5 km/s\) as the upper end for this fuel mixture.

[^4]: Similar to [^2], but instead of subtracting the tether tip speed, we add it: \(7.67 + 2.4\).

[^5]: With a translunar injection, the largest possible payload drops down to 43,500 kg &mdash 1.5% of the total mass.

[^6]: Starship weighs up to 4.99 million kg and will be able to deliver around 199,500 kg to LEO ([wikipedia](https://en.wikipedia.org/wiki/SpaceX_Starship))
