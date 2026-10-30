# Pulse — A Living Memory Protocol for AI Agents

> An AI agent's memory doesn't have to be a black box that forgets when the context window collapses.
> **Pulse** is a protocol + reference implementation for a *visible, human-editable, breathing* memory:
> the agent keeps only rules in its hot context, stores everything else outside, and *inhales* (searches by meaning) on every question.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## TL;DR

Large language model agents suffer from **context collapse**: the window fills up, the system compacts it, and the agent silently forgets what you told it last week. The standard answer is "bigger context windows" or "memory as a service" — black boxes the agent manages by itself.

We took the opposite path. Instead of more memory inside the model, we built **a discipline of memory outside the model**:

- the **human is the source of truth** — notes live in a visible, hand-editable vault (Obsidian);
- the agent **writes new knowledge out immediately** (pulse-beats) instead of hoarding it in its head;
- on every question the agent **inhales first**: semantic search over the vault, then it answers;
- the whole stack is **local, free, and costs 0 LLM tokens** (a local embedding model, no cloud).

We then **proved it survives compaction**: in a live session at 127/256K tokens, we flushed knowledge out, let the context collapse, and the agent continued from where it left off — nothing was lost. See [docs/proof.md](docs/proof.md).

---

## Why this is different

| | Typical "agent memory" (Mem0, Zep, Letta, MemGPT) | Pulse |
|---|---|---|
| Who owns the memory | The agent, in a black box | **The human**, in a visible vault |
| Editable by the user | No — API only | **Yes** — open files, edit, done |
| Storage cost | Paid API, tokens per op | $0, local |
| Procedure layer (skills) | Not a thing | **Yes** — skills as procedural memory |
| Survives compaction | Claimed, rarely shown | **Proven** on a live session |
| Behavior change | A library you add | A **protocol** the agent follows |

We are **not** claiming to have invented vector memory. We *are* claiming something the market doesn't sell: a **living discipline of memory for a human–machine pair**, with proof it works.

---

## The protocol (the "breathing")

1. **Hot memory** — only behavioral rules and the current focus. Small, always in context.
2. **Skills** — procedural knowledge, loaded only when triggered.
3. **Supermemory** — semantic search over everything accumulated (meaning, not keywords).
4. **Obsidian** — the files, the source of truth; opened point-by-point when needed.
5. **Session search** — raw past sessions, by keyword.

Every meaningful user question → the agent **breathes in** (semantic search) → answers. New knowledge → **pulse-beat**: written out immediately, never hoarded.

Full text: [MANIFEST.md](MANIFEST.md). Architecture: [docs/architecture.md](docs/architecture.md).
Tiny context window (2K–8K)? See [docs/tiny-window.md](docs/tiny-window.md) — adapted for small windows.

---

## What's in this repo

```
pulse-memory/
├── README.md
├── MANIFEST.md            # the protocol itself
├── LICENSE                # MIT
├── docs/
│   ├── architecture.md    # memory layers
│   ├── proof.md           # the compaction survival test (live log)
│   ├── stack.md           # how to run the local stack
│   └── tiny-window.md     # adapting Pulse to 2K–8K token windows
└── scripts/
    ├── ingest.py          # one-time bulk ingest of the vault
    └── obsidian-sync.py   # live sync (watchdog) — edit → indexed in seconds
```

---

## Quick start

```bash
# 1. Point at your environment
export OBSIDIAN_VAULT="$HOME/ObsidianVault"
export SUPERMEMORY_URL="http://localhost:6767"
export SUPERMEMORY_API_KEY="$(cat /path/to/api-key)"
export SUPERMEMORY_TAG="my-agent"

# 2. Bulk index the vault (idempotent, resumable)
python3 scripts/ingest.py

# 3. Live sync: any vault edit is indexed automatically
python3 scripts/obsidian-sync.py
```

The stack runs fully local: a supermemory server (vector store) + a local embedding model (e.g. `bge-m3`). No cloud, no tokens, no cost. Details in [docs/stack.md](docs/stack.md).

---

## Contributing

This is an open protocol. Ideas we'd love help with (see Issues):

- **Formal benchmark** — a reproducible compaction-survival test suite.
- **Provider adapters** — wire the same protocol to any vector store/embedder.
- **Multi-agent** — pulse-beats shared across a team of agents.
- **Templates** — vault skeletons (hot memory, skills, pulse-beats) to bootstrap a new agent.

---

## License

MIT — do whatever you want, just keep the attribution. See [LICENSE](LICENSE).
