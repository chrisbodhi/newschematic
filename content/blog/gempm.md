+++
title = "gempm"
date = "2016-12-10T02:44:31"
tags = ["rails", "gem", "nodejs", "pipeline architecture"]
categories = []
draft = false
comments = false
showcomments = false
showpagemeta = true
+++

## Background

Here at OwnLocal, we've built lots of Rails apps and added lots of Ruby code to those apps. As our products and tools have grown organically over the years, our systems have become more opaque and, in some cases, more brittle.

In the last quarter of 2016, my team was tasked with automating away a large portion of our bread and butter: writing parsers to extract, transform, and load data from manifest files sent to us by our partners on a daily basis. Studying the requirements, it seemed to me that the proposed data flow&mdash;passing in a manifest file along with a partner-specific configuration for how the system should translate that data&mdash;it seemed to me that, at a high-level, each step resembled a pure function: we'd always get the same output from the same input. When I pitched the idea that we build a greenfield project, instead of bolting more functionality onto a Rails app we plan to sunset next year, Drew told us to go for it.

As the manifest pipeline started to take shape, Chris Allen started to build out the front-end tool that support engineers would be using to create those partner-specific configurations in the form of JSON. One requirement for that tool was to allow the support engineer to view the results of their config as they were writing it. It quickly became apparent that we'd need to share code between our pipeline&mdash;a graph run AWS Lambdas&mdash;and our existing Rails app&mdash;deployed on EC2 and managed with OpsWorks. So, I got to work finding a way for us to share isomorphic Javascript code between projects and contexts.

## Research and Requirements

I started looking into Browserify and Webpack as two potential ways to load Javascript functions, initially written targeting a Node.js build environment, into a fairly simple [read: framework-less] frontend on a Rails app. Once I started talking to folks on other teams, the question of loading the code into the Rails asset pipeline surfaced.

Eventually, I settled on creating a single Github repo that would contain the Javascript code in a `src` directory. Also in that same repo, we'd have a Gemfile and a Node.js package, so that we could point both apps at the same repo, and they would just pull what they needed. We'd have a single source to update and maintain, which ended up the largest&mdash;and possibly only&mdash;requirement for this part of the project.

After lots of thesaurus consultation, I ended up calling the repo `gempm`. You know, like npm for gems. And Node.js modules.

## Implementation

Referencing an internal gem of ours, I started out by getting our tool configs in place: Code Climate, linters, a CircleCI build file, and of course, a README. _[note for our project managers: getting a ticket to make a `gempm init` command would be super rad]_ 


## Drawbacks

- redeploying apps to propagate changes made at the `gempm` level
- having to create build processes instead of just `require` file
- 
