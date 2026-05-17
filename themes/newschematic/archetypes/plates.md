---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
deck: ""
fig: ""                     # figure number — e.g. "1", "i", "2a"
caption: ""                 # italic caption below the figure
image: ""                   # path to the image, e.g. "/images/plates/orbit.png"
alt: ""                     # alt text for accessibility
tags: []
---

<!--
  If `image` is set above, the image is rendered in the plate frame and this
  body content shows below as commentary. If `image` is empty, put your SVG
  or other figure content directly here and it will render in the frame.
-->

Optional commentary on the figure — what it depicts, how it was made, what it means.
