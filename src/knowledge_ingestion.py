"""Deterministic text chunking and source fingerprinting."""
import hashlib
import re
from pathlib import Path
from config import KNOWLEDGE_DIR, UPLOAD_DIR, CHUNK_WORDS, CHUNK_OVERLAP

def sources():
    files = list(KNOWLEDGE_DIR.glob("*.txt")) + list(UPLOAD_DIR.glob("*.txt"))
    return sorted((path for path in files if path.is_file()), key=source_name)

def source_name(path):
    try:
        return f"uploads/{path.relative_to(UPLOAD_DIR).as_posix()}"
    except ValueError:
        try:
            return path.relative_to(KNOWLEDGE_DIR).as_posix()
        except ValueError:
            return path.name

def read_sources():
    return [(p, p.read_text(encoding="utf-8-sig").strip()) for p in sources()]

def fingerprint(items):
    h = hashlib.sha256()
    for path, body in items:
        h.update(source_name(path).encode()); h.update(b"\0"); h.update(body.encode()); h.update(b"\0")
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
                    name = source_name(path)
                    out.append({"id": f"{name}:{idx}", "text": part, "source": name, "chunk": idx})
                if start + size >= len(words): break
    return out
