"""Deterministic text chunking and source fingerprinting."""
import hashlib
import re
from pathlib import Path
from config import KNOWLEDGE_DIR, CHUNK_WORDS, CHUNK_OVERLAP

def sources():
    return sorted(p for p in KNOWLEDGE_DIR.glob("*.txt") if p.is_file())

def read_sources():
    return [(p, p.read_text(encoding="utf-8-sig").strip()) for p in sources()]

def fingerprint(items):
    h = hashlib.sha256()
    for path, body in items:
        h.update(path.name.encode()); h.update(b"\0"); h.update(body.encode()); h.update(b"\0")
    return h.hexdigest()

def chunks(items):
    out = []
    size = max(50, CHUNK_WORDS); overlap = max(0, min(CHUNK_OVERLAP, size - 1))
    for path, body in items:
        if not body:
            continue
        # Prefer route/section boundaries while preserving the original wording.
        sections = re.split(r"(?=^(?:ROUTE\s+\d+|SECTION\s+\d+|LOCATION\s+\d+))", body, flags=re.I|re.M)
        for section in sections:
            words = section.split()
            for start in range(0, len(words), size-overlap):
                part = " ".join(words[start:start+size]).strip()
                if part:
                    idx = len(out)
                    out.append({"id": f"{path.name}:{idx}", "text": part, "source": path.name, "chunk": idx})
                if start + size >= len(words): break
    return out
