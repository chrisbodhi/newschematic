+++
title = "assert_equal in MiniTest"
date = "2015-02-15T17:18:00"
tags = ["exercism.io", "ruby", "minitest", "SCIENCE!", ]
categories = ["imported from tumblr", "text", ]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

<div class="gist"><a href="https://gist.github.com/chrisbodhi/b7b10f5e428088fa38da" target="_blank">https://gist.github.com/chrisbodhi/b7b10f5e428088fa38da</a></div>

<blockquote>
  <p>@chrisbodhi I also find it difficult to understand how the test cases are passed. I&rsquo;ve checked them and they do, but in my opinion <code>test_name_sticks</code> should fail as every call to name will append a new random name to the previous one instead of returning the same string. For example, if we run a simple test:</p>
  
  <p><code>robot = Robot.new</code>
  <br/><code>2.times{puts robot.name}</code>
  <br/>
  we get:
  <br/><code>QF658</code>
  <br/><code>QF658YV199</code>
  <br/>
  making it clear that the test should fail. —<a href="http://exercism.io/franrodalg" target="_blank">franrodalg</a></p>
</blockquote>

<p>If I&rsquo;m understanding the question, it looks like that <code>assert_equal</code> calls <code>robot.name</code> twice; since the two return values are different, the test should fail. I wasn&rsquo;t sure how that method works, so I peeked at the <a href="http://ruby-doc.org/stdlib-2.0.0/libdoc/minitest/rdoc/MiniTest/Assertions.html#method-i-assert_equal" target="_blank">source here</a> [thankfully, it&rsquo;s also written in Ruby]. The method takes two values: the expected output and the actual output. It uses the system&rsquo;s <code>diff</code> tool to compare the two arguments and then proceeds based on the value returned by the <code>diff</code>.</p>

<p>I haven&rsquo;t used a lot of the Unix tools before, so I fired up <a href="http://pryrepl.org/" target="_blank">pry</a> and copied in my Robot class. I created a new robot instance [you can see in the returned object that the <code>@name</code> value is instantiated as an empty string] and used <code>%x</code> to run system [Unix] commands in the REPL, passing in the string-interpolated <code>robot.name</code> twice.</p>

<p><code>robot = Robot.new</code><br/><code>=&gt;#&lt;Robot:0x007fff134761b0 @name=""&gt;</code><br/><code>%x(diff -u #{robot.name} #{robot.name})</code><br/><code>diff: XP677XA768: No such file or directory</code><br/><code>diff: XP677XA768: No such file or directory</code><br/><code>=&gt;""</code><br/></p>

<p>I initially thought the <code>diff</code> would compare <code>robot.name</code> as a static object [something like <code>nombre = robot.name</code> and then <code>diff -u #{nombre} #{nombre}</code>], so I was surprised to see that the method gets called twice. However, it seems that the methods are running before the <code>diff</code> tool does its thing. I&rsquo;m willing to wager that the object ID is the same for both return values. So, even though the return value doesn&rsquo;t meet the requirements for a robot name [two letter, three numbers], the  value does persist and the test passes.</p>

<p>Find the entire discussion <a href="http://exercism.io/submissions/f12650b29ed940488d133b293d74ce73" target="_blank">here</a>.</p>