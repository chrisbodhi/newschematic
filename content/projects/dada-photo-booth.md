+++
title = "Dada Photo Booth"
draft = false
date = "2016-11-14T19:00:00-06:00"
categories = ["projects"]
tags = ["golang", "ruby", "processing", "dada", "glitch", "gifs", "teamwork makes the dream work"]
comments = false
+++

### An Inscrutable Representation of Yourself

![A wild Canadian appears](/img/glitch.gif)

[tumblr](http://dadaphotobooth.tumblr.com) | [source code, v1](https://github.com/chrisbodhi/processing-class/tree/master/exhibit_00) | [source code, Electron client and server](https://github.com/vurvco/dada-photo-booth)

_developer, artistic collaborator_

Designed and developed as a final project for [dadageek](http://dadageek.com/)'s course on creating generative art using Processing. Presented at the Fall 2016 Dadageek Student Showcase, which was part of [EAST](http://east.bigmedium.org).

_Tech Stack_

- Go and [Go OpenCV binding](https://github.com/lazywei/go-opencv) for image capture and cropping
- [Processing](http://processing.org) for image manipulation [i.e. making the art]
- [Gifsicle](https://github.com/kohler/gifsicle) for generating and compressing gifs
- Ruby for posting to [Tumblr](http://dadaphotobooth.tumblr.com) and local file cleanup

Reincarnated as an experience using p5.js for 2018 EAST. Read more [about it on the blog](/blog/dada-photo-boobooth/).
