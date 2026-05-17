---
title: "schema-ui"
date: 2026-02-10
draft: false
deck: "Express middleware that generates LLM-driven HTML interfaces from JSON schemas."
status: "shipped"
stack: ["TypeScript", "Bun", "Express", "Claude API"]
repo: "https://github.com/chrisbodhi/schema-ui"
tags: ["typescript", "llm", "bun"]
---

schema-ui sits in front of an Express route and, given a JSON schema describing an expected response shape, generates an HTML interface for a user to fill in that shape — with all the reasonable-default behaviour you'd want an LLM to figure out on your behalf.

## Motivation

I kept writing the same glue code: take a schema, ask the model to render a form, validate the input, coerce types, handle errors. schema-ui is that glue, once.

## Approach

A single `schemaUI()` middleware factory. Pass it a schema and it returns a handler that renders, validates, and submits.
