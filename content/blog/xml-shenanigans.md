+++
title = "XML Shenanigans"
date = "2015-02-09T02:44:31"
tags = ["nokogiri", "xml is like violence", "or is it violins?", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>For the last couple of weeks, I&rsquo;ve been working on a project at work that has involved, among other things, parsing XML and updating existing XML files. Just like every other time I have to deal with XML, I do two things:</p>

<ol><li>Throw up a little bit.</li>
<li><code>gem install nokogiri</code></li>
</ol><p>I found lots of code samples, including in the <a href="http://www.nokogiri.org/tutorials/modifying_an_html_xml_document.html#creating_new_nodes" target="_blank">Nokogiri tutorials</a>, that discussed how to create a new node and then insert a string as the node contents. This would have been ok if my node contents didn&rsquo;t contain more nodes. Nokogiri tried to be helpful and escaped the node contents. So, not very many <code>&lt;</code> and <code>&gt;</code>, but lots of <code>&amp;gt;</code> and <code>&amp;lt;</code>.</p>

<p>D'oh.</p>

<p>I eventually came across this snippet:</p>

<p><code>Nokogiri::XML::DocumentFragment.parse(thing_to_add)</code></p>

<p>It takes an XML-ish string and reformats it, making it ready to insert into the XML document. Take a look at the following gist for a version of the method I used for my assignment:</p>

<div class="gist"><a href="https://gist.github.com/chrisbodhi/0a5a090d986daa0461b2" target="_blank">https://gist.github.com/chrisbodhi/0a5a090d986daa0461b2</a></div>