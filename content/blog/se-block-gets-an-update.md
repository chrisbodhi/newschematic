+++
title = "SE Block Gets an Update"
date = "2015-06-28T14:47:43"
tags = ["stack overflow", "stack exchange", "chrome extension", "se block", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>This week, I released an update to <a href="https://chrome.google.com/webstore/detail/se-block/ffpkepieaocfchmcokenleighplnifjh" target="_blank">SE Block</a>, the Chrome extension that removes some of the cruft from the otherwise-excellent Stack Exchange pages. I had initially struck upon the idea for the extension shortly after I started <a href="http://gamesalad.com" target="_blank">my last job</a>. Spending a lot of time on Stack Overflow, I found myself getting distracted by whatever was trending on the rest of the network—analysis of characters in Gibson’s Bridge Trilogy? efforts to build supercapacitors using graphene sheets? mining the bowels of the English language to satisfy an itch for the perfect word choice? #relevant to this blog’s interests #productivity drain</p>

<p>I spun up a Chrome extension scaffold using the <a href="https://github.com/yeoman/generator-chrome-extension" target="_blank">Yeoman generator</a>, and got to work. Since I did this more than <a href="http://codeblocks.tumblr.com/post/87891549210/se-block" target="_blank">a year ago</a>, most the process has been forgotten. One thing I remember I decided was to do the selection of elements on the page without relying on jQuery or any other third-party library. So, out came <code>getElementById</code> and its ilk. More specifically,</p>

<div class="gist"><a href="https://gist.github.com/chrisbodhi/029e53b94160a4e1b3c4" target="_blank">https://gist.github.com/chrisbodhi/029e53b94160a4e1b3c4</a></div>

<p>For each ID and class, again and again and again. This is something I know can be done more efficiently, and it’ll gnaw at me until I fix it, but that’s neither here nor there.</p>

<p>As a user requested on the Chrome App Store page, Stack Exchange added a new couple of divs as they rolled out their Careers site. So, I updated my extension to account for the new divs, recognizing the irony in my comments in the script:</p>

<div class="gist"><a href="https://gist.github.com/chrisbodhi/c836dcdbf034f7548f0b" target="_blank">https://gist.github.com/chrisbodhi/c836dcdbf034f7548f0b</a></div>

<p>Maybe it was because it was late at night when I started, but I initially ran into troubles when trying to delete all of the divs with the <code>everyonelovesstackoverflow</code> class name. First, I learned that <code>document.getElementsByClassName</code> doesn’t return an actual array, but rather an array-like object. Oh, ok. Seems that “array-like” means it’ll support selection by index, but not all of those fun and helpful JavaScript Array methods; <code>forEach</code>, for instance. Next, I dusted off the part of my brain that writes <code>for</code> loops.</p>

<div class="gist"><a href="https://gist.github.com/chrisbodhi/8edbac8e9427c5f16b2b" target="_blank">https://gist.github.com/chrisbodhi/8edbac8e9427c5f16b2b</a></div>

<p>Turned out that just dusting off that part of my brain wasn’t enough, because I kept getting this wrong; it took me a minute to catch it: the length of <code>recruiters</code> changes as objects are removed from the array[-like object]. So, it would never remove all of the items, leaving some divs behind [not realizing that Ad Block was also taking care of some of those divs didn’t help my troubleshooting!].</p>

<p>After some experimenting in the console, I finally took the approach of working from the end to the start, rather than from position zero:</p>

<div class="gist"><a href="https://gist.github.com/chrisbodhi/9110bc09a42cbae1e293" target="_blank">https://gist.github.com/chrisbodhi/9110bc09a42cbae1e293</a></div>

<p>I pushed the changes to the Chrome App Store and they went live later that evening. I think this project warrants a rewrite—if you beat me to it, <a href="https://github.com/chrisbodhi/se-block" target="_blank">pull requests are welcome</a>!</p>