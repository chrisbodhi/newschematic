+++
title = "gempm: Sharing JavaScript Code Between Rails and Node.js apps"
date = "2016-12-10T02:44:31"
tags = ["rails", "gem", "nodejs", "pipeline architecture", "browserify"]
categories = ["rails", "javascript", "sharing is caring"]
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

## Background

Here at OwnLocal, we've built lots of Rails apps and added lots of Ruby code to those apps. As our products and tools have grown organically over the years, our systems have become more opaque and, in some cases, more brittle.

In the last quarter of 2016, my team was tasked with automating away a large portion of our bread and butter: writing parsers to [extract, transform, and load](https://en.wikipedia.org/wiki/Extract,_transform,_load) data from text files sent to us by our partners on a daily basis. Studying the requirements, it seemed to me that the proposed data flow&mdash;passing in a text file along with a partner-specific configuration for how the system should translate that data&mdash;resembled a pure function: we'd always get the same output from the same input, no side-effects. When I pitched the idea that we build a greenfield project, rather than bolting more functionality onto a Rails app we plan to sunset next year, Drew told us to go for it.

As our new [pipeline](https://en.wikipedia.org/wiki/Pipeline_(software)) started to take shape, Chris Allen started to build out the front-end tool that support engineers would use to create those partner-specific configurations in the form of JSON. One requirement for that front-end tool was to allow the support engineer to view the results of their config as they were writing it; keeping the feedback cycle tight.

It quickly became apparent that we'd need to share code between our pipeline&mdash;a graph run on AWS Lambdas&mdash;and our existing Rails app&mdash;deployed on EC2 and managed with OpsWorks. So, I got to work finding a way for us to share ~isomorphic~ universal JavaScript code between projects and contexts.

## Research and Requirements

I started looking into Browserify and Webpack as two potential ways to load JavaScript functions, initially written targeting a Node.js build environment, into a simple [read: framework-less] frontend on a Rails app. Once I started talking to folks on other teams, the question of loading the code into the Rails asset pipeline surfaced.

To share the code between projects, I started with a new Github repo that would contain the JavaScript code in a structure that mimicked the Rails directory. Also in that repo, we'd have a `gemspec` file and a `package.json`, so that we could point both apps at the same repo, and they would just pull what they needed. We'd have a single source to update and maintain, which addressed the main requirement for this part of the project.

In need of a good name for this repo, I consulted various thesarauses and online sources. I ended up calling the repo `gempm`. You know, like npm for gems. And Node.js modules. _I'll show myself out._

## Implementation

To prove out the concept, I started out by writing some placeholder code in this new repo.

```
function testing() {
  return 'hola, testing function';
}
```

Just as if I was writing a Ruby gem, I added this code to a JavaScript file, `file-name.js`, which lived under the directory, `app/assets/javascripts`. After filling out a basic `gem_name.gemspec` file in the repo root, I ran `gem build gem_name.gemspec` in the project root to generate the first iteration of the gem, suitable for usage in Rails projects.

As far as the `gem_name.gemspec` file went, I followed the example provided by the [Ruby gem docs](http://guides.rubygems.org/make-your-own-gem/) for the most part. One thing I did differently, though, was to add a little bit of code to `lib/version.rb` so we'd only have to update the version number in the `package.json` to maintain parity between the gem and Node.js package.

```
# lib/version.rb
module GemName
  require 'json'
    pkg = JSON.parse(File.read(File.join(__dir__, '../package.json')))

    VERSION = pkg['version']
end
```

```
# gem_name.gemspec
$:.push File.expand_path('../lib', __FILE__)

require 'version'

Gem::Specification.new do |s|
  ...
  s.version = GemName::VERSION
  ...
end
```

To test out the first part of the concept, I had to get the gem into my Rails app:

- From the `gempm` directory, run `gem build gem_name.gemspec` to build the latest version of the gem.
- In the Gemfile for the Rails app, add a line to the end that contains the name of the gem and its local path, like `gem 'gem_name', path: 'path/to/gempm'`.
- Run `bundle install` then start the Rails app
- Open up the developer console in the browser. The `testing()` function can be invoked right there, confirming that Rails has `file-name.js` in its asset pipeline.

Next, in the Node.js app:

- Run `npm install --save path/to/gempm`, which copies the `gempm` code to the Node.js app's `node_modules` directotry
- To confirm, start the Node.js REPL, `require` the `gempm` package, and invoke the `testing` function.

#### Almost There

For simple JavaScript functions, this setup would be sufficient for sharing code across stacks. However, we're dependent on some third-party libraries written for Node.js. It could have been possible to find analogs that ran in the browser, but attempts to go down that path quickly devolved into a mess of branching code. I rolled back that attempt and got back to [Browserify](http://browserify.org/). It turned out that, with a few flags, Browserify easily solved our problem.

My first attempt at running the basic Browserify bundling command from their homepage, `browserify lib/file-name.js -o app/assets/javascripts/bundle.js`, resulted in a file I could load into both the Node.js and Rails apps, but not use with Rails: the code was bundled, but the functions were not exposed. A little bit of research yielded a solution:

```
browserify lib/file-name.js --standalone myModule > app/assets/javascripts/bundle.js
```

And then, in the `gem_name.gemspec` file, I just updated the `s.files` line:

```
s.files = ["app/assets/javascripts/bundle.js"]
```

This way, the functions I wanted to use in the Rails app could be accessed as properties on `myModule`; invoking the `testing` function was as simple as calling `myModule.testing()` from anywhere in the front-end code.

## Drawbacks

The biggest drawback for the approach we've taken here mostly has to do with our deployments being somewhat cumbersome; there are a lot of moving parts that have to be babysat in order to get changes into our apps.

Also, having to create build processes instead of just requiring a file creates more overhead while demanding that more tooling be installed and kept up to date on our machines. 

Lastly, because we use CircleCI for building our apps, we had to jump through some hurdles to [allow Circle access to more than one private repo on GitHub](https://circleci.com/docs/github-security-ssh-keys/#machine-user-keys) for building the Node.js app. For the Rails app, though, we're able to simply cache the latest version of the gem with `bundle package --all` before committing.

All of these inconveniences, though, are fairly minor when considering the pains associated with attempting to maintain the same code aross projects, rather than just a version number. 

## Plans for the Future

One thing to explore as our engineering department moves to new architectures is how to apply lessons learned from this project to other efforts. This might look like something techincal&mdash;a generator that creates a directory structure and skeleton files&mdash;or it may simply be an extension of this blog post for guiding other engineers around hurdles in building a shared JavaScript library.























