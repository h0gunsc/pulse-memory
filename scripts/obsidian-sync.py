#!/usr/bin/env python3
"""Obsidian -> Supermemory: live sync driven by filesystem events.

No cron, no polling. The OS reports file changes (mtime/size) and the note is
sent to supermemory immediately. Runs as a long-lived process (daemon/service).

Watches:
  - .md files in the vault (excluding service dirs)
  - create / modify / delete
  - deleting a note deletes its document from supermemory

Storm protection: debounce (several rapid edits = one upload).

Config via environment variables (same as ingest.py):
  OBSIDIAN_VAULT   path to the vault folder (required)
  SUPERMEMORY_URL   base URL of the supermemory server (default http://localhost:6767)
  SUPERMEMORY_API_KEY  bearer token for the server
  SUPERMEMORY_TAG   container tag / namespace (default "hermes-agent")
  PULSE_SYNC_STATE state file path (default ./sync-state.json)
"""

import os, sys, json, time, re, hashlib, threading, queue
import urllib.request, urllib.error
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

VAULT = os.environ.get("OBSIDIAN_VAULT", "")
BASE = os.environ.get("SUPERMEMORY_URL", "http://localhost:6767")
TAG = os.environ.get("SUPERMEMORY_TAG", "hermes-agent")
KEY = os.environ.get("SUPERMEMORY_API_KEY", "")
STATE = os.environ.get("PULSE_SYNC_STATE", os.path.join(os.getcwd(), "sync-state.json"))
SKIP_DIRS = {".stversions", ".stfolder", ".obsidian", ".smart-env", ".git", ".trash"}
DEBOUNCE = 3.0  # seconds: wait for quiet after the last edit of a file

def log(msg):
    line = "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    try:
        print(line, flush=True)
    except Exception:
        pass

def sanitize(s):
    s = s.replace("\\", "/")
    s = re.sub(r"[^A-Za-z0-9:_\-/]", "_", s)
    s = s.replace("/", "-")
    if len(s) > 91:
        s = s[:77] + "-" + hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]
    return s

def rel_of(path):
    return os.path.relpath(path, VAULT).replace("\\", "/")

def is_tracked(path):
    if not path.lower().endswith(".md"):
        return False
    parts = set(rel_of(path).split("/"))
    return not (parts & SKIP_DIRS)

def api(method, endpoint, payload=None, timeout=180):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(BASE + endpoint, data=body, method=method,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

def upsert(path):
    rel = rel_of(path)
    cid = "obsidian:" + sanitize(rel)
    try:
        raw = open(path, "rb").read()
    except Exception as e:
        log("SKIP %s: %s" % (rel, e)); return False
    # Skip binary-ish .md dumps (e.g. unpacked .db/.sqlite as notes):
    # >5% NUL bytes => no meaning, just search noise.
    if raw.count(b"\x00") / max(len(raw), 1) > 0.05:
        log("SKIP-BIN %s" % rel); return False
    content = raw.decode("utf-8", "replace")
    if not content.strip():
        return False
    titled = "# " + os.path.basename(rel) + "\n\n" + content
    payload = {"content": titled, "type": "text", "containerTags": [TAG],
               "customId": cid, "metadata": {"source": "obsidian", "path": rel},
               "taskType": "superrag", "dreaming": "instant"}
    for attempt in range(4):
        try:
            st, _ = api("POST", "/v3/documents", payload)
            if st in (200, 201, 202):
                log("UP %s" % rel)
                return True
        except urllib.error.HTTPError as e:
            if e.code in (400, 429, 500, 502, 503, 504):
                time.sleep(2 + attempt * 2); continue
            log("FAIL %s: %d" % (rel, e.code)); return False
        except Exception as e:
            if attempt == 3:
                log("FAIL %s: %s" % (rel, str(e)[:60])); return False
            time.sleep(3)
    return False

def delete(path):
    rel = rel_of(path)
    cid = "obsidian:" + sanitize(rel)
    try:
        import urllib.parse
        api("DELETE", "/v3/documents/" + urllib.parse.quote(cid), None, timeout=30)
        log("DEL %s" % rel)
    except Exception as e:
        log("DEL-SKIP %s: %s" % (rel, str(e)[:50]))

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.q = queue.Queue()

    def _push(self, path, action):
        if path and is_tracked(path):
            self.q.put((path, action))

    def on_created(self, e):
        if not e.is_directory: self._push(e.src_path, "up")

    def on_modified(self, e):
        if not e.is_directory: self._push(e.src_path, "up")

    def on_moved(self, e):
        if not e.is_directory:
            self._push(e.src_path, "del")
            self._push(e.dest_path, "up")

    def on_deleted(self, e):
        if not e.is_directory: self._push(e.src_path, "del")

def worker(h):
    """Debounce: collect events per file, flush after a quiet pause."""
    pending = {}
    while True:
        try:
            path, action = h.q.get(timeout=1.0)
            pending[path] = (action, time.time())
        except queue.Empty:
            pass
        now = time.time()
        ready = [p for p, (a, t) in pending.items() if now - t >= DEBOUNCE]
        for p in ready:
            action, _ = pending.pop(p)
            if action == "del":
                delete(p)
            else:
                if os.path.exists(p):
                    upsert(p)
                else:
                    delete(p)

def main():
    if not VAULT or not os.path.isdir(VAULT):
        print("Set OBSIDIAN_VAULT to an existing folder.", file=sys.stderr)
        sys.exit(2)

    log("=== Obsidian -> Supermemory sync started ===")
    try:
        st, _ = api("POST", "/v3/search", {"q": "test", "containerTags": [TAG], "limit": 1}, timeout=30)
        log("supermemory reachable (status %d)" % st)
    except Exception as e:
        log("WARN supermemory unreachable: %s" % str(e)[:80])

    h = Handler()
    obs = Observer()
    obs.schedule(h, VAULT, recursive=True)
    obs.start()
    log("watching %s (recursive)" % VAULT)
    threading.Thread(target=worker, args=(h,), daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

if __name__ == "__main__":
    main()
