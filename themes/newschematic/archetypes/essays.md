---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
deck: ""
tags: []
# number: ""        # optional — essay number for the running head
# reading_time: 0   # optional — override computed reading time
---

{{</* drop */>}}
Open with a paragraph that earns its drop cap. The first sentence of an
essay does real work — it sets the voice, names the subject, and gives
the reader a reason to keep going past the scroll fold.
{{</* /drop */>}}

The rest of the essay follows. Use `{{</* break */>}}` for section pauses,
`{{</* plate fig="1" caption="..." */>}}…{{</* /plate */>}}` for diagrams, and
`{{</* pull */>}}…{{</* /pull */>}}` for pull quotes.
