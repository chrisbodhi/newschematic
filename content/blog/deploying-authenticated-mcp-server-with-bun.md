+++
draft = false
date = 2026-01-04T00:00:00Z
title = "Deploying an Authenticated MCP Server with Bun and Cloudflare"
description = "Can you use Bun to deploy Cloudflare's MCP templates? Yes, but cookies are tricky."
categories = ["technical"]
tags = ["mcp", "bun", "cloudflare", "oauth", "claude"]
comments = false
showcomments = false
showpagemeta = true
+++

I had a question this afternoon: can you use Bun to deploy an authenticated MCP server using Cloudflare's templates? The templates are designed for npm, but Bun claims to be a drop-in replacement for Node.js (rundown of [Bun's compatibility is here](https://bun.com/docs/runtime/nodejs-compat)). Let's find out if that's actually true.

BLUF: it nearly works out of the box, but we had to fix some security cookies along the way.

## The Setup

Cloudflare publishes a [reference template](https://developers.cloudflare.com/agents/guides/remote-mcp-server/) for deploying remote MCP servers with GitHub OAuth. It's a solid starting point—Durable Objects for state, KV for OAuth storage, and Server-Sent Events for the MCP protocol.

The documented approach uses `npm create cloudflare@latest`, but I wanted to see if Bun could handle it, since I'd be using Bun for the rest of the product:

```bash
bun create cloudflare@latest my-mcp-server-github-auth \
  --template=cloudflare/ai/demos/remote-mcp-github-oauth
```

Worked perfectly. Bun auto-installed dependencies and created a `bun.lock` file next to the `package-lock.json`. Set up the GitHub OAuth app, added credentials to `.dev.vars`, logged into Cloudflare, and ran:

```bash
bun run start
```

Server started on `http://localhost:8788`. So far, so good.

## The Cookie problem

Testing the OAuth flow with the MCP Inspector revealed the first issue. After authorizing with GitHub, the callback failed:

```
POST /authorize error: OAuthError: Missing CSRF token cookie
```

This is where things got interesting.

### Root cause: Secure cookies on HTTP

The template uses `__Host-` prefixed cookies with the `Secure` flag for CSRF protection. This is the right approach for production (HTTPS), but browsers won't send `Secure` cookies over HTTP—even on localhost.

Here's the problem code in `src/workers-oauth-utils.ts`:

```typescript
export function generateCSRFProtection(): CSRFProtectionResult {
  const csrfCookieName = "__Host-CSRF_TOKEN";
  const token = crypto.randomUUID();
  const setCookie = `${csrfCookieName}=${token}; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=600`;
  return { token, setCookie };
}
```

That `Secure` flag means the cookie never makes it back to the server during local development.

### The Fix: Environment detection

The solution is detecting whether we're running on HTTP (local dev) or HTTPS (production), and conditionally setting cookie flags:

```typescript
function isLocalDevelopment(request?: Request): boolean {
  if (!request) return false;
  const url = new URL(request.url);
  return url.protocol === 'http:' ||
         url.hostname === 'localhost' ||
         url.hostname === '127.0.0.1';
}

export function generateCSRFProtection(request?: Request): CSRFProtectionResult {
  const isDev = isLocalDevelopment(request);
  const csrfCookieName = isDev ? "CSRF_TOKEN" : "__Host-CSRF_TOKEN";
  const token = crypto.randomUUID();
  const secureFlag = isDev ? "" : " Secure;";
  const setCookie = `${csrfCookieName}=${token}; HttpOnly;${secureFlag} Path=/; SameSite=Lax; Max-Age=600`;
  return { token, setCookie };
}
```

This pattern needed to be applied to all the OAuth cookie functions:
- `generateCSRFProtection()` - CSRF tokens
- `validateCSRFToken()` - Token validation
- `bindStateToSession()` - OAuth state binding
- `validateOAuthState()` - State validation
- `addApprovedClient()` - Client approval tracking
- `getApprovedClientsFromCookie()` - Reading approved clients

After updating these functions and passing the request object through the call chain, the OAuth flow worked locally.

## Production deployment

Once local development worked, production deployment was straightforward:

1. **Create production GitHub OAuth app** with the production callback URL
2. **Create KV namespace** for OAuth storage:
   ```bash
   npx wrangler kv namespace create "OAUTH_KV"
   ```
3. **Set production secrets**:
   ```bash
   npx wrangler secret put GITHUB_CLIENT_ID
   npx wrangler secret put GITHUB_CLIENT_SECRET
   npx wrangler secret put COOKIE_ENCRYPTION_KEY
   ```
4. **Deploy**:
   ```bash
   bun run deploy
   ```

The server went live at `my-mcp-server-github-auth.cboette.workers.dev` without any issues.

## Key takeaways

1. **Bun works with Cloudflare's templates.** The create process, dependency management, and Wrangler CLI all worked seamlessly.

2. **Cookie security matters for local development.** Templates optimized for production HTTPS need environment-aware cookie handling for HTTP development.

3. **The `__Host-` prefix requires HTTPS.** This is a browser security feature—you can't use `__Host-` prefixed cookies over HTTP, even on localhost.

4. **Pass context through the call chain.** Environment detection requires access to the request object, which means updating function signatures throughout the OAuth flow.

5. **Test the full OAuth flow early.** We only discovered the cookie issue when actually testing the authorization callback, not when the server started.

## Bonus: Using Claude for this

I worked with Claude Code to debug and fix this issue. Claude identified the cookie security problem, implemented the environment detection pattern, and updated all the necessary functions. The fixes preserved the production security posture while enabling local development—exactly what you want from AI-assisted debugging.

Would I recommend this approach for production? The cookie fixes are solid and maintain security boundaries. But as always, security decisions require understanding your threat model. The template's original approach (production-only, HTTPS-everywhere) is simpler and harder to misconfigure.

That said, being able to test OAuth flows locally makes iteration much faster. Speed wins.
