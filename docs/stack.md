# Stack: running Pulse locally

The Pulse protocol needs three local pieces:

1. **The vault** — a folder of Markdown files (works with Obsidian, but any folder of `.md`
   files works; you don't even need the Obsidian app).
2. **A supermemory server** — a local vector store with a search API.
3. **The sync + ingest scripts** — in `scripts/`.

Everything runs locally. No cloud, no LLM tokens spent on memory operations.

---

## 1. Vault

Any folder of Markdown files. The human edits it by hand — that's the point.

```bash
export OBSIDIAN_VAULT="$HOME/ObsidianVault"
```

## 2. Supermemory server

We run a self-hosted supermemory server (`http://localhost:6767`) backed by a local
embedding model (e.g. `bge-m3`, 1024-dim). The scripts in this repo talk to it via
`/v3/documents` and `/v3/search`.

Set these to match your server:

```bash
export SUPERMEMORY_URL="http://localhost:6767"
export SUPERMEMORY_API_KEY="$(cat /path/to/api-key)"   # or however your server auths
export SUPERMEMORY_TAG="my-agent"                       # container tag / namespace
```

> The exact server implementation is intentionally not bundled here — the protocol is
> server-agnostic. If you have a different vector store, adapt the two scripts' `api()`
> helper (it's a short function at the top of each file).

## 3. Ingest (one-time bulk)

```bash
python3 scripts/ingest.py
```

- Walks the vault, uploads every `.md` as a document.
- **Idempotent:** re-running skips what's already uploaded.
- **Resumable:** progress is saved to a log file; interrupt and resume anytime.
- `customId` is sanitized (only `[A-Za-z0-9:_-]`), long paths are hashed to stay unique.

## 4. Live sync (watchdog)

```bash
python3 scripts/obsidian-sync.py
```

- Watches the vault with `watchdog` (file-system events).
- On create/modify/delete of a `.md` → updates or deletes the corresponding document
  in supermemory **within seconds**.
- **Debounced** (3 s): several rapid edits = one upload.
- Skips service dirs (`.obsidian`, `.git`, etc.) and binary-looking files.

## Dependencies

```bash
pip install watchdog
```

No other third-party packages are required (stdlib `urllib`, `json`, `hashlib`, `re`).

---

## Example: end-to-end

```bash
export OBSIDIAN_VAULT="$HOME/ObsidianVault"
export SUPERMEMORY_URL="http://localhost:6767"
export SUPERMEMORY_API_KEY="$(cat /path/to/api-key)"

python3 scripts/ingest.py
python3 scripts/obsidian-sync.py   # leave running
```

Now: edit any note in the vault → within seconds it's searchable by meaning in supermemory
→ the agent can inhale it on the next question.
