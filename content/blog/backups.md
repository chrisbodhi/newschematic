+++
title = "Backups"
date = "2014-02-27T07:30:37"
tags = []
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>I copied my `gem list` and `brew list` outputs to text files in Dropbox today [is the next step writing a script that installs the listed packages when called?]. I then did some sort of nasty copy-and-paste job on my Sublime Text 2 settings, putting them into the Reboot folder, too. Then I came across this response to a <a href="http://stackoverflow.com/questions/11365948/how-to-save-restore-sublime-text-2-configs-plugins-to-migrate-to-another-compute" target="_blank">question</a> on Stack Overflow. It&rsquo;s so much nicer &amp; will continue to backup automagically. It&rsquo;s another one of those too-rare instances where technology makes life easier. </p>
<blockquote>
<div class="vote"><span class="vote-count-post "><br/>I just set up a good solution for this, it requires dropbox. I am currently using this to sync plugins and settings across ~5 different sublime installs on windows, linux, osx, and a few vm&rsquo;s.</span></div>
<div class="post-text">
<ul><li>
<p>Step 1: use <a href="http://wbond.net/sublime_packages/package_control" target="_blank">PackageControl</a> to manage all your plugins, its awesome.</p>
</li>
<li>
<p>Step 2: Add a &ldquo;Sublime&rdquo; directory to your root drop-box directory (I replicated the full directory structure for the hell of it, <code>{DropBox}/Sublime/Packages/User</code>). Make sure sublime is closed, and move the contents of <code>{SublimeRoot}/Packages/User</code> in to the dropbox directory you just made. Delete <code>{SublimeRoot}/Packages/User</code>, and replace it with a symlink that points to <code>{DropBox}/Sublime/Packages/User</code>.</p>
</li>
</ul><p>Use this same process on every computer where you use sublime, it accomplishes 2 things.</p>
<ul><li>
<p>1) The contents of your <code>User/</code> directory are synced, so all your custom settings are the same across machines.</p>
</li>
<li>
<p>2) Every time PackageControl starts up, it checks the <code>Package Control.sublime-settings</code> in your <code>User/</code> directory. If if finds a plugin that should be installed according to the settings, but isn&rsquo;t actually installed, it automatically installs it, no questions asked.</p>
</li>
</ul><p>Setting up another computer with this solution simply requires sublime and package control to be installed, then just delete the <code>{SublimeRoot}/Packages/User/</code> directory and point it to the copy in dropbox with a symbolic link. Next time you fire up sublime, package control will automatically install all your plugins.</p>
<p><em><strong>Creating the symbolic links</strong></em>: execute from the <code>{Sublime}/Packages</code> directory</p>
<ul><li><strong>Windows</strong>: <code>mklink /D .\User C:\Users\[username]\Dropbox\Sublime\Packages\User</code></li>
<li><strong>Linux/OSX</strong>: <code>ln -s {DropboxRoot}/Sublime/Packages/User ./User</code></li>
</ul></div>
</blockquote>