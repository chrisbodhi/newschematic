+++
title = "org-mode shortcuts for literate programming"
date = "2020-11-07T14:30:56"
draft = false
categories = ["org-mode",]
tags = ["reference",]
comments = false
showcomments = false
showpagemeta = true
toc = false
+++

Recently, I had occasion to [complete some coding exercises](https://bradfieldcs.com/csi/apply/). Since there was some exposition involved, I wanted to take advantage of some of the affordances for literate programming provided by `org-mode` in Emacs.

I won't get too much into the definition and benefits of literate programming here. My intent is to create a reference of some of my favorite `org-mode` commands that, in practice, I don't get to use that often; but, would like to have collected in one spot.

### Embedding

#### Images

The caption is added with `#+CAPTION: caption text goes here`, placed on a line above the image
path; the name for the image is done the same way.

```
#+CAPTION: take your pick – based on work by Renee French
#+NAME: gopher goin'
[[https://blog.golang.org/gopher/usergroups.png]]
```

The image in the link on the last line could be to a file on the local file system.

It'll look like this:

![image embed be like](/img/org-mode-img-embed-example.jpeg)

#### An entire file

Let's say you want to embed an entire file in your output, and use the syntax highlighting for that file type. It's as simple as using `#+INCLUDE:`, the path to the file, and then `src` plus the source code language:

```
#+INCLUDE: "path/to/file.go" src go
```

Quickly jump to the file with `C-c '`, if you like.

#### Part of a file

More likely, you'll want to embed part of a file. It's similar to the previous command, but with a `:lines` argument followed by which lines to add:

```
#+INCLUDE: "some/dir/README.org" :lines "4-"
```

No number after the `-` will import all lines until the end of the file.

#### REST calls

This is useful when testing an API that's in development. I've definitely been bitten by accidentally using a newly-outdated `curl` command from my command line history, and wondering why the response didn't match what I expected.

After installing [ob-restclient.el](https://github.com/alf/ob-restclient.el), it can be used like:

```
#+begin_src restclient :results value code :exports both
POST http://localhost:8080/api/check
Content-Type: "application/json"

{
  "ipAddress": "0.0.0.1"
}
#+end_src
```

Kicking off the request with `C-c C-c` will embed the response below it, looking like:

```
#+RESULTS:
#+begin_src restclient
{
  "ipAddress": "0.0.0.1",
  "isNewVisitor": true
}
#+end_src
```

### Exporting

#### Front matter

```
#+TITLE: Bradfield CSI application
```
becomes both the `<title>` in the exported HTML, as well as an `h1` tag with the `class` set to `"title"`.

```
#+AUTHOR: Chris Boette
```
becomes a `<meta>` tag in the exported HTML, with the `name` attribute set to `"Chris Boette"`, as well as a `<p>` tag with the `class` set to `"author"`.

```
#+DATE: Friday 6 November 12020
```
becomes a `<p>` tag with the class `date`.

```
#+HTML_HEAD: <style>body { padding: 1rem; } header h1 { font-size: 1.75rem; } h1 { font-size: 1.5rem; } img { max-width: 28rem; } </style>
```
This one is fun. It allows for the setting of various tags directly in the `<head>` tag. I chose to augment the existing CSS with some more modern styling conventions.
