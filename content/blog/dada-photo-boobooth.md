+++
draft = false
categories = [
  "art",
  "projects",
]
tags = [
  "processing",
  "EAST",
  "collaboration",
  "selfies",
]
comments = false
showcomments = false
showpagemeta = true
date = "2018-11-17T10:29:08-06:00"
title = "Dada Photo Boo-booth"

+++

As the next step in the exploration of the ideas behind the [Dada Photo Booth](https://newschematic.org/projects/dada-photo-booth/), [Adam](http://dezein.co/) and I reworked the project
for showing at the [Museum of Human Achievement](http://themuseumofhumanachievement.com/) during the 2018 [East Austin Studio Tour](http://east.bigmedium.org/about.html). Responding to a call for artists working with the concepts around taking selfies, we intended to directly transplant our piece into one of about 30 stations in a selfie gauntlet. Personally, I was looking forward to the challenge of architecting and coding a stand-alone, self-service iteration of the Dada Photo Booth. However, once we received the requirements and context around the selfie gauntlet, it became clear that this would be an exercise in doing more with less coding.

The selfie gauntlet would consist of 30 stations, with participants starting at one end and working down the line. The artifact would be captured with their own phones, and they would not know what was coming up. And the entire experience would be timed &mdash; users would only get 30 seconds at each station, start to finish.

Initial ideas for how to rework the project included QR codes, gif uploads, app development, abusing a Kubernetes cluster <sup><a href="/blog/dada-photo-boobooth#1">1</a><span id="return-1" /></sup>, and on and on. Zac, the director of MOHA, had a simple suggestion: why not have the participant take a photo of a screen that's displaying their glitched image? I then took the suggestion a step further: why not introduce [this dynamic of self-image-capture in a prototypical context](https://www.theguardian.com/fashion/2018/sep/13/decoding-the-power-of-the-bathroom-selfie), the bathroom mirror?

<img src="/img/bathroom-selfie.jpg" alt="Bathroom selfie via Complex magazine" />

From this point on, the piece largely became a question of how to craft the setting. I picked up a bathroom vanity and sink from the [ReStore](https://www.austinhabitat.org/restore), and bought some new cabinet handles. Toothbrush, soap, ear swabs, and lotion all came from various [LOT 2046](https://lot2046.com) packages. Adam scavanged a stand for the monitor and created a wonderfully-constrasting backdrop to further imbue the concrete feeling of a sense of place.

For the digital part of our work, we went back to Processing from [p5.js](https://p5js.org/). The benefits were too good to pass up: direct access to the camera via an official library, a packaged executable for the show days, and the IDE <sup><a href="/blog/dada-photo-boobooth#2">2</a><span id="return-2" /></sup>. The most technical challenge we encountered was how to mirror the drawing of pixels on the screen, in order to more accurately mimic the bathroom experience; this simply became a matter of subtracting the position of the pixel in the X-axis from width of the screen.

Prior to the show, I picked up a webcam, in case something happened to the built-in camera in the display. This turned out to be some good foresight: the camera stopped working on the Sunday of the first weekend. Simply plugging in the webcam got us running again. This swap turned out to be unnecessary, as the built-in camera started to work again after a night at Adam's house. Perhaps the chilly temperatures at MOHA contributed to an intermittent failure, but the cause still remains unclear. In the future, though, I would consider leaving back-up equipment locked up with, or near, the primary hardware.

In the end, the Dada Photo Boo-booth became an exercise in the best kind of code: the code you don't need to write.

<a href="https://www.instagram.com/p/BqSyEUqFZSm2kCmEPAMFtZ954VuBxPNmGEexas0/"><img src="/img/dada-selfie-booth.jpg" alt="Photo by @dezein" title="Dada Photo Boo-booth" /></a>

<hr />

<span id="1">1</span>: The Javascript implementation of the app has a tendency to crash with a seg fault, so why not just spin up a few instances of the app behind a load balancer and deliberately restart each one after it completes its task? <a href="blog/dada-photo-boobooth#return-1">🔙</a>

<span id="2">2</span>: Presumbly, we also picked up some performance gains, but we didn't take measurements to back up any claims. <a href="blog/dada-photo-boobooth#return-2">🔙</a>
