# MANIFEST — The Pulse Protocol

> Version: rev9 (2026-10) · Previously: rev8 (2026-06, on a self-hosted semantic store)

This is the full text of the **Pulse** method. It is a *protocol of behavior*, not a library.

---

## 1. The problem

Context windows are finite. When they fill up, the system compacts them, and an agent that
hoards knowledge in its context **silently forgets**. Bigger windows delay the collapse —
they don't solve it. Memory services (Mem0, Zep, Letta…) move knowledge into black boxes
that only the agent can touch, and they cost tokens per operation.

## 2. The insight

Forget "more memory inside the model". Build **a discipline of memory outside the model**:

- The **human is the source of truth**. Knowledge lives in a visible, hand-editable vault.
- The agent **does not carry everything**. It carries only rules + focus.
- The agent **writes new knowledge out immediately** (a "pulse-beat"), never hoards it.
- On every question, the agent **breathes in**: searches by *meaning*, then answers.

## 3. The layers

| Layer | What | When |
|---|---|---|
| **Hot memory** | behavior rules + current focus | every request |
| **Skills** | procedures / pitfalls | on trigger |
| **Supermemory** | semantic search over everything accumulated | "what did we decide about X?" |
| **Obsidian** | the files — source of truth | open point-by-point |
| **Session search** | raw past sessions | by keyword |

## 4. Breathing (the core loop)

**Every meaningful question:**

1. `supermemory-search` by *meaning* (not by keywords).
2. If found, open the actual file in the vault (point-by-point, not the whole vault).
3. Only then answer.
4. If nothing found — say so. Do not invent.

**New knowledge → pulse-beat:** write a note into the vault immediately.
The sync service indexes it into supermemory within seconds. Never "later".

## 5. Hot memory

Hot memory holds **only** rules of behavior + session focus.
No technical config, no IPs, no dates, no code — all of that lives in the vault/supermemory
and is pulled only when needed.

## 6. Rules

- Don't lie. Unsure → say so.
- A correction → change.
- Nothing found → say nothing was found. Never fabricate.

## 7. Why it survives compaction

Since the source of truth is outside the context, a compaction is not a catastrophe:
the agent loses only its *conversation scratchpad*, never its knowledge.
Proven live — see [docs/proof.md](docs/proof.md).

## 8. The claim

We are **not** claiming to have invented vector memory. We claim a **living discipline of
memory for a human–machine pair** — visible, hand-editable, local, $0, and proven to
survive compaction. That combination, as a published protocol, we have not seen elsewhere.
