+++
title = "On Inquisitive Variable Names"
date = "2019-07-24T14:30:56"
draft = false
categories = ["reflections", "workplace", "writing code",]
tags = ["metaskills"]
comments = false
showcomments = false
showpagemeta = true
+++

They say that code should read like well-written prose, and that code is written to be read by people&mdash;it's only incidental that machines do something with whatever we create.

To those ends, prefixing the names of variables of the boolean type with "is" or "has" or another interrogative word has the effect of leading the reader to expect an answer&mdash;"yes" or "no," or in the parlance of the language, `true` or `false`. This communicates to the reader that the variable represents a boolean, and primes them for approaching the next part of the expression as something that may or may not happen. 

Asserting a condition in the variable name (`somethingIsSomethingElse`) is a statement that does not invite inquisition; it is a fact that is not to be challenged, an immutable condition. The reader expects the variable to be communicating truthfully&mdash;"this is an assertion of fact, and it should not be considered to ever be false." This is deceptive in the case of variables that could contain the value of `false`!

