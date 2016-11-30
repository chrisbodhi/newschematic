+++
title = "(&:stuff) > {|a| a.stuff}"
date = "2015-01-29T18:46:00"
tags = ["ruby", "skip red", "skip green", "just refactor", "what could go wrong", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>Rather than writing</p>

<p><code>object.map{ |o| o.action }</code>,</p>

<p>I just found out that I could write</p>

<p><code>object.map(&amp;:action)</code>.</p>

<p>I&rsquo;m currently attempting to suppress a very strong urge to refactor everything in my current project. No curly braces, no pipes? Sign me up!</p>

<p><a href="http://stackoverflow.com/a/24917606/2276791" target="_blank">src</a> &amp; in the <a href="http://ruby-doc.org/core-2.1.5/Symbol.html#method-i-to_proc" target="_blank">Ruby docs</a></p>