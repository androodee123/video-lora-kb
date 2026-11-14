"""Shared helpers for scripts/update.py (identical copy in image-lora-kb and video-lora-kb).

Safety contract: metadata only; never downloads weights; never runs ingest.py; never ingests to Graydient;
never touches any account other than the GitHub account `androodee123`; aborts the commit on any secret hit.
"""
from __future__ import annotations
import fcntl, json, os, re, subprocess, sys, time
from datetime import datetime
from pathlib import Path

GH_ACCOUNT = "androodee123"
FORBIDDEN_ACCOUNT = "adonaldson" + "-oss"

# Secret patterns, built so this file never matches its own scan.
_P = {
    "hf-token": r"hf_[A-Za-z0-9]{25,}",
    "github-token": r"(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{25,})",
    "bearer": r"Bearer\s+[A-Za-z0-9._\-]{25,}",
    "api-key-in-url": r"[?&](?:token|api_key|apikey|key)=[A-Za-z0-9_\-]{16,}",
    "sk-key": r"sk-[A-Za-z0-9]{25,}",
    "private-key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "graydient-login-config": r"graydient" + r"_login",
    "graydient-login-url": r"https?://[^\s\"'<>)]*graydient[^\s\"'<>)]*/(?:login|magic|auth|signin)[^\s\"'<>)]*",
    "civit-token": r"civitai[^\n]{0,40}(?:token|api[_-]?key)\s*[:=]\s*[\"']?[A-Za-z0-9]{16,}",
}
SECRET_RES = {k: re.compile(v, re.I if k in ("graydient-login-config", "graydient-login-url", "civit-token") else 0) for k, v in _P.items()}

def log(*a):
    print(*a, file=sys.stderr, flush=True)

def sanitize_env():
    for k in ("GITHUB_TOKEN", "GH_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN"):
        os.environ.pop(k, None)

def sh(cmd, root, check=True, capture=True, timeout=None):
    r = subprocess.run(cmd, cwd=root, capture_output=capture, text=True, timeout=timeout, env=os.environ.copy())
    if check and r.returncode != 0:
        raise RuntimeError(f"command failed ({r.returncode}): {' '.join(cmd)}\n{(r.stderr or '')[-600:]}")
    return r

class Lock:
    def __init__(self, root: Path):
        self.f = open(root / ".update.lock", "w")
    def __enter__(self):
        try:
            fcntl.flock(self.f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise SystemExit("another update.py run holds .update.lock; aborting")
        return self
    def __exit__(self, *a):
        fcntl.flock(self.f, fcntl.LOCK_UN)

class Clock:
    def __init__(self, max_minutes: float):
        self.t0 = time.time()
        self.deadline = self.t0 + max_minutes * 60
        self.steps = {}
    def left(self):
        return self.deadline - time.time()
    def step(self, name):
        clock = self
        class _S:
            def __enter__(s):
                s.t = time.time(); log(f"== {name}"); return s
            def __exit__(s, *a):
                clock.steps[name] = round(time.time() - s.t, 1)
        return _S()

def check_gh_account(root: Path, need_push: bool):
    """Return (ok, detail). Never prints tokens."""
    origin = sh(["git", "remote", "get-url", "origin"], root, check=False).stdout.strip()
    if f"github.com/{GH_ACCOUNT}/" not in origin and f"github.com:{GH_ACCOUNT}/" not in origin:
        return False, f"origin is not under {GH_ACCOUNT}: {origin}"
    if FORBIDDEN_ACCOUNT in origin:
        return False, "origin points at a forbidden account"
    r = sh(["gh", "api", "user", "-q", ".login"], root, check=False)
    login = (r.stdout or "").strip()
    if login != GH_ACCOUNT:
        return (not need_push), f"gh active account is '{login or 'unknown'}', expected {GH_ACCOUNT}"
    return True, GH_ACCOUNT

def ensure_git_identity(root: Path):
    if not sh(["git", "config", "user.name"], root, check=False).stdout.strip():
        sh(["git", "config", "user.name", GH_ACCOUNT], root)
    if not sh(["git", "config", "user.email"], root, check=False).stdout.strip():
        sh(["git", "config", "user.email", "323714909+androodee123@users.noreply.github.com"], root)

def dirty(root: Path):
    return sh(["git", "status", "--porcelain"], root).stdout.strip()

_MASKS = [re.compile(p) for p in (
    r"\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?",
    r"\d{1,2} [A-Z][a-z]{2,8} \d{4}(?:, \d{2}:\d{2})?(?: Africa/Johannesburg \(SAST\))?",
    r"\d{2}:\d{2}",
)]
def _mask(text: str) -> str:
    for m in _MASKS:
        text = m.sub("<TS>", text)
    return text

def revert_cosmetic(root: Path):
    """Revert tracked text files whose only diff is a timestamp. Returns list of reverted paths."""
    reverted = []
    for p in sh(["git", "diff", "--name-only"], root).stdout.split("\n"):
        p = p.strip()
        if not p or not p.endswith((".md", ".txt", ".json")):
            continue
        old = sh(["git", "show", f"HEAD:{p}"], root, check=False).stdout
        new = (root / p).read_text(errors="replace") if (root / p).exists() else None
        if new is not None and _mask(old) == _mask(new):
            sh(["git", "checkout", "--", p], root)
            reverted.append(p)
    return reverted

def secret_scan_staged(root: Path):
    """Scan staged added lines + staged paths. Returns list of (pattern, file) hits (no secret values)."""
    hits = []
    names = sh(["git", "diff", "--cached", "--name-only"], root).stdout.split("\n")
    for n in names:
        if n.strip().endswith((".safetensors", ".ckpt", ".pt", ".env")) or n.strip() == ".env":
            hits.append(("forbidden-file-type", n.strip()))
    diff = sh(["git", "diff", "--cached", "-U0", "--no-color"], root).stdout
    cur = "?"
    for ln in diff.splitlines():
        if ln.startswith("+++ b/"):
            cur = ln[6:]
        elif ln.startswith("+") and not ln.startswith("+++"):
            for k, rx in SECRET_RES.items():
                if rx.search(ln):
                    hits.append((k, cur))
    seen, out = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h); out.append(h)
    return out

