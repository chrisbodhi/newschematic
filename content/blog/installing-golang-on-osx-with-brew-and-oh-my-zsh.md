+++
title = "Installing Golang on OSX with Brew and oh-my-zsh"
date = "2016-10-11T02:25:22"
tags = ["golang", "til", "homebrew", "zsh", "dang that took a long time", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p><code>brew install go</code> worked well, as expected. However, at the end of the installation, the notes suggest I add <code>GOROOT</code> to my path:</p>

<blockquote>
  <p>You may wish to add the GOROOT-based install location to your PATH: <code>export PATH=$PATH:/usr/local/opt/go/libexec/bin</code></p>
</blockquote>

<p><img src="https://media.giphy.com/media/2RHswlsG1f3tm/giphy.gif" alt="seems legit"/></p>

<p>Buuuuut, it didn&rsquo;t work. After trying out some different iterations, I was reminded when <code>ls</code>-ing through the surrounding directories that <code>/usr/local/opt/go/...</code> was aliased because Homebrew. <a href="http://stackoverflow.com/a/33624443/2276791" target="_blank">This Stack Overflow answer</a> reinforced my hunch. So, I updated my <code>.zshrc</code>:</p>

<p><code></code></p>

<pre>
export GOPATH="/Users/IceKing/Code/go"
export GOROOT="/usr/local/Cellar/go/1.7.1/libexec"
export PATH="$PATH:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.npm-packages/bin:$GOROOT"
</pre>



<p>and it worked.</p>

<p>Background: <a href="http://brew.sh/" target="_blank">homebrew</a>, the missing package manager for osx | <a href="http://ohmyz.sh/" target="_blank">oh my zsh</a> shell | <a href="https://golang.org/" target="_blank">golang</a></p>