+++
title = "Too Many Content Requests"
date = "2015-07-08T15:01:22"
tags = ["react.js", "troubleshooting", "too many cooks reference?", "learnin'", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>During a phone screen recently, the CTO of the company was going through my <a href="http://newschematic.org" target="_blank">portfolio site</a>. He checked the browser&rsquo;s network console and noticed that the site — a page built with React components — was sending multiple requests a second for data from a JSON object [the object serves as the page&rsquo;s datastore because spinning up a database in this instance would be overkill]. A learning moment!</p>

<p>I revisited the <a href="https://facebook.github.io/react/tips/initial-ajax.html" target="_blank">React docs</a> and the <a href="https://github.com/chrisbodhi/newschematic/commit/4ead7ca82888f024528be2447ae989357508379c" target="_blank">code for the components</a>. With a better understanding of React, the issue was quickly apparent: every time the <code>Dealer</code> component was rendered, an AJAX request for <code>data.json</code> fired. Which, just to get static data, was a lot.</p>

<p>My fix involved changing the AJAX request to fire only once the <code>Dealer</code> component loaded. Luckily, React has a built-in event <code>componentDidMount</code> for such an occasion. Just swapped out the names, added an extra check for mounting, and then I deleted the call to the AJAX function in the <code>render</code> portion of the component. Problem solved!</p>

<p><em>earlier write-up on my first impressions using React is <a href="http://codeblocks.tumblr.com/post/111688707280/getting-going-with-react" target="_blank">here</a></em></p>