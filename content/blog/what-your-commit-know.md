+++
title = "What Your Commits Know That Your Resume Doesn't"
date = "2026-02-06T14:00:00-05:00"
draft = true
categories = ["programming"]
tags = ["git", "tools", "visualization"]
comments = false
showcomments = false
showpagemeta = true
description = "Building git-log-carver to chart actual work distribution from commit history"
+++

## What Your Commits Know That Your Resume Doesn't

Your resume summarizes three years at a job in a bullet point. Your git history knows the truth: which languages you actually touched, when, and how much of your energy went where. Here's how I made that visible.

## The Gap

Resumes flatten complexity into narrative. Git history is granular, honest, and almost never examined. Why it matters: you have proof of your work distribution, right there in the log.

## Reading the Log

`git log --stat` exists but outputs wall-of-text format. You need to extract what the data actually says: by date, by file extension, by volume. Why Bun: fast startup, TypeScript comfort, streams for large repos without blowing memory.

## The Carver

Core logic: stdin → line-by-line parser → extract extensions → group by date → JSON out.

Show the parsing approach with code walkthrough. Explain why file extensions alone are surprisingly revealing.

## From JSON to Chart

The output feeds directly into Chart.js on the resume page. Each language gets its own colored line, tracking changes over time. The logarithmic scale reveals patterns that raw counts would hide. Visual walkthrough: what the chart actually shows to someone looking at your resume.

## What This Revealed

Honest reflection on what you learn about your own work patterns. Why small, focused tools that output JSON are better than big dashboards. The value of making invisible work visible.

