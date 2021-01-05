+++
draft = false
categories = [
  "tycs",
]
tags = [
  "scheme",
]
comments = false
showcomments = false
showpagemeta = true
date = "2019-01-04T10:29:08-06:00"
title = "Building Lists in Scheme"
+++

## Or, the differences between `append`, `cons`, & `list`

[from sicp](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book-Z-H-15.html#%_sec_2.2)

- **2.26**: Suppose we define `x` and `y` to be two lists:

    ```scheme
    (define x (list 1 2 3))
    (define y (list 4 5 6))
    ```

    What's the output of the following?

    ```scheme
    (append x y)
    ;; (1 2 3 (4 5 6))
    ;; but actually
    ;; (1 2 3 4 5 6)

    (cons x y)
    ;; ((1 2 3) (4 5 6))
    ;; but actually
    ;; ((1 2 3) 4 5 6)

    (list x y)
    ;; (1 2 3 4 5 6)
    ;; but actually
    ;; ((1 2 3) (4 5 6))
    ```

