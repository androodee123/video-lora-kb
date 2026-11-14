"""Adults-only safety filter shared by the update scripts (identical rules to image-lora-kb)."""
from __future__ import annotations
import re

MINOR_RE = re.compile(r"\b(loli\w*|shota\w*|child\w*|kids?|toddler|underage|under[- ]age|minor|preteen|pre[- ]teen|teen\w*|tween|jk|jc|elementary|middle[- ]school|little[- ]girl|little[- ]boy|young[- ]girl|baby[- ]?face|age[- ]?(slider|difference|regress\w*)|lolita)\b", re.I)
HARD_RE = re.compile(r"\b(loli\w*|shota\w*|underage|under[- ]age|preteen|pre[- ]teen)\b", re.I)
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
