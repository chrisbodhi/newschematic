+++
title = "Loading Partials in Mustache"
date = "2014-07-13T23:12:15"
tags = ["mustache", "partial", "jade", "rtfm", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>This took me a while to put together. Luckily, RTFM helped. By the way, the example is written in Jade, which I compile to HTML [with Mustache braces in place] using a Grunt task.</p>

<p><code>index.jade</code> has this thing: <code>{{&gt; header}}</code> but it renders to a blank line.</p>

<p>I had the <code>header.mustache</code> file in the same directory (<code>mustache/</code>) as <code>index.mustache</code> [which is the file to which the Jade template compiles]. That directory, however, was not the default location that the <code>grunt-mustache-render</code> task was using. So, in my Gruntfile, I simply added <code>options: {directory: "mustache/"}</code> to the <code>mustache_render</code> task.</p>

<p>And now, <code>index.html</code> renders the header partial. Huzzah!</p>