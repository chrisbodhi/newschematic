+++
title = "Debugging Claude's MCP Server with Nix"
date = "2025-02-17T12:00:00-06:00"
draft = false
tags = ["nix", "claude", "debugging", "mcp", "development",]
comments = false
showcomments = false
showpagemeta = true
toc = false
+++

# Debugging Claude's MCP Server with Nix

When I first started using Claude with my Nix-managed development environment, I ran into an interesting issue. The default examples for starting a local MCP (Model Context Protocol) server with `npx` were giving me cryptic error messages whenever I tried to restart Claude:

```
Error: spawn ENOENT
```

## Investigation

My first step was to check the Claude logs at `~/Library/Logs/Claude/mcp*.log` using `tail`. I also used the MCP inspector tool (so snazzy) to verify that my API keys and tools were configured correctly. Running the tools manually with `npx` in my terminal worked fine, so what was going on?

After digging through some issues reported my Windows brethren, I realized that `ENOENT` indicates that an executable couldn't be found. This led me to compare my local `PATH` with what Claude was seeing.

## The Solution

To debug this, I used a shell script (suggested by Claude) to save the `PATH` and environment variables at MCP startup:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "/bin/sh",
      "args": [
        "-c",
        "echo $PATH > /tmp/claude_path.txt; env > /tmp/claude_env.txt"
      ]
    }
  }
}
```

After checking the output saved in these files, my suspicion was confirmed: my shell's `PATH` was different from Claude's, and the `npx` executable wasn't available because it was being managed by Nix.

The solution was not to install `npx` globally, but to modify how we call `npx` by extending the `PATH` in the MCP server configuration:

```json
"filesystem": {
  "command": "/bin/sh",
  "args": [
    "-c",
    "PATH=/run/current-system/sw/bin:$PATH exec npx -y @modelcontextprotocol/server-filesystem /Users/b/Desktop /Users/b/Documents /Users/b/Downloads"
  ]
},
```

## Key Takeaways

1. When using Nix-managed tools with Claude's MCP server, you need to ensure the correct `PATH` is set in your MCP configuration
2. The `ENOENT` error usually indicates a missing executable in your `PATH`
3. Debugging environment variables at startup can help identify PATH-related issues
4. Adding Nix's system binary path (`/run/current-system/sw/bin`) to the `PATH` can resolve executables not being found

This solution allows Claude to work seamlessly with Nix-managed development environments while maintaining the isolation and reproducibility that Nix provides.

* * *

## Bonus feature

I wanted to make a public note about this solution, so that others might benefit from my digging. I did a brain dump into Claude about what I did and discovered. It then created this blog post as a Markdown file and committed it to [the repo where I store my posts](https://github.com/chrisbodhi/newschematic). _It got me 95% of the way there on the first try._ I saw this, and literally laughed out loud with joy. What it missed was some formatting of the front matter, which I was alerted to after CI failed to generate the new post. I was able to quickly fix it after comparing this new post to an old post's structure.

For posterity, my prompt-dump:

```
I'd like to add a new blog post about how I got Claude working with npx installed with Nix. My blog is in source control, on Github, at chrisbodhi/newschematic. The issue I was seeing was that using the default examples to start a local MDP server with npx were giving me cryptic error messages when restarting Claude: "Error: spawn ENOENT". I inspected the logs at ~/Library/Logs/Claude/mcp*.log with tail. I used the MCP inspector tool (so snazzy) to check that the API keys and tools worked as expected. I installed ran the tools manually with npx in my terminal. After digging through some issues from my Windows brethren and realizing that ENOENT means an executable wasn't being found, I compared my local PATH to what Claude was seeing. I used a slick shell script that Claude provided to save the PATH and env at MCP startup: json{
  "mcpServers": {
    "filesystem": {
      "command": "/bin/sh",
      "args": [
        "-c",
        "echo $PATH > /tmp/claude_path.txt; env > /tmp/claude_env.txt"
      ]
    }
  }
} That confirmed my shell's PATH different, and that my npx executable wasn't available, because it was being managed by Nix. Claude then suggested a different way of calling npx by extending the PATH. json"filesystem": {
      "command": "/bin/sh",
      "args": [
        "-c",
        "PATH=/run/current-system/sw/bin:$PATH exec npx -y @modelcontextprotocol/server-filesystem /Users/b/Desktop /Users/b/Documents /Users/b/Downloads"
      ]
    },
```
