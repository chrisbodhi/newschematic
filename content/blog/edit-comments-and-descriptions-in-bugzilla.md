+++
title = "Edit Comments and Descriptions in Bugzilla"
date = "2014-07-07T16:28:15"
tags = ["bugzilla", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>I found it a bit baffling that this functionality was not built in, but from an archival perspective, it makes sense. If you need it for your project, there&rsquo;s an easy workaround:</p>

<ul><li>Go to <a href="https://github.com/mozilla/webtools-bmo-bugzilla" target="_blank">this GitHub repo</a> and from the <code>Extensions</code> directory, copy the <code>EditComments</code> directory over to your installation&rsquo;s <code>Extensions</code> directory.</li>
<li>In your Bugzilla directory, from the command line, run <code>./checksetup.pl</code> to build the necessary tables and extra columns and other magical things.</li>
<li>Lastly, in <code>template/en/default/bug/comments.html.tmpl</code>, add the following line to your <code>comment_text</code> div: <code>[% Hook.process('a_comment-end', 'bug/comments.html.tmpl') %]</code>. This provides a link to turn on editing for that field. </li>
</ul><p>Since I don&rsquo;t have memcaching enabled [yet!], I commented out line 229 from <code>extensions/EditComments/Extension.pm</code>. Once I get that memcache going, though, that pound sign is coming right out.</p>

<p>I hope this helps. It took me a while to put this all together, since the information is rather dispersed.</p>

<p>Happy bug tracking!</p>