def scan_tree(root: Path):
    """Scan every tracked file (used for the one-off verification)."""
    hits = []
    for p in sh(["git", "ls-files"], root).stdout.split("\n"):
        f = root / p
        if not p or not f.is_file() or f.stat().st_size > 60_000_000:
            continue
        try:
            for i, ln in enumerate(f.read_text(errors="ignore").splitlines()):
                for k, rx in SECRET_RES.items():
                    if rx.search(ln):
                        hits.append((k, p, i + 1))
        except Exception:
            pass
    return hits

def patch_markers(path: Path, block: str, before_heading: str, start="<!-- AUTO-UPDATE:START -->", end="<!-- AUTO-UPDATE:END -->"):
    text = path.read_text()
    new_block = f"{start}\n{block.strip()}\n{end}\n"
    if start in text and end in text:
        text = re.sub(re.escape(start) + r".*?" + re.escape(end) + r"\n?", lambda m: new_block, text, flags=re.S)
    else:
        i = text.find(before_heading)
        text = (text[:i] + new_block + "\n" + text[i:]) if i >= 0 else text.rstrip() + "\n\n" + new_block
    path.write_text(text)

def changelog_prepend(root: Path, entry: str):
    p = root / "CHANGELOG.md"
    head = "# Changelog\n\nAutomatic entries from `scripts/update.py` (newest first). Catalog/SKILL updates are applied automatically; adding weights to Graydient stays a manual, Andrew-requested step.\n\n"
    body = p.read_text() if p.exists() else head
    if not body.startswith("# Changelog"):
        body = head + body
    i = body.find("\n## ")
    body = (body[:i + 1] + entry.rstrip() + "\n\n" + body[i + 1:]) if i >= 0 else body.rstrip() + "\n\n" + entry.rstrip() + "\n"
    p.write_text(body)

def fmt_items(items, limit=40):
    out = [f"- {x}" for x in items[:limit]]
    if len(items) > limit:
        out.append(f"- … and {len(items) - limit} more")
    return out

def commit_and_push(root: Path, msg: str, push=True):
    """Stage everything, scan, commit, push. Returns dict(status, sha, hits)."""
    sh(["git", "add", "-A"], root)
    if not sh(["git", "diff", "--cached", "--name-only"], root).stdout.strip():
        return {"status": "no-change", "sha": sh(["git", "rev-parse", "HEAD"], root).stdout.strip(), "hits": []}
    hits = secret_scan_staged(root)
    if hits:
        sh(["git", "reset", "-q"], root)
        return {"status": "aborted-secret-scan", "sha": None, "hits": hits}
    sh(["git", "commit", "-q", "-m", msg], root)
    sha = sh(["git", "rev-parse", "HEAD"], root).stdout.strip()
    if not push:
        return {"status": "committed-not-pushed", "sha": sha, "hits": []}
    r = sh(["git", "push", "origin", "HEAD:main"], root, check=False)
    if r.returncode != 0:
        sh(["git", "pull", "--rebase"], root)
        r = sh(["git", "push", "origin", "HEAD:main"], root, check=False)
        sha = sh(["git", "rev-parse", "HEAD"], root).stdout.strip()
        if r.returncode != 0:
            return {"status": "push-failed", "sha": sha, "hits": [], "error": (r.stderr or "")[-300:]}
    return {"status": "pushed", "sha": sha, "hits": []}

def restore_tree(root: Path):
    """After --dry-run: discard generated changes (tracked files and new non-ignored files)."""
    sh(["git", "checkout", "--", "."], root, check=False)
    sh(["git", "clean", "-fdq"], root, check=False)  # respects .gitignore, so caches survive

def visibility(root: Path, repo: str):
    r = sh(["gh", "repo", "view", repo, "--json", "visibility", "-q", ".visibility"], root, check=False)
    return (r.stdout or "").strip() or "unknown"
