"""Adults-only safety filter shared by the update scripts (identical rules to image-lora-kb)."""
from __future__ import annotations
import re

MINOR_RE = re.compile(r"\b(loli(?!ta)\w*|shota(?!ro)\w*|toddler|underage|under[- ]age|preteen|pre[- ]teen)\b", re.I)  # hard exclusions only; everything else is flagged minor_coded by semantic.py
HARD_RE = re.compile(r"\b(loli(?!ta)\w*|shota(?!ro)\w*|underage|under[- ]age|preteen|pre[- ]teen)\b", re.I)
FORBIDDEN_ID_RE = re.compile(r"youngandrew|handyandy|andrewyoung|andy\.?young", re.I)

def minor_reason(*texts):
    for t in texts:
        if not t:
            continue
        if FORBIDDEN_ID_RE.search(t):
            return "forbidden identity (youngandrew/handyandy/andrewyoung)"
        m = MINOR_RE.search(t)
        if m:
            return f"possible minor-coded term: {m.group(0)}"
    return None

def hard_reason(text):
    m = HARD_RE.search(text or "")
    return f"possible minor-coded term in description: {m.group(0)}" if m else None
