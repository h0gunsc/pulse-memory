# Architecture: The Pulse Memory Layers

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      THE AGENT                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  Hot memory  │  │   Skills     │  │  Supermemory       │  │
│  │ (rules+focus)│  │ (procedures) │  │ (semantic search)  │  │
│  └─────────────┘  └──────────────┘  └──────────┬─────────┘  │
│        ▲                    ▲                    │           │
│        │                    │                    ▼           │
│  ┌─────┴─────┐        ┌─────┴─────┐      ┌──────┴─────┐     │
│  │  Session   │        │  Obsidian  │      │  Vault     │     │
│  │  search    │        │  (vault)   │◄────►│  files     │     │
│  │ (raw logs) │        │  source of │      │  (md)      │     │
│  └───────────┘        │  truth     │      └────────────┘     │
│                       └────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                 ▲                     ▲
                 │   human edits       │  sync service watches
                 │   (source of truth) │  and indexes automatically
                 └─────────────────────┘
```

## Layer responsibilities

### Hot memory
Holds only behavioral rules and the current session focus. Kept deliberately small so it
stays in context at all times. No config, no IPs, no code.

### Skills
Procedural knowledge: how to do recurring tasks, pitfalls, user preferences for this kind
of work. Loaded only when their trigger matches. This is the "muscle memory" layer.

### Supermemory
A local semantic search index over everything accumulated. Queries match by *meaning*
(embeddings), not just keywords. This is the "inhale" source.

### Obsidian (the vault)
The files themselves — the source of truth. The human edits them by hand. The agent opens
them point-by-point when needed, never loads the whole vault.

### Session search
Raw past conversation logs, searchable by keyword (FTS). Used when you need the exact
original wording of an old exchange.

## Data flow

1. **Write path (pulse-beat):** agent discovers something new → writes a note into the vault
   → the sync service picks it up → indexes it into supermemory within seconds.
2. **Read path (breathing):** user asks → agent runs a semantic search over supermemory →
   if relevant, opens the matching vault file(s) → answers.

## Properties

- **Human-in-the-loop:** the vault is hand-editable; the human is the ultimate source of truth.
- **Local & free:** no cloud, no LLM tokens spent on memory ops.
- **Compaction-proof:** knowledge lives outside the context window, so compaction only drops
  the conversation scratchpad, never the knowledge.
