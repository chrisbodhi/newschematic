+++
draft = false
date = "2014-04-20T10:52:50-05:00"
title = "Markov Q. Aurelius"
categories = ["projects"]
tags = ["ruby", "sinatra", "twitter bot", "solo"]
+++

### Philosopher for the 21st Century

![Was once hosted on Heroku: Markov Aurelius, the Philosopher King](/img/mqa.png)

[on twitter](https://twitter.com/markovQaurelius) | was once on heroku | [source code](https://github.com/chrisbodhi/stoic_generator)

_developer, designer_

Uses Marcus Aurelius's "Meditations" and a Markov Chain to generate philosophical quotes that are posted to Twitter daily.

_Tech Stack_

- Ruby on a [GitHub Action](https://github.com/chrisbodhi/stoic_generator/blob/trunk/.github/workflows/generate-tweet.yml)
- Twitter & marky_markov Ruby gems
- Daily post through [another GitHub Action](https://github.com/chrisbodhi/stoic_generator/blob/trunk/.github/workflows/send-tweet.yml)
