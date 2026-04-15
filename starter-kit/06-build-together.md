# Build Together: A Catalog of Tools

Once you and your AI partner know each other — once you've done the bootstrap, built the vault, written the visitor guide — you're in a position to build things together.

You don't need to know how to code. Describe what you need, explain why, and your AI partner can help you build it. That's what collaborative alignment looks like in practice.

Not everyone needs the same toolkit. Read through, see what resonates, and ask your partner to help you build the ones that matter.

---

## Knowledge Graph / Hypergraph

**What it is:** A map of the connections between everything you know and work on. Documents, ideas, people, projects — all linked in a traversable network.

**Use cases:**
- You're a researcher tracking how ideas connect across hundreds of papers. The graph shows relationships you'd never find by searching.
- You run a small business and want to see how clients, projects, and vendors relate — and where the gaps are.

**Why it matters:** Flat folders hide relationships. A knowledge graph surfaces them. Your AI can traverse the graph to find connections you'd miss, suggest links you haven't made, and identify clusters of related work.

**Ask your AI:** *"I have a folder of markdown files about [domain]. Can you help me build a knowledge graph that maps the connections between them?"*

---

## Temporal Awareness Layer

**What it is:** A system that tracks how your knowledge and decisions evolve over time. Not just what you know — when you learned it, how it changed, what it replaced.

**Use cases:**
- You want to see how your thinking on a topic changed over six months — the evolution, not just the current state.
- You need to trace why a project decision was made and what you knew at the time.

**Why it matters:** Context without history is just a snapshot. This gives you the movie. Your AI can understand not just what's true now, but how you got here — which makes its recommendations dramatically better.

**Ask your AI:** *"I want to add time-awareness to my vault. When I update a document, I want to track what changed and when. Can you help me build a versioning system?"*

---

## Semantic Search

**What it is:** Finding things by meaning, not just keywords. Search for the *concept* of "trust in distributed systems" and find every note that discusses it, even if those exact words never appear.

**Use cases:**
- You have 500 notes and need to find everything related to a concept, across projects and time periods.
- You're prepping a talk and need every relevant idea you've ever written down, including the ones you forgot.

**Why it matters:** A vault is only as useful as your ability to find what's in it. Keyword search misses semantic relationships. Semantic search finds them.

**Ask your AI:** *"I want to search my notes by meaning, not just keywords. Can you help me set up semantic search using embeddings?"*

---

## MCP Server (Personal Context API)

**What it is:** A server that makes your vault accessible to any AI tool that speaks the Model Context Protocol. Your context becomes a resource any agent can query.

**Use cases:**
- You use Claude, Cursor, and ChatGPT — and want all of them to know your projects without re-explaining.
- You're building a custom agent and want it to query your vault directly.

**Why it matters:** Portability. Your context lives in one place and any tool can access it. This is the "never re-explain yourself" infrastructure.

**Ask your AI:** *"I want to turn my vault into an MCP server so any AI tool can access my context. Can you walk me through setting that up?"*

---

## Vault Automation

**What it is:** Automated maintenance — auto-linking, orphan detection, stale content flagging, daily summaries.

**Use cases:**
- Every new note automatically gets suggested connections to existing notes.
- A weekly script surfaces documents with no incoming links so you can link or archive them.

**Why it matters:** A vault that doesn't maintain itself decays. Automation keeps the neural network alive.

**Ask your AI:** *"I want a script that finds all my vault documents with no incoming links and generates a weekly report. Can you build that?"*

---

## Custom Local Tools

**What it is:** Scripts that run on your machine — private, fast, yours.

**Use cases:**
- A script that summarizes your daily notes every evening using a local model and appends to your state-of-play.
- A batch processor that works through a document backlog extracting key themes.

**Why it matters:** Not everything needs the cloud. Local tools are private by default, fast, and fully customizable.

**Ask your AI:** *"I want a Python script that reads today's notes, generates a summary using a local model, and appends it to state-of-play. Can you write that?"*

---

## Creative Project Infrastructure

**What it is:** Scaffolding for writing, art, music, or media. A system that knows your chapters, themes, characters, or episode history.

**Use cases:**
- A manuscript tracker that knows your book's structure, themes, and unresolved threads — helping find plot holes.
- A show prep system that generates episode outlines from what you've been thinking about recently.

**Why it matters:** Creative work has structure too, and your AI partner already knows your voice. Access to your creative infrastructure means it can help with the architecture, not just the words.

**Ask your AI:** *"I'm writing a book with [X chapters]. I want a tracking system for each chapter's status, themes, and unresolved threads. Can you set that up?"*

---

## Decision Journal System

**What it is:** Structured capture of decisions, reasoning, and outcomes — more formal than a decision log, queryable by your AI.

**Use cases:**
- You're a founder making dozens of calls a week and want to learn from patterns in your own judgment.
- You want your AI to reference how you've handled similar situations before.

**Why it matters:** Possibly the most underrated tool here. With a decision journal, your AI can say "last time you faced a similar tradeoff, you chose X because of Y — and it worked / didn't. Does that apply here?"

**Ask your AI:** *"I want a decision journal with structured entries: context, options, decision, reasoning, and a field for outcomes. Can you set that up in my vault?"*

---

## The Pattern

Notice something about all of these? None require you to be a developer. Every one starts with a conversation: you describe what you need, your AI partner helps you build it. Some generate code. Some generate documents. Some generate systems. All emerge from the same collaborative process.

The bootstrap got you and your AI partner on the same page. The vault gave you shared infrastructure. Now you can build whatever you need — together.

---

*Next: [Tips and Patterns](07-tips-and-patterns.md) — field-tested advice for deepening the collaboration.*
