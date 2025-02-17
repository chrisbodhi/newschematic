---
title: "Debugging Claude's MCP Server with Nix"
date: 2025-02-17T12:00:00-06:00
draft: false
tags: ["nix", "claude", "debugging", "mcp", "development"]
---

# Debugging Claude's MCP Server with Nix

When I first started using Claude with my Nix-managed development environment, I ran into an interesting issue. The default examples for starting a local MCP (Model Context Protocol) server with `npx` were giving me cryptic error messages whenever I tried to restart Claude:

```
Error: spawn ENOENT
```

## Investigation

My first step was to check the Claude logs at `~/Library/Logs/Claude/mcp*.log` using `tail`. I also used the MCP inspector tool (which is quite snazzy, by the way) to verify that my API keys and tools were configured correctly. Running the tools manually with `npx` in my terminal worked fine, so what was going on?

After digging through some issues reported by Windows users, I realized that `ENOENT` indicates that an executable couldn't be found. This led me to compare my local `PATH` with what Claude was seeing.

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

This confirmed my suspicion: my shell's `PATH` was different from Claude's, and the `npx` executable wasn't available because it was being managed by Nix.

The solution was to modify how we call `npx` by extending the `PATH` in the MCP server configuration:

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