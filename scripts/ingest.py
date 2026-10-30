#!/usr/bin/env python3
"""Bulk-ingest a Markdown vault into a local Supermemory store (idempotent).

Every .md becomes a document. customId is sanitized (only [A-Za-z0-9:_-]).
Re-running updates the same documents and continues from where it left off.
Progress is saved to a log file, so you can interrupt and resume.

Config via environment variables:
  OBSIDIAN_VAULT   path to the vault folder (required)
  SUPERMEMORY_URL   base URL of the supermemory server (default http://localhost:6767)
  SUPERMEMORY_API_KEY  bearer token for the server
  SUPERMEMORY_TAG   container tag / namespace (default "hermes-agent")
  PULSE_PROGRESS    progress log path (default ./ingest-progress.jsonl)
"""

import os, sys, json, time, re, hashlib, urllib.request, urllib.error

BASE = os.environ.get("SUPERMEMORY_URL", "http://localhost:6767")
KEY  = os.environ.get("SUPERMEMORY_API_KEY", "")
VAULT = os.environ.get("OBSIDIAN_VAULT", "")
TAG  = os.environ.get("SUPERMEMORY_TAG", "hermes-agent")
PROG = os.environ.get("PULSE_PROGRESS", os.path.join(os.getcwd(), "ingest-progress.jsonl"))

SKIP_DIRS = {".obsidian", ".smart-env", ".git", ".stfolder", ".stversions", ".trash"}

def sanitize(s):
    """customId: only [A-Za-z0-9:_-], ~90 chars max. Long paths: prefix + sha1."""
    s = s.replace("\\", "/")
    s = re.sub(r"[^A-Za-z0-9:_\-/]", "_", s)
    s = s.replace("/", "-")
    if len(s) > 91:
        h = hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]
        s = s[:77] + "-" + h
    return s

def post(custom_id, path, content):
    body = json.dumps({
        "content": content,
        "type": "text",
        "containerTags": [TAG],
        "customId": custom_id,
        "metadata": {"source": "obsidian", "path": path},
        # taskType=superrag + dreaming=instant: index within the request,
        # avoids a deferred worker timing out and dropping the document.
        "taskType": "superrag", "dreaming": "instant",
    }).encode("utf-8")
    for attempt in range(6):
        req = urllib.request.Request(BASE + "/v3/documents", data=body, method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, b""
        except urllib.error.HTTPError as e:
            code = e.code
            resp = e.read()[:200]
            if code in (400, 429, 500, 502, 503, 504):
                # 400 often arrives on indexer races/overload — retry passes.
                time.sleep(2 + attempt * 2)
                continue
            return code, resp
        except Exception as e:
            if attempt == 5:
                return None, str(e).encode()
            time.sleep(3)
    return None, b"max retries"

def collect():
    files = []
    for root, dirs, names in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            if n.lower().endswith(".md"):
                files.append(os.path.join(root, n))
    files.sort()
    return files

def main():
    if not VAULT or not os.path.isdir(VAULT):
        print("Set OBSIDIAN_VAULT to an existing folder.", file=sys.stderr)
        sys.exit(2)

    files = collect()
    total = len(files)
    done = set()
    if os.path.exists(PROG):
        for line in open(PROG, encoding="utf-8", errors="replace"):
            try:
                done.add(json.loads(line)["rel"])
            except Exception:
                pass
    print(f"Notes: {total} | already ingested: {len(done)}")
    ok = skip = err = 0
    t0 = time.time()
    with open(PROG, "a", encoding="utf-8") as plog:
        for i, f in enumerate(files, 1):
            rel = os.path.relpath(f, VAULT).replace("\\", "/")
            if rel in done:
                skip += 1
                continue
            cid = "obsidian:" + sanitize(rel)
            try:
                content = open(f, encoding="utf-8", errors="replace").read()
            except Exception as e:
                print(f"[{i}] SKIP {rel}: {e}"); err += 1; continue
            if not content.strip():
                continue
            # title prefix: keeps the extractor from treating a URL-led note
            # as a web link, and gives the document a meaningful title.
            titled = "# " + os.path.basename(rel) + "\n\n" + content
            st, resp = post(cid, rel, titled)
            if st in (200, 201, 202):
                ok += 1
                plog.write(json.dumps({"rel": rel, "status": st, "ts": time.time()}) + "\n")
                plog.flush()
                if ok % 50 == 0:
                    el = time.time() - t0
                    print(f"  +{ok} ({skip+ok+err}/{total}) · {el:.0f}s · {ok/el:.1f}/s")
            else:
                err += 1
                print(f"[{i}] FAIL {rel}: {st} {resp!r}"[:300])
    print(f"DONE: ingested={ok} skipped={skip} errors={err}")

if __name__ == "__main__":
    main()
