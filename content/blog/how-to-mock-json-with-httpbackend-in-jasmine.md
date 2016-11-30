+++
title = "How to Mock JSON with $httpBackend in Jasmine"
date = "2014-08-08T00:45:40"
tags = ["angularjs", "json", "jasmine", "karma", "bdd", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<p>There is a lot of information out there on running tests for Angular using Jasmine + Karma. One thing that was tripping me up, though, was being able to access a mock JSON file, rather than trying to hit a server with an HTTP request every test.</p>

<p>Working from this <a href="http://dailyjs.com/2013/05/16/angularjs-5/" target="_blank">code sample</a>, I injected the mock file with the <code>beforeEach</code> call. However, I wasn&rsquo;t able to access the JSON response until I injected the <code>defaultJSON</code> directly into the specific test:</p>

<p><code>it('should get a Success response from Auth', inject( function (defaultJSON) {</code>
<br/>
   <code>expect(defaultJSON.status).toBe('Success');</code>
<br/>
   <code>expect(defaultJSON.object.id).toBe(5);</code>
<br/>
   <code>httpBackend.flush();</code>
<br/><code>}));</code></p>

<p>All green.</p>

<p>[ <a href="https://jasmine.github.io/2.0/introduction.html" target="_blank">more</a> <a href="https://karma-runner.github.io/0.12/index.html" target="_blank">testing</a> <a href="http://scriptogr.am/pploug/post/karma-unit-tests-in-phantomjs" target="_blank">resources</a> ]</p>