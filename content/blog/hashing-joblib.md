+++
title = "Hashing Pipelines with Joblib"
date = "2020-05-11T15:15:15"
draft = false
categories = ["til",]
tags = ["joblib","hash",]
comments = false
showcomments = false
showpagemeta = true
+++

For the last six months or so, I've been working on building out the infrastructure for our machine-learning service at work. One thing that had me scratching my head last week was trying to compare two fitted pipelines, trained on what could be the same data. To ensure that I wasn't re-uploading a duplicate fitted pipeline, I wanted to compare the MD5 hashes of the fitted pipelines. Joblib has a [way to do this](https://joblib.readthedocs.io/en/latest/generated/joblib.hash.html#joblib.hash), but I spent way too long trying to find an example of getting it working.

Following the advice that one could blog what would have helped oneself four weeks earlier, I present to you, my past self and current reader, how to use Joblib to get the hash of a fitted pipeline:

```python
joblib.hash(joblib.load('./path/to/pipeline.joblib'))
```

It was unclear to me that the `obj` in the docs for `joblib.hash` was something that had to be loaded in with `joblib.load`. I had tried pretty much everything else up to the point: passing in a string of the path, passing in a `Path` object of the pipeline's path, using `with open('./path') as p` and then trying to pass `p` into `joblib.hash`, and so forth and so forth.

After getting the hash, I take the previous pipeline's filename and the extract the hash from the name; saving the fitted pipeline with its hash in the name is much nicer than having to recalculate the hash before every comparison. Plus, the pipelines aren't user-facing, so the only one getting confused by this mish-mash of letters and numbers is me.

If the two hashes match, I log it, and stop the work. If they're different, though, the new fitted pipeline gets uploaded with its hash appended to its name. Some amount of time later, the process is repeated with another fitted pipeline.
