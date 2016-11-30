+++
title = "this. & Model, singular & [Mark] Haml"
date = "2013-12-11T06:02:34"
tags = ["makersquare", "js this", "rails model", "mark haml", "lolcommits", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>Day 19 of MakerSquare.</p>
<p>Frontend: We started with a much-needed refresher in Javascript. After Gilbert had us all repeat &ldquo;&lsquo;this&rsquo; points to the object calling the function&rdquo; not once, but twice, I decided to write it down. It could be important. <em>&lt;/understatement&gt;</em></p>
<p>As an aside, will the next generation understand jokes referencing closing HTML tags after we all start using Haml and other templating engines in the Future?</p>
<p>Anyway, we broke for lunch before getting into `for` loops. Met up with a friend of mine who wants to develop a game to teach kids programming concepts. Luckily, I could follow along with his idea and even understood the funny stories he told about his CS undergrad experiences in the lab. At the very least, I&rsquo;ll be a much better guest at cocktail parties after this program is over. </p>
<p>Backend: We got back into ActiveRecord and associations in Rails. During the hackathon, we almost used multiple tables and started to dive into `has_many` and `has_many` relationships [versus `has_many` and `belongs_to`, which is all we&rsquo;ve learned so far]. Thanks to our Saturday night tech pivot, we didn&rsquo;t have to worry about any of that quite yet. </p>
<p>Back to Rails. I thought I had understood what gets pluralized and when in Rails. But when I was stumped by my pair&rsquo;s question of why models were singular when reference in the Rails console, we had to get a response. The first part of my takeaway was</p>
<blockquote>
<p>Model != database</p>
</blockquote>
<p>Since learning about models and databases/tables on the same day last week, I&rsquo;ve been using the words interchangeably. If they all meant the same thing, then why, in the Rails console, did we write `Movie.all`, and then pop over to Sublime Text to examine the &ldquo;movies&rdquo; table in the schema?</p>
<p>As I grokked it, the model isn&rsquo;t the whole database, it&rsquo;s a representative portion of the whole database, like a row. A complete [or incomplete] row can tell you what the column headings are and what data type is accepted. From this information, it&rsquo;s possible to build out the database and ready it for accepting content. <em>hashtag rails magic</em></p>
<p>I worked on the Haml lesson at home, even though I continuously thought of <a href="http://media2.policymic.com/7d3c596ba13c0290330200e0b8eee001.jpg" target="_blank">this guy</a> whenever I read the name of the templating language. I already hit some snags with not indenting a table&rsquo;s body and trying to find reliable documentation for writing `form_for` forms. I get a badge for those things, right? <em>incomplete documentation achievement unlocked </em></p>
<p>That&rsquo;s enough of that. I&rsquo;m going to outline [read: stare at] my hackathon write up. Hope to see yinz at the holiday party tomorrow, <em>especially</em> the bots that follow this blog.</p>
<blockquote>
<p>As an aside, I&rsquo;m going to strongly encourage the use of <a href="http://mroth.github.io/lolcommits/" target="_blank">this thing</a> during the next hackathon. You know, for the yuks.</p>
</blockquote>