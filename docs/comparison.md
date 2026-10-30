# Pulse vs. the field — an honest comparison

This document compares Pulse to the main approaches to agent memory as of late 2026.
We tried to be fair: where Pulse overlaps with something that already exists, we say so.

---

## The landscape

| Approach | Examples | Core idea |
|---|---|---|
| Memory as a service | Mem0, Zep | A hosted memory layer: extract facts, retrieve them on demand |
| Agent-managed memory | Letta (MemGPT), LangMem | The agent itself decides what to store/forget/retrieve; OS-like tiers |
| Vault-as-brain | obsidian-mind, Miyo, AI-Vault | The agent's memory is a Markdown vault (Obsidian) with semantic search |
| Plain RAG / full-context | — | Stuff the context window / retrieve chunks at query time |

## The close one: obsidian-mind

**obsidian-mind** (breferrari/obsidian-mind) is the closest thing to Pulse we have found:

- turns an Obsidian vault into the agent's memory;
- does **not** dump the whole vault into context — lightweight context on session start;
- uses semantic search (QMD), not grep;
- has a `PreCompact` hook (backs up the session before compaction);
- tiered token economics (Always / On-demand / Triggered / Rare).

Pulse and obsidian-mind independently converged on the same core insight: *the vault is
the memory, search it by meaning, don't load it all*. We acknowledge that overlap openly.

## Where Pulse differs

| Dimension | obsidian-mind / others | Pulse |
|---|---|---|
| Human as editor | The agent writes to the vault | **The human is the source of truth** — hand-edits files; the agent reads and appends pulse-beats |
| Proven survival of compaction | `PreCompact` hook exists (backup) | **Live-proven**: session at 127/256K flushed → collapsed → continued, nothing lost ([proof.md](proof.md)) |
| Cost | Embedding API calls (OpenAI etc.) can be paid | **$0, fully local** (bge-m3), zero LLM tokens for memory ops |
| Procedural layer | A separate "skills" layer is not part of the design | **Skills = procedural memory** (how-to, pitfalls), loaded on trigger |
| Behavior, not just software | A tool you integrate | A **protocol** the agent follows: hot memory → skills → semantic search → vault → session search |

## Against the commercial services (Mem0, Zep)

Mem0 and Zep are strong, mature products. Their numbers (LongMemEval etc.) are good —
but they are *black boxes*:

- the user cannot edit what the agent remembers — API only;
- every operation costs tokens/API calls;
- the memory is owned by the provider (or at least by the agent, not the human).

Pulse trades some automated extraction power for **visibility, control, and zero cost**:
you can open the vault and fix a wrong memory with a text editor. That is a deliberate
trade, not a claim of superiority in retrieval accuracy.

## What we explicitly do NOT claim

- We did not invent vector memory, embeddings, or RAG.
- We are not claiming higher benchmark scores than Mem0/Zep.
- We are not claiming the vault-as-brain idea as exclusively ours (obsidian-mind exists).

## What we do claim

A **living discipline of memory for a human–machine pair**: visible, hand-editable, local,
$0, with a procedural layer, and proven to survive compaction in a real long-running
session. As a published, reproducible protocol with a working reference implementation,
we have not seen that combination elsewhere.
