+++
title = "'Recursion is the GOTO of functional programming.' -- Erik Meijer"
date = "2016-06-30T04:30:35"
tags = []
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<pre><code>
def fact(n):
    return reduce(lambda x, y: x * y, range(1, n + 1))

print(fact(5))
#=&gt; 120
</code></pre>