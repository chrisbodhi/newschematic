---
title: "The request lifecycle"
date: 2026-01-22
draft: false
deck: "A small schematic of what happens between a tapped button and a returned response."
fig: "iii"
caption: "The request lifecycle, in five labeled stages. Auth is the stage that bites."
tags: ["diagrams", "web"]
---

<svg viewBox="0 0 600 200" width="100%" style="display:block;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </marker>
  </defs>

  <rect x="20" y="70" width="100" height="60" fill="none" stroke="currentColor" stroke-width="0.5" rx="4"/>
  <text x="70" y="95" text-anchor="middle" font-family="Iowan Old Style, serif" font-size="14" fill="currentColor" font-style="italic">Client</text>
  <text x="70" y="112" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" fill="currentColor" opacity="0.7">A</text>

  <path d="M120 100 L160 100" stroke="currentColor" stroke-width="0.5" marker-end="url(#arrow)"/>

  <rect x="160" y="70" width="100" height="60" fill="none" stroke="var(--ns-oxblood)" stroke-width="0.5" rx="4"/>
  <text x="210" y="95" text-anchor="middle" font-family="Iowan Old Style, serif" font-size="14" fill="var(--ns-oxblood)" font-style="italic">Auth</text>
  <text x="210" y="112" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" fill="var(--ns-oxblood)" opacity="0.8">B</text>

  <path d="M260 100 L300 100" stroke="currentColor" stroke-width="0.5" marker-end="url(#arrow)"/>

  <rect x="300" y="70" width="100" height="60" fill="none" stroke="currentColor" stroke-width="0.5" rx="4"/>
  <text x="350" y="95" text-anchor="middle" font-family="Iowan Old Style, serif" font-size="14" fill="currentColor" font-style="italic">Route</text>
  <text x="350" y="112" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" fill="currentColor" opacity="0.7">C</text>

  <path d="M400 100 L440 100" stroke="currentColor" stroke-width="0.5" marker-end="url(#arrow)"/>

  <rect x="440" y="70" width="100" height="60" fill="none" stroke="currentColor" stroke-width="0.5" rx="4"/>
  <text x="490" y="95" text-anchor="middle" font-family="Iowan Old Style, serif" font-size="14" fill="currentColor" font-style="italic">Handler</text>
  <text x="490" y="112" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" fill="currentColor" opacity="0.7">D</text>

  <path d="M490 130 Q490 170 70 170 Q70 150 70 130" fill="none" stroke="currentColor" stroke-width="0.5" stroke-dasharray="3 3" marker-end="url(#arrow)"/>
  <text x="280" y="188" text-anchor="middle" font-family="Iowan Old Style, serif" font-size="12" fill="currentColor" opacity="0.7" font-style="italic">response</text>
</svg>

A small commentary on what makes the auth stage the one to watch: it's the only stage in the lifecycle where the *correct* outcome can change based on external state you don't control. The other four stages are, structurally speaking, pure functions of the request.
