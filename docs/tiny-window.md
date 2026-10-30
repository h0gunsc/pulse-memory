# Pulse for tiny context windows

Pulse normally keeps rules + focus in the context and knowledge outside. But very small
windows (e.g. 2K–8K tokens) can't even hold the rules. The fix is to move **rules and
protocol** outside too — leave only a *breathing reflex* inside.

## The one-line principle

> In a tiny window, keep only one line: the pointer to the rule file.
> Everything else lives outside and is pulled on demand.

## Mechanism 1 — Pointers instead of rules

Don't embed a rule list in the system prompt (hundreds of tokens). Embed a single line:

```
Before answering, read the protocol file: /path/to/PULSE-RULES.md
```

The model makes one tool call to read the file only when it actually needs it.
A tiny window stays tiny.

## Mechanism 2 — Episodic exit

A tiny window can't hold a long dialog tail. So every N messages (or at the first sign of
pressure), the agent:

1. flushes the session into a pulse-beat note (outside),
2. starts a clean episode.

Memory becomes purely episodic — outside — which is exactly what Pulse already does.

## Mechanism 3 — Breathing moves out of the model

The most powerful adaptation: the "inhale" (semantic search) moves from the model into the
wrapper. A script, *before* the model call, already:

1. takes the user question,
2. searches supermemory,
3. builds a tight package: question + top-3 snippets,
4. hands only that to the model.

The model receives the minimal context and just answers. The wrapper breathes for the model.

## Honest limit

If the window is below ~2K tokens, even "pointer + question + snippets" may not fit.
Then only Mechanism 3 works: the model becomes a pure generator over a pre-built context,
and the wrapper owns all memory I/O.

---

This section is a design sketch — the reference implementation of the tiny-window wrapper
is a next-step item (see the README roadmap).
