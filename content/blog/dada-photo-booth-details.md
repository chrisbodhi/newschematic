+++
draft = false
categories = ["blog", "how i did it"]
tags = ["golang", "ruby", "processing", "opencv", "glitch", "gifs", "gifsicle", "dada"]
date = "2017-02-19T12:28:16-06:00"
title = "Dada Photo Booth: Details"
comments = false
showcomments = false
showpagemeta = true
+++

>Dada philosophy is the sickest, most paralyzing and most destructive thing that has ever originated from the brain of man.

For some reason that my therapist hasn't been able to nail down, I enjoy making things difficult for myself. When planning out the tech stack for the [Dada Photo Booth](todo), I decided to write all of the wrapper code in Go, which I was just starting to learn. What ended up getting produced, though, was a mixture of Go, Ruby, and command line invocations, wrapped in a brittle shell script. The unholy ghost of Marcel Duchamp must have been smiling down on us during our exhibit because nothing exploded or completely fell apart.

The story goes like this:

- A command from the CLI starts a shell script.
- The first command, `go run webcam_facedetect.go`, fires up a Go script.
  - The Go script loads up OpenCV, finds faces, and listens for a keystroke to save [an image of a] face.
- The second command, `processing-java --sketch=`pwd` --output=`pwd`/output --force --run`, does the art.
  - The back entrance to Processing, `processing-java`, creates a glitchy-looking block on top of the image of the face by grabbing the color from a random pixel. It does this 3500 times&mdash;we save off single frames of .gif images from frame 1500 to frame 3499. Processing exits.
- The third command, `gifsicle --delay=3 -O3 --loop artifacts/f*.gif > glitch.gif`, does the stitching.
  - We end up with an animated, looping gif that gets mega-compressed for the next step.
- The final command, `ruby post-to-tumblr.rb`, adds the image to Tumblr, but also does some clean-up.
  - The animated gif gets uploaded to our Tumblr, [dadaphotobooth.tumblr.com/](http://dadaphotobooth.tumblr.com/), and then the script cleans up the gif and our temp files.



