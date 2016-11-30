+++
title = "Getting Going with React, Part II: On to Development"
date = "2015-03-01T22:07:20"
tags = ["react.js", "new schematic", "coding puns", "portfolio rebuild", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p><em>part one <a href="http://codeblocks.tumblr.com/post/111688707280/getting-going-with-react" target="_blank">here</a> | completed portfolio site redesign <a href="http://newschematic.org" target="_blank">here</a></em></p>

<p>Rather than jumping into a full web application, I decided to start small with something I could finish in one sitting. I already had designed my portfolio site to use card-like visual components for each project. Having read over this article on <a href="http://facebook.github.io/react/docs/thinking-in-react.html" target="_blank">thinking in React</a>, I figured a rebuild would be a natural fit.</p>

<p>Step one was to dump all of the content into a JSON file, which I could use instead of an actual database. This approach made sense because of the small amount of content, the lack of updates to the site [working on this!], and my lack of interest in setting up &amp; maintaining a database through my shared web hosting service.</p>

<p>Next up, which is probably the most important part of any project: coming up with funny variable names that are both descriptive and part of a larger theme. As Adam Anderson, of <a href="https://q2ebanking.com/" target="_blank">Q2</a>, once noted in a lecture, &ldquo;Half of coding is naming things.&rdquo; I decided to build on the card theme: each project would be displayed in a <code>Card</code>; the code to iterate over all of the content and return the complete card component would be the <code>Deck</code>; and the code that retrieved the data from the JSON file would be the <code>Dealer</code>.</p>

<p><img src="http://media2.giphy.com/media/ObZEj9rGiC7Ru/200_s.gif" alt="Batman gets it. He gets everything."/></p>

<p>The roles and links at the bottom of the card didn&rsquo;t fit in a way that I liked, so I broke them out into their own components. Sadly, I couldn&rsquo;t think of names that would both be descriptive and fit with the theme. The bonus of moving them into their own components, however, was that I got some more experience writing code in JSX.</p>

<h4>Dealer Component</h4>

<div class="gist"><a href="https://gist.github.com/chrisbodhi/b542f089515831cf0d66" target="_blank">https://gist.github.com/chrisbodhi/b542f089515831cf0d66</a></div>

<h4>Deck Component</h4>

<div class="gist"><a href="https://gist.github.com/chrisbodhi/354b57385d9c6834d050" target="_blank">https://gist.github.com/chrisbodhi/354b57385d9c6834d050</a></div>

<h4>Card Component</h4>

<div class="gist"><a href="https://gist.github.com/chrisbodhi/a6b99ac9fd98baa84dfc" target="_blank">https://gist.github.com/chrisbodhi/a6b99ac9fd98baa84dfc</a></div>

<h3>A Couple of Things</h3>

<ul><li>I had a script that I called at the bottom of my original HTML page to ensure that all of the cards were the same height. With the new configuration utilizing React components, leaving the script in the same position meant that it got called before the cards finished loading, which meant nothing happened. So, on a tip from the same coworker who started this whole mess, I added <code>componentDidMount</code> to the <code>Card</code> component and called the script from in there.</li>
<li>I needed to add certain classes to certain cards in order to get the  titles to sit in the middle of the cards and block out the appropriate amount of border. Introducing <code>React.addons.classSet</code>. In each card&rsquo;s chunk of JSON, I added a boolean attribute (for example, <code>markov: true</code>) and in the process of building the array of classes to add to each card, I dropped in a few checks for truthiness:
<code></code></li>
</ul><pre>
[other stuff],
'small-6 medium-12': this.props.data.markov,
'small-5 medium-9': this.props.data.mars,
[continuing with stuff]
</pre>

<p>
Probably a bit whack, but it worked. Suggestions for improvement, though, are always welcome!</p>

<h3>Parting Thoughts</h3>

<p>React.js is a nifty library and I want to get in some more time playing with it. I&rsquo;m currently working on a side project using <a href="http://d3js.org/" target="_blank">D3.js</a> and it&rsquo;s been tempting to try to find a way to shoehorn some React into it. However, I realize that it would be overkill and jQuery is going to be more than enough for my app&rsquo;s needs. For now, I&rsquo;ll have to settle for late night binge-coding sessions.</p>