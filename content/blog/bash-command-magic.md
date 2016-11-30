+++
title = "bash command magic"
date = "2015-02-18T15:12:56"
tags = ["awk", "but not awkward", "csv", "unix", "stack exchange", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>Since I can&rsquo;t upvote the question or answer, I thought I&rsquo;d just give a shout-out to <a href="https://unix.stackexchange.com/questions/68808/bash-commands-script-to-remove-a-line-from-csv-with-duplicate-in-column" target="_blank">this question</a> on unix.stackexchange.com.</p>

<p>To delete duplicate rows from a CSV file using the command line:</p>

<p><code>awk -F, '!seen[$0]++' inputfile.csv &gt; outputfile.csv</code></p>

<p>Fantastic.</p>