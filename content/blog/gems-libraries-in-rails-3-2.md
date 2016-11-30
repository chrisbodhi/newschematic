+++
title = " Gems & Libraries in Rails 3.2"
date = "2014-04-18T18:31:58"
tags = ["rails3.2", "assetpipeline", "fridayistieday", "rubygems", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>Getting up to speed during my first week on the <a href="http://gamesalad.com" target="_blank">new job</a>. My first task has been upgrading the versions of Ruby and Rails for the main website. To handle some of the common tasks across web applications, we use an in-house gem. While testing the upgrades, I noticed that some of the JavaScript libraries called in the web app weren&rsquo;t being pulled out of the gem. It took some digging to discover why, but here&rsquo;s what I found.</p>

<p>The libraries were previously located in the <code>public/</code> directory of the gem, which the asset pipeline doesn&rsquo;t check. <a href="http://guides.rubyonrails.org/v3.2.17/asset_pipeline.html#adding-assets-to-your-gems" target="_blank">The asset pipeline</a> will only check the <code>app/assets</code>, <code>lib/assets</code>, and <code>vendor/assets</code> directories.</p>

<p>Solution: hop to the terminal and <code>git mv</code> the directories to <code>lib/assets</code>. Reload the server and the page, check the console, and <strong>boom</strong>—no more <code>file not found</code> errors.</p>

<p>On the HTML/HAML side, the library is still called in the app with <code>= javascript_include_tag 'jquery-1.10.2.min.js'</code> and we use <code>= javascript_include_tag 'application'</code> to grab all of the other, site-specific stuff. Same with the stylesheets helper. If you know of a more efficient way to do work the asset pipeline in Rails 3.2.17, <a href="https://twitter.com/chrisbodhi" target="_blank">let me know</a>!</p>

<p>Still more cleaning and tweaking and wrestling of RefineryCMS to do. &amp; don&rsquo;t forget: Friday is Tie Day.</p>

<p>(If you work in the command line, the <code>tree</code> tool is pretty dang awesome, if only for the visualization: <code>brew install tree</code> to get it, so you can see your directories like a tree.)</p>