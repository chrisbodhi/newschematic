+++
title = "Node.js errors need some work."
date = "2014-02-09T06:37:43"
tags = ["node", "bugsquashing", "bettererrors", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>Writing this in routes/api.js&hellip;</p>
<pre>   exports.posts = function(req, res) {
  var posts = [];

  data.posts.forEach(function(posts, i) {
    posts.push({
      id: i,
      title: post.title,
      text: post.text.substr(0, 50) + '...'
    });
  });
  res.json({
    posts: posts
  });
};

exports.posts = function(req, res) {
  var id = req.params.id;
  if (id &gt;= 0 &amp;&amp; id &lt; data.posts.length) {
    res.json({
      post: data.posts[id]
    });
  } else {
    res.json(false);
  }
};
    
</pre>
<p><em>[d'oh! Note the two `exports.posts`.]</em></p>
<p>&hellip;and then attempting to run the Node server will through a less than helpful error:</p>
<pre>    /Users/b/Desktop/Code/ng-blog/node_modules/express/lib/router/index.js:252
    throw new Error(msg);
          ^
Error: .get() requires callback functions but got a [object Undefined]
    at /Users/b/Desktop/Code/ng-blog/node_modules/express/lib/router/index.js:252:11
    at Array.forEach (native)
    at Router.route (/Users/b/Desktop/Code/ng-blog/node_modules/express/lib/router/index.js:248:13)
    at Router.(anonymous function) [as get] (/Users/b/Desktop/Code/ng-blog/node_modules/express/lib/router/index.js:270:16)
    at Function.app.(anonymous function) [as get] (/Users/b/Desktop/Code/ng-blog/node_modules/express/lib/application.js:414:26)
    at Object. (/Users/b/Desktop/Code/ng-blog/app.js:51:5)
    at Module._compile (module.js:456:26)
    at Object.Module._extensions..js (module.js:474:10)
    at Module.load (module.js:356:32)
    at Function.Module._load (module.js:312:12)
</pre>
<p>Line 52 on the top-mentioned file? It&rsquo;s just calling the function that displays the error. The offending file wasn&rsquo;t listed anywhere in the stack trace. Once I found where I had gone wrong, the error made sense, but damn if I didn&rsquo;t spend close to half an hour finding it.</p>
<p>Sexy new technologies sure are sexy, but they lack the polish of more refined tech, especially where it&rsquo;s needed.</p>