+++
title = "Getting Going with React"
date = "2015-02-21T21:04:30"
tags = ["react", "curly braces", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<h4>Part I: Before I Typed a Single Curly Brace or Semicolon</h4>

<p>When I first saw some JSX code in a tutorial on React, I immediately poo-pooed the whole library: &ldquo;What is that, HTML in JavaScript? Facebook, grrr! I&rsquo;m no wizard, but that&rsquo;s a terrible combination of concerns! Also, it&rsquo;s ugly and please give me back my Jade, <em>immediately</em>.&rdquo; But, as time went on and as one of my co-workers continued his incessant gushing about React, I finally broke down and gave it a spin. And I really, really liked it.</p>

<blockquote>
  <p>&ldquo;HTML in JavaScript?&rdquo;</p>
</blockquote>

<p>That&rsquo;s what it looks like, but it&rsquo;s really not. In reality, it&rsquo;s a way of asking the JSX transpiler to later create some HTML that looks like it. A small distinction, yes, but for some reason, learning that distinction helped assuage some concerns.</p>

<blockquote>
  <p>&ldquo;Faceook, grrr!&rdquo;</p>
</blockquote>

<p>Nothing will change this. I take solace in the fact that FB—as a self-serving organization that treats its users as cattle—will one day go the way of AOL, who once thought they ruled the internet. [Note the lack of disparagement for the individuals involved with the company.]</p>

<blockquote>
  <p>&ldquo;a terrible combination of concerns!&rdquo;</p>
</blockquote>

<p>This had to be pointed out to me: Angular actually has tightly-coupled views and controllers. Change the ID of a button in the view? Gotta update that ID in the controller. With React, the scripting and the output are all right there, in the same <code>React.createClass</code>.</p>

<blockquote>
  <p>&ldquo;it&rsquo;s ugly and please give me back my Jade&rdquo;</p>
</blockquote>

<p>There&rsquo;s no getting around the fact that it is ugly. As far as having to sully my code with <code>&lt;</code> and <code>&gt;</code>, <a href="https://github.com/duncanbeevers/jade-react" target="_blank">there</a> <a href="https://github.com/jadejs/react-jade" target="_blank">are</a> <a href="https://github.com/mikepb/jade-react-compiler" target="_blank">options</a> to explore.</p>

<p>So, with all of this in mind, I put on <a href="https://www.youtube.com/watch?v=z5e7kWSHWTg" target="_blank">this video</a> from React.js Conf the other night at around 9pm, and ended up working until 2am on my first React project. Blast.</p>

<h5>A Note on Testing</h5>

<p>Testing doesn&rsquo;t seem to be as integral to development as it is in Angular. Take, for instance, the <a href="https://docs.angularjs.org/tutorial" target="_blank">Angular tutorial</a> that walks one through the building of an app for phone shopping. Testing makes up a <a href="https://docs.angularjs.org/tutorial/step_02" target="_blank">significant portion</a> of that experience. With React, though? Not so much — the test utilities are <a href="http://facebook.github.io/react/docs/test-utils.html" target="_blank">included only in an add-on</a>. Even though there&rsquo;s research that concludes that <a href="http://devchat.tv/ruby-rogues/184-rr-what-we-actually-know-about-software-development-and-why-we-believe-it-s-true-with-greg-wilson-and-andreas-stefik" target="_blank">TDD doesn&rsquo;t result in less buggy or more quickly-developed code</a>, getting a test suite to green triggers an endorphin release in my brain that I really quite enjoy.</p>

<p><em>Next time: my first React project - a rebuild of <a href="http://newschematic.org" target="_blank">my personal website</a>. Or maybe I&rsquo;ll go through the React + Jade tools. Or maybe I&rsquo;ll build an actual dang app.</em></p>