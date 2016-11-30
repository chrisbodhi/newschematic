+++
title = "Vagrant and Ubuntu Server 14.04"
date = "2014-04-24T23:14:53"
tags = ["vagrant", "ubuntu14", "apache", "trusty-tahr", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>Trying to apply the instructions for the <a href="http://docs.vagrantup.com/v2/getting-started/index.html" target="_blank">Vagrant tutorial</a> to Ubuntu Server 14.04 Trusty Tahr and I ran into a problem when trying to load up the localhost in order to take a peek at my shared directory. I kept getting an Apache error, which meant that the web server was running locally, just nothing was getting served. Running down the error, I came across this <a href="http://askubuntu.com/questions/452042/why-is-my-apache-not-working-after-upgrading-to-ubuntu-14-04" target="_blank">Ask Ubuntu post</a>. Rather than trying to mess with any conf files, I simply dropped an <code>html</code> directory to <code>/var/www/</code> and <em>voila</em> - it worked.</p>