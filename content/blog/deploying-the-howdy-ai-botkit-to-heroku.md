+++
title = "Deploying the Howdy.ai Botkit to Heroku"
date = "2016-01-31T20:11:51"
tags = ["howdy.ai", "botkit", "slack", "heroku", "all of the bots", "amateur-hour devops", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p><em>It wasn&rsquo;t difficult, but like they say, blog about what would have helped your previous self.</em></p>

<p>Presumbaly, you&rsquo;re here because you have a rad bot you built using <a href="https://github.com/howdyai/botkit" target="_blank">Botkit</a>, and you&rsquo;re looking for a bit of guidance on getting it out of your local environment and into the real world using <a href="https://www.heroku.com/" target="_blank">Heroku</a>.</p>

<p><img src="https://dl.dropboxusercontent.com/u/3648990/gifs/bots.gif" alt="bots-gif"/></p>

<p><em>If you&rsquo;re not already familiar with Heroku, or just need a refresher, check out <a href="https://devcenter.heroku.com/articles/getting-started-with-nodejs#introduction" target="_blank">their tutorial on deploying Node.js apps</a>.</em></p>

<p><em>Quick tip: from the command line, using Homebrew on OSX, run <code>brew install heroku-toolbelt</code> and then <code>heroku login</code> to get started.</em></p>

<p>After deploying my working-locally bot using the Heroku tutorial, I kept getting a port error, which <a href="https://github.com/DarrenN" target="_blank">DarrenN</a> mentioned in <a href="https://github.com/howdyai/botkit/issues/13" target="_blank">an issue filed on Github</a>. Following <a href="https://github.com/benbrown" target="_blank">benbrown</a>&rsquo;s <a href="https://github.com/howdyai/botkit/issues/13#issuecomment-165506505" target="_blank">suggestions</a>, I first tried running my bot as a background process [as specified in my Procfile], but that didn&rsquo;t work, likely because I did something wrong. Trying out the second suggestion, I set up a web server using some of Botkit&rsquo;s <a href="https://github.com/howdyai/botkit#controllersetupwebserver" target="_blank">built-in functionality</a>. Works as advertised!</p>

<p>The next time I deploy a bot using Botkit and Heroku [which will likely be sooner than later], this is the process I&rsquo;ll use:</p>

<ul><li><p>Set my <code>token</code> environmental variable on my Heroku app using Heroku&rsquo;s toolbelt: <code>heroku config:set token=all-sorts-of-alphanumeric-biz-from-slack</code></p></li>
<li><p>At the top of my <code>snark-bot.js</code> file, set up the web server:</p></li>
</ul><div class="gist"><a href="https://gist.github.com/chrisbodhi/3db3d71533ce2d2eb2e7" target="_blank">https://gist.github.com/chrisbodhi/3db3d71533ce2d2eb2e7</a></div>

<ul><li>Put together my minimal Procfile, as explained in the Heroku tutorial:</li>
</ul><p><code>web: node snark-bot.js</code></p>

<ul><li>In order to save myself some time, I&rsquo;ll test Heroku locally using a <code>.env</code> file containing my sandbox-Slack token and the <code>heroku local</code> command [more info <a href="https://devcenter.heroku.com/articles/heroku-local" target="_blank">here</a>]. That <code>.env</code> file will look something like this:</li>
</ul><p><code>token=different-sorts-of-alphanumeric-biz-from-my-sandbox-slack</code></p>

<ul><li><p>When everything is working as expected using <code>heroku local</code>, I&rsquo;ll then <code>git push heroku feature-branch:master</code> and check the logs using <code>heroku logs --tail</code> while testing the newly-hosted-on-Heroku bot to confirm that everything still looks good.</p></li>
<li><p>My last step will be merging <code>feature-branch</code> into <code>master</code>, and redeploying to Heroku using <code>git push heroku master</code>.</p></li>
</ul><p>Easy peasy, chicken breezy.</p>