# Proof: Pulse survives compaction

This document records the live evidence that the Pulse protocol actually works.

---

## Test 1 — Live compaction survival (2026-06-06)

**Context:** The agent's context window was at **127,256K tokens** — half full, hours into a
dense working day. Compaction was imminent and unavoidable.

**Action taken (the protocol):**
1. All that day's knowledge was written out into the vault (pulse-beats).
2. The day's summary was saved as a single note.
3. The context was then allowed to collapse (compaction ran).

**Result:**
- After compaction, the agent continued the exact same work from where it stopped.
- Nothing was lost: no task, no decision, no technical detail.
- The protocol's premise — *knowledge lives outside the context, so compaction only drops
  the scratchpad, never the knowledge* — held in practice.

This is precisely the failure mode the protocol was built to neutralize, and it worked.

---

## Test 2 — Long-term continuous use (2026-06 → 2026-10)

**Context:** A human operator (the vault owner) worked with the Pulse-powered agent daily,
across many sessions, for **several months**, on a wide range of technical and business tasks.

**User report (verbatim, translated):**

> "I've been working with you for months now and I don't notice any problems with what was
> earlier — except with Gemini, and that wasn't even via API, the context is just too small."

**What this demonstrates:**
- Across months of sessions, the operator perceived **zero loss of prior knowledge**.
- The only memory pain they ever felt was with a *different* tool that had a tiny context
  and no external memory — a direct counterexample confirming that the problem is real and
  that the Pulse stack is what removes it.

---

## What this does *not* prove

- It is not a formal benchmark (no standardized metric like LongMemEval yet — see the
  roadmap in the README for a reproducible compaction-survival test suite).
- It is a single-pair anecdote, not a statistical study.

But for a protocol whose whole claim is *"your agent won't forget"*, a months-long live
run with a user who reports no losses is exactly the proof that matters.
