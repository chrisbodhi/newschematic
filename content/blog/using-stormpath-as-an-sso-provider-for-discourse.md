+++
title = "Using Stormpath as an SSO Provider for Discourse"
date = "2015-04-25T16:58:39"
tags = ["discourse", "stormpath", "not a white power band", "sso", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<hr><p><em><a href="https://stormpath.com/" target="_blank">Stormpath</a></em>: User Auth &amp; Management as a Service [UAMaaS?]</p>

<p><em><a href="http://www.discourse.org/about/" target="_blank">Discourse</a></em>: an open source forum, designed for reading</p>

<p><em>SSO</em>: single sign-on; &ldquo;&hellip; a user logs in once and gains access to all systems without being prompted to log in again at each of them.&rdquo; [<a href="https://en.wikipedia.org/wiki/Single_sign-on" target="_blank">src</a>]</p>

<hr><p>As we&rsquo;re moving toward an open beta for the company&rsquo;s new product, web work to promote, support, and disseminate information is ramping up. I was tasked with using Stormpath as the SSO provider for our Discourse forums. If I made a mistake with this configuration, I would be locked out of any settings panel on the Discourse side. The only way to regain access would be <code>ssh</code>-ing into the Discourse box and executing some commands from <code>irb</code>. The catch was that no one knew the address for that hosted box. The solution?</p>

<p><img src="http://i.giphy.com/kNPoWMtuMa8E0.gif" alt="Do as Ru says."/></p>

<p><em>Protip: when testing out the SSO configuration, leave your admin settings open in a separate window and muck around with a different user in a different window</em></p>

<p>Manufactured tension out of the way, let&rsquo;s go over how I implemented this in our Node.js app. First off, we&rsquo;ll need some packages to make this easier: 
<code>npm install express-stormpath --save</code> and <code>npm install discourse-sso --save</code> are good starts. [Read more about express-stormpath <a href="https://github.com/stormpath/stormpath-express" target="_blank">here</a> and discourse-sso <a href="https://github.com/ArmedGuy/discourse_sso_node" target="_blank">here</a>.]</p>

<p>To start out, I was handed a project-already-in-progress. Lots of the basic functionality was already in place for handling the routes and rendering the Jade templates. Since integration of the main app with Stormpath was already handled, we&rsquo;ll be skipping that step and getting right into the SSO action.</p>

<p>Thankfully, Discourse has a good overview of what&rsquo;s needed on their side to get SSO going &ndash; check it out <a href="https://meta.discourse.org/t/official-single-sign-on-for-discourse/13045" target="_blank">here</a> and read through the section, &ldquo;Enabling SSO&rdquo;. After you finish following their instructions, we&rsquo;ll pick up here.</p>

<p>All set? Ok, cool. Let&rsquo;s pop over to that Node.js app. I created a new file <code>discourse.js</code> in the <code>routes</code> directory. In there, I start with pulling in the router and requiring the packages we installed earlier.</p>

<pre><code>
var express         = require('express'),
    router          = express.Router(),
    stormpath       = require('express-stormpath'),
    discourse_sso   = require('discourse-sso');
</code></pre>

<p><em>Once a coworker learned that I like Ruby, my use of this structure finally made sense to him.</em></p>

<p>Then, construct a new SSO object using the <code>sso_secret</code> you added when configuring SSO on the Discourse side: <code>var sso = new discourse_sso('i_love_sso_a_lot');</code>. This <code>sso</code> object contains some helper functions which will be useful for handling the payload coming from Discourse, as we&rsquo;ll see shortly.</p>

<p>Next, set up the endpoint we told Discourse to hit. To my <code>app.js</code>, I added</p>

<pre><code>
var discourse = require('./routes/discourse');
app.use('/sso', discourse);
</code></pre>

<p>Back to <code>routes/discourse.js</code>. Since I set the endpoint in the <code>sso url</code> field to <code><a href="https://my-awesome-site.io/sso/discourse" target="_blank">https://my-awesome-site.io/sso/discourse</a></code> on Discourse, I started by adding a GET route: <code>router.get('/discourse', function(req, res){...});</code>.</p>

<p>Time to get into the SSO action. We&rsquo;ll be receiving two query params from Discourse, <code>sso</code> and <code>sig</code>, so let&rsquo;s start by snagging those</p>

<pre><code>
var payload = req.query.sso,
    sig     = req.query.sig;
</code></pre>

<p>and then put them to work.</p>

<pre><code>
if (req.user &amp;&amp; sso.validate(payload, sig)){
              var nonce = sso.getNonce(payload);
              var userParams = {
                "nonce": nonce,
                "external_id": req.user.href.split('accounts/')[1],
                "email": req.user.email
              };
</code></pre>

<p><em>Hey, it&rsquo;s those helper functions that the <code>sso</code> object provides! And <code>(.split &gt; new RegExp) === true</code>.</em></p>

<p>After we make sure that there&rsquo;s a user who&rsquo;s signed-in, we validate the info from the query params, get the <a href="https://en.wikipedia.org/wiki/Cryptographic_nonce" target="_blank">nonce</a>, and create a <code>userParams</code> object. In it, we send back the nonce to verify with Discourse that it&rsquo;s us, an external ID—which, in this case, is pulled from Stormpath—unique to the user, and the user&rsquo;s email address. Since we&rsquo;re letting Discourse handle all of the username business, we&rsquo;re skipping that and the also-optional name params.</p>

<p>The last part of the process involves packaging all of this info up and sending it back to Discourse.</p>

<pre><code>
var q = sso.buildLoginString(userParams);
res.redirect('https://forums.my-awesome-site.io/session/sso_login?' + q);
window.location.replace('https://forums.my-awesome-site.io');
</code></pre>

<p><em>That last line - hacky? Yup. Now accepting pull requests? Always.</em></p>

<p>Finally, wrap up with the <code>else</code> condition and export the whole thing to use back in <code>app.js</code>, as we saw earlier.</p>

<pre><code>
  } else {
    res.redirect('https://my-awesome-site.io/login');
  }
});

module.exports = router;
</code></pre>

<p>Next time, we&rsquo;ll handle single-sign-out!</p>