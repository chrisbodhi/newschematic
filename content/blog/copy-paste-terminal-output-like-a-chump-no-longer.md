+++
title = "Copy & paste terminal output like a chump no longer!"
date = "2015-08-31T21:09:40"
tags = ["pipe output", "tee", "command line fun", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p><code>run command_with_output | tee /path/to/destination/file.txt</code></p>

<p>You&rsquo;ll still get the output of your command to the terminal, but that output will also get piped into <code>file.txt</code>, thanks to the <code>tee</code> command. Pre-installed on OS X.</p>