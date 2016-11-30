+++
title = "Changing git remote origin"
date = "2014-04-13T01:41:32"
tags = ["git", "nasahackathon", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>&ldquo;Midway through development we decided to switch from private shared accounts to a corporate account. Switching local repos couldn&rsquo;t be easier:&rdquo;</p>

<pre><code>git remote rm origin  #Removes old origin
git remote add origin https://username@bitbucket.org/your.new.repo        
#Adds new origin pointing to BitBucket
git push -u origin  #Pushes commits to new repo
</code></pre>

<p>[I love it when this stuff works so easily.]
<a href="http://andersonleeb.com/blog/changing-git-remote-origin" target="_blank">src</a></p>