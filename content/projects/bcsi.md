+++
title = "Bradfield Computer Science Intensive"
draft = false
date = "2021-09-09T09:09:09-06:00"
categories = ["projects","cs"]
tags = ["asm", "memory hierarchy",]
comments = false
+++

_Or, Everything That Had to Happen, Is Happening, and Will Happen When You Submit a Form_

A year-long course from the fine folks who run [https://teachyourselfcs.com](https://teachyourselfcs.com), but more in-depth, more accountable, and more over Zoom. Eight modules leading up to a capstone project, where we are expected to build something we would not have been able to create previously, whether because of a series of missing pieces of knowledge or because our foundation knowledge was shaky due to leaky abstractions.

## Pre-work

Six different subjects, though with my limited time, I definitely over-indexed on [learning C](https://github.com/chrisbodhi/bcsi/tree/trunk/c). The [Go project](https://github.com/chrisbodhi/bcsi/tree/trunk/go) was fun after working with C&mdash;the lineage is noticeable, to say the least, and the task more meaty. With sufficient planning, I rarely felt stuck.

## Introduction to Computer Systems

There's this loop that's constantly running, humming along at four instructions a nanosecond (that's 4,000,000,000 instructions a second), and it's at the heart of every key pressed, packet received, and pixel painted by a modern computer. Fetch, decode, execute, repeat. How data is stored, where is it stored when it's used, and what form does that data take? Caches and cache lines (64 bits in a cache line on modern systems). Understanding how a computer is really programmed, and cutting through the abstractions to the level of what the machine does with machine code&mdash;this is what we're here for.

* [Writing a simulated VM](https://github.com/chrisbodhi/bcsi/blob/trunk/intro-to-computer-systems/intro-01/prework/vm.go) to fetch, execute, and decode instructions
* [A program written in Assembly](https://github.com/chrisbodhi/bcsi/blob/trunk/intro-to-computer-systems/assembly/sum_to_n.asm)
* [Some optimized C code](https://github.com/chrisbodhi/bcsi/blob/trunk/intro-to-computer-systems/optimization/pagecount.c) and [thoughts on said code](https://github.com/chrisbodhi/bcsi/blob/trunk/intro-to-computer-systems/optimization/responses.org)

