+++
comments = false
showcomments = false
showpagemeta = true
date = "2016-12-18T14:25:20-06:00"
title = "Adding node.js test coverage from CircleCI to Code Climate"
draft = false
categories = ["javascript"]
tags = ["circleci", "code climate", "testing", "node.js"]

+++

- install [istanbul](https://github.com/gotwarlost/istanbul) & [codeclimate-test-reporter](https://github.com/codeclimate/javascript-test-reporter) in your dev dependencies: `npm install --save-dev istanbul codeclimate-test-reporter`
- add to circle.yml:

```
general:
  artifacts:
    - "coverage"

test:
  post:
    - CODECLIMATE_REPO_TOKEN=$CODECLIMATE_REPO_TOKEN ./node_modules/.bin/codeclimate-test-reporter < coverage/lcov.info
``` 

- In Code Climate, get the test reporter token from https://codeclimate.com/repos/YER_PROJECT_ID/coverage_setup and take it to the "Env Var" section of your Circle CI project settings page, like https://circleci.com/gh/USER_NAME/PROJECT_NAME/edit#env-vars -- add a variable with a `name` of `CODECLIMATE_REPO_TOKEN` and `value` of the test reporter token from Code Climate.

- Update your `test` command in your `package.json` from

```
"test": "NODE_ENV=test ./node_modules/.bin/jasmine"
```
to

```
"test": "NODE_ENV=test ./node_modules/.bin/istanbul cover --include-all-sources ./node_modules/.bin/jasmine"
```

Now, when CircleCI runs your test suite, it'll generate a coverage report using istanbul and then send that report to Code Climate.
