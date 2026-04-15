# The Vault Template: Shared Infrastructure

A conversation disappears when the window closes. A collaboration needs infrastructure — a persistent, shared context that both you and your AI partner can reference, update, and build on.

This template gives you a minimal but complete structure. It's a folder of markdown files. You can use Obsidian, VS Code, a plain text editor, or just a folder on your desktop. The AI doesn't care about the tool — it cares about the content.

## The Core Files

You need five files to start. Everything else grows from use.

### bootstrap.md

The first thing your AI reads at the start of every session. It answers: who are you, what are we working on, and how do we work together?

```markdown
# Bootstrap

## Who I Am
[Your name, what you do, what matters to you — one paragraph]

## What We're Working On
[Current projects, priorities, what's active right now]

## How We Work Together
[Your preferences, communication style, what you expect]

## Start-of-Session Protocol
1. Read this file
2. Read state-of-play.md for current status
3. Check inbox/ for new items
4. Orient to my opening message and engage
```

Keep it under a page. This is the handshake, not the autobiography.

### state-of-play.md

The living document — what's happening right now. Update it during or after sessions.

```markdown
# State of Play
*Last updated: [date]*

## Active Priorities
1. [Highest priority]
2. [Second priority]
3. [Third priority]

## In Progress
- [Project]: [status, next step]

## Pending Decisions
- [Decision needed]: [context, options]

## Recent Session Notes
- [Date]: [What happened, what was decided, what's next]
```

This file changes most often and pays the biggest dividends — every new session starts current instead of cold.

### visitor-guide.md

Your AI partner's orientation document. See [05-visitor-guide-template.md](05-visitor-guide-template.md).

### decision-log.md

A running record of decisions and reasoning.

```markdown
# Decision Log

## [Date]: [Decision]
**Context:** [What prompted this]
**Options considered:** [What was on the table]
**Decision:** [What we chose]
**Reasoning:** [Why]
**Outcome:** [Fill in later]
```

The most underrated file in the system. When your AI can reference how you've decided things before, future recommendations improve dramatically.

### inbox/ (folder)

A place to drop notes, links, and ideas between sessions. Your AI checks this at session start and incorporates what's there.

## The Key Principle: Everything Connects

Whenever you create a new document, add a `## Related` section at the bottom with links to other relevant files. In Obsidian, these are `[[wikilinks]]`. In plain markdown, regular links.

This matters more than it seems. Your vault is a knowledge graph — every connection makes every other document more findable and useful. Orphan documents are wasted knowledge. The connections ARE the intelligence.

## Growing the Vault

Start with the five core files. As your collaboration deepens, add:

- **Project folders** — one per major project
- **A voice/style reference** — examples of your writing and tone
- **Domain knowledge** — things you know that a general-purpose AI doesn't
- **Templates** — structures you use repeatedly

Don't over-build at the start. Let the structure emerge from actual use.

## Using It With Different AI Systems

This vault is markdown files in a folder. It works with everything:

- **Claude Projects:** Upload core files as project knowledge
- **ChatGPT:** Paste relevant files at conversation start
- **Claude Code / Cursor:** Point them at the folder
- **MCP servers:** Serve files as resources any tool can query
- **Local models:** Drop the folder in the context

The portability is the point. Your context travels with you. No lock-in.

---

*Next: [The Visitor Guide Template](05-visitor-guide-template.md) — write an orientation document for your AI partner.*
