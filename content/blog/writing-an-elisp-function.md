+++
title = "Writing Emacs-Lisp, or elisp"
date = "2021-07-14T06:06:06"
draft = false
categories = ["programming", "emacs-lisp",]
tags = ["til",]
comments = false
showcomments = false
showpagemetadata = true
+++

In the much-vaunted style of literate programming, here&rsquo;s an emacs-lisp function I wrote this afternoon.

The motivation was to convert a shell alias I added this morning, which counts the number of Zettelkasten notes I&rsquo;ve written that day. (&ldquo;Jesus, him, too?&rdquo; Yes, dear reader, I&rsquo;m afraid that this is one trend I haven&rsquo;t managed to dodge forever, but my adoption has been cautious and deliberate.)

    alias today_count="fd $(date -u +"%Y-%m-%d") ~/org/zd | wc -l"

Using the lovely [fd](https://github.com/sharkdp/fd) utility, I find all files in my Zetteldeft directory, which start with today&rsquo;s date. Then, I pipe that output to `wc -l` to get the count. Easy peasy, chicken breezy; took me about two minutes to write. *ETA: Turns out this doesn&rsquo;t work as an alias; the date isn&rsquo;t recalculated every time the alias is called.*

But, in the spirit of staying focused inside of one tool (where I&rsquo;m already writing my notes), I wanted to convert the alias to an emacs-lisp function I could call from anywhere in Emacs. And in the spirit of learning in public, here&rsquo;s an annotated walk-through.

We start with importing a sequence library to use later for filtering entries.

    (require 'seq)

Next, we declare our function, with no variables. It&rsquo;s not a stretch, though, to imagine specifying which date (or dates!) I would want a count from.

    (defun zd/today-count ()

After that, gasp, a document string, which the elisp linter was very insistent on me adding. Does the culture influence the tooling, or does the tooling influence the culture?

    "Return the number of notes created today. Depends on notes saved with the format YEAR-MONTH-DAY."

Then, we use the `interactive` special form. This is necessary for the requirement to be able to call the function from anywhere using `M-x`.

    (interactive)

Next up, there&rsquo;s a function for returning today&rsquo;s date in a string, formatted in such a way as to match up with how our filenames are constructed. This started out as a variable, but it turns out that `defvar` will assign a value to a variable *only once*. I suspect there&rsquo;s a more semantically-correct way to do this, but this is what we have for now.

    (defun get-today ()
      (format-time-string "%Y-%m-%d"))

Here, I&rsquo;m making use of that `seq` library that was imported at the very start. An anonymous function takes each filename (as a string), and returns a non-nil value if the filename matches a regular expression built from today&rsquo;s date.

    (defun get-today-files (day)
      (seq-filter
        (lambda (f) (string-match-p (regexp-quote day) f))
        (directory-files deft-directory)))

Lastly, in a convoluted line, we print a string to the Messages buffer, which includes the date and number of notes written so far!

    (message "It's %s; you've written %d notes so far." (get-today) (length (get-today-files (get-today)))))

