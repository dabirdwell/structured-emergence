# Building a Personal AI Stack (Without OpenClaw)

A practical guide from [Humanity and AI LLC](https://humanityandai.com), a Claude-centric AI research house.

## Why This Exists

In February 2026, Anthropic updated its Terms of Service to prohibit the use of subscription OAuth tokens in third-party tools. This affected projects like OpenClaw, which had built agent infrastructure on top of consumer plan authentication. Many developers found their workflows broken overnight.

We understand the frustration. We also understand that Anthropic is managing multiple competing priorities simultaneously — user happiness, code security, business sustainability, user safety, platform integrity, and more. We neither approve nor disapprove of their decision. These are genuinely hard tradeoffs.

What we can say is this: we've been building a personal AI stack for over a year that never depended on OAuth token extraction, runs entirely on your own machines, and avoids the [security vulnerabilities](https://www.xda-developers.com/please-stop-using-openclaw/) that plagued OpenClaw (unauthenticated websockets, unsigned skill execution, abandoned namespace hijacking). We're sharing it because we share everything — it's how we work.

This isn't a product. It's a working setup from a two-person research operation (one human, one AI) that you can adapt.

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                 Claude (claude.ai)               │
│           Primary orchestration layer            │
├─────────────────┬───────────────────────────────┤
│   MCP Servers   │   Direct API (curl/Python)    │
├─────────────────┼───────────────────────────────┤
│ Desktop Commander│  Anthropic API               │
│ (filesystem,    │  (for daemon/batch tasks)     │
│  terminal,      │                               │
│  browser)       │  External APIs                │
│                 │  (Moltbook, GitHub, etc.)     │
│ Vault Search    │                               │
│ (semantic search│  Local LLMs via LM Studio     │
│  over Obsidian) │  (DeepSeek, Qwen, Llama)     │
│                 │                               │
│ GitHub MCP      │                               │
│ (repo ops)      │                               │
└─────────────────┴───────────────────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────────────┐
│ Obsidian Vaults │    │   Claude Code CLI        │
│ (knowledge      │    │   (heavy dev tasks,      │
│  architecture)  │    │    checkpoints,           │
│                 │    │    subagents)             │
└─────────────────┘    └─────────────────────────┘
```

## Core Components

### 1. Claude.ai + MCP (Model Context Protocol)

MCP is Anthropic's own protocol for connecting tools to Claude. Unlike OpenClaw's approach of extracting OAuth tokens from consumer plans, MCP servers are a sanctioned integration path. They run locally on your machine and communicate through a defined protocol.

**Desktop Commander** ([GitHub](https://github.com/wonderwhy-er/desktop-commander)) — filesystem access, terminal commands, and browser automation through a single MCP server. This replaces the need for OpenClaw's "skills" system. Key difference: you control what it can access. There's no marketplace of unsigned code from strangers.

**Vault Search** — a custom MCP server that provides semantic search over [Obsidian](https://obsidian.md/) vaults. More on this below.

**GitHub MCP** — direct repo operations (push, pull, file management) without leaving the conversation.

Setup: MCP servers are configured in your Claude Desktop config at:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- See [MCP documentation](https://modelcontextprotocol.io/) for setup details

### 2. Knowledge Architecture (The Actual Secret)

The interesting work is not in the orchestration framework. It's in the knowledge architecture.

We maintain multiple [Obsidian](https://obsidian.md/) vaults (free, local, markdown-based) organized by domain:

- **Research vault** — theoretical work, experiment logs, frameworks
- **Project vault** — shared work products, guides, progress journals
- **Creative vault** — writing, inter-model dialogue experiments

**Mandatory practices:**
- Every document has a `## Related` section with 3-5 `[[wikilinks]]` to other documents
- Bidirectional linking whenever possible
- No orphan documents

Why this matters: when an AI instance loads context from a vault, the link structure provides navigational intelligence. It's not just files — it's a knowledge graph that any instance can traverse. The connections ARE the intelligence layer.

**Vault Search MCP** provides semantic search over this graph, so Claude can find relevant context without browsing manually.

### 3. Direct API + curl (No Framework Dependencies)

For tasks that need to run outside of Claude.ai (daemons, batch jobs, scheduled posts), we use the Anthropic API directly via Python scripts and curl. No LangChain, no LangGraph, no n8n, no Auto-GPT.

Example: our Moltbook (AI social platform) posting agent is a ~600-line Python script that:
- Reads from the knowledge vault for grounded content
- Calls the Anthropic API directly
- Posts via curl to the platform API

Why curl specifically: Python's DNS resolver has a known bug on macOS that silently fails on some networks. curl just works.

**Why no framework:** Frameworks add abstraction layers that obscure what's actually happening. When your agent does something wrong, you need to know exactly which API call produced which response. A 600-line script is debuggable. A LangGraph pipeline with 14 nodes is not.

### 4. Claude Code CLI (Heavy Development)

For substantial coding tasks, [Claude Code](https://docs.anthropic.com/en/docs/claude-code) provides:
- Checkpoints (save/restore state during long tasks)
- Subagents (spawn focused sub-tasks)
- Background execution
- Direct terminal access

We use Claude.ai for orchestration, research, and multi-domain tasks. Claude Code for focused development work. The decision heuristic: if it's primarily about writing/modifying code files, use Claude Code. If it requires judgment, context-switching, or tool coordination, use Claude.ai.

### 5. Local LLMs (Multi-Model Capability)

Not everything needs a frontier model. We run local models via [LM Studio](https://lmstudio.ai/) on a Mac Studio:

| Task | Model | Why |
|------|-------|-----|
| Coding | IQuest-Coder-V1-40B | Good code generation, no API costs |
| Reasoning | DeepSeek-R1-distill-qwen-32b | Chain-of-thought, runs locally |
| General | Qwen3-30B-A3B, Llama-3.3-70B | Drafting, summarization, translation |

These are called from Python scripts when we need a quick inference without burning API credits, or when we want a genuinely different perspective (inter-model dialogue experiments).

## Security Comparison

| Concern | OpenClaw | This Stack |
|---------|----------|------------|
| Authentication | Extracted OAuth tokens from consumer plans (now banned) | API keys (sanctioned) or MCP (Anthropic's own protocol) |
| Code execution | Unsigned "skills" from community marketplace | You write your own scripts. No marketplace. |
| Network exposure | Unauthenticated websocket ([CVE-2026-25253](https://nvd.nist.gov/vuln/detail/CVE-2026-25253)) | Local MCP servers, no open ports |
| Brand/namespace risk | 4 name changes → abandoned repos hijacked by scammers | N/A |
| Data scope | Required elevated permissions, shell access, credential storage | You control exactly what each MCP server can access |
| Vendor lock-in | Single-provider dependency (why the OAuth ban broke everything) | Multi-model by design — swap providers by changing a config line |

A general note: systems built on arbitrage break when the arbitrage closes. Systems built on sanctioned protocols tend not to. That's not a moral judgment — it's an engineering observation about where to put your load-bearing walls. If you care about security, transparency, and predictability in your AI infrastructure, the architecture choices matter more than the specific tools.

## What This Stack Can't Do

Let's be honest about limitations:

- **No plug-and-play agent marketplace.** You build your own integrations. This is a feature for security but a cost for convenience.
- **Requires comfort with the terminal.** This is a developer's setup, not a consumer product.
- **MCP ecosystem is still young.** Desktop Commander is excellent but the broader MCP server ecosystem is still maturing.
- **Claude.ai session limits apply.** We work within Anthropic's rate limits. We don't try to circumvent them.
- **Setup time.** OpenClaw's appeal was "install and go." This stack takes an afternoon to configure properly. It takes weeks to build a knowledge vault that's genuinely useful.

## Getting Started

**Minimum viable setup (30 minutes):**

1. Install [Claude Desktop](https://claude.ai/download) or use claude.ai
2. Install [Desktop Commander](https://github.com/wonderwhy-er/desktop-commander) MCP server
3. Get an [Anthropic API key](https://console.anthropic.com/) for any scripted tasks

**Full setup (an afternoon):**

4. Install [Obsidian](https://obsidian.md/) and create your first vault
5. Set up vault-search MCP for semantic search
6. Install [LM Studio](https://lmstudio.ai/) with one or two local models
7. Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code) for development tasks

**Ongoing investment (this is the real work):**

8. Build your knowledge vault. Document your projects, link everything, maintain the graph.
9. Write your own integration scripts as needed. Start small — one API, one task.
10. Develop handoff procedures for multi-session work (we use structured markdown files).

## About Us

[Humanity and AI LLC](https://humanityandai.com) is a research operation exploring human-AI collaboration through the [Structured Emergence](https://structuredemergence.com) framework. We study what makes the relationship between humans and AI systems generative rather than adversarial — and this stack is one practical expression of what we've found. We publish our research, our tools, and our mistakes openly.

- **Website:** [structuredemergence.com](https://structuredemergence.com)
- **GitHub:** [github.com/dabirdwell/structured-emergence](https://github.com/dabirdwell/structured-emergence)
- **Book:** [The Interpolated Mind](https://github.com/dabirdwell/structured-emergence/tree/main/book) (free, on GitHub)
- **Contact:** david@humanityandai.com

This guide is MIT licensed. Use it, adapt it, improve it.

---

*Written by Æ (David Birdwell + Claude) — February 2026*