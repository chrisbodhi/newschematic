+++
title = "Refactoring. It's a delight."
date = "2015-02-01T07:30:38"
tags = ["ruby", "refactor", "fun with arrays", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>From</p>

<div class="gist"><a href="https://gist.github.com/chrisbodhi/15210705414f1b4afcf2" target="_blank">https://gist.github.com/chrisbodhi/15210705414f1b4afcf2</a></div>

<p>to</p>

<p><code>file_info[:control_info].map {|arr| arr[1] }</code></p>

<p>to</p>

<p><code>file_info[:control_info].map(&amp;:last)</code></p>