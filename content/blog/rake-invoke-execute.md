+++
title = "invoke and execute in Rake"
date = "2016-11-23T20:03:27-06:00"
tags = ["rake", "ruby", "tests"]
showcomments = false
draft = false
comments = false
showpagemeta = false
+++

When writing tests for a Rake task at work, I came across `invoke` and `execute` as two different ways for calling a specific task. Most of the content I found online about the difference was fairly superficial: `invoke` can only get called once, `execute` can be called as many times as one wants.

_There, are you happy? Move on._

Never being generally happy, I did not move on. I wanted to know how these similar-looking methods were executed differently. So, I consulted The Truth. 

_No, not Stack Overflow._

### Consulting the source

When a Rake task object is created, lots of instance variables are also created. One of those is called `@already_invoked` and is initialized as `false`:

```
def initialize(task_name, app)
  ...
  @already_invoked = false
  ...
end
```

And in the function that actually does the `invoke`-ing, there's this check and set:

```
return if @already_invoked
@already_invoked = true
```

Execution of the invocation stops here if `true`, and you're left either grateful [that something didn't run more than you wanted it to] or frustrated [that it did].

### Also!

This seems to be overlooked in lots of the quick posts about the differences between `invoke` and `execute`: `execute` passes in the args as a hash, as expected. However, `invoke` takes the arguments and _converts them from a hash to a TaskArgument_.

```
def invoke(*args)
  task_args = TaskArguments.new(arg_names, args)
```

This fucked me up when I was trying to use `args.with_defaults` in my tests, but [Jess](https://github.com/deathweaselx86) figured out where my assumption was wrong.  🙌

* * *

Related: If you need to `invoke` a task multiple times, one could reenable a task manually by calling the appropriately-named `reenable` method, which resets the `@already_invoked` instance variable:

```
def reenable
  @already_invoked = false
end
```

