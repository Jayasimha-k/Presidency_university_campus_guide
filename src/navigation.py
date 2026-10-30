"""Source-grounded route lookup; never constructs paths by combining records."""
import re

from src.chatbot import answer_with_context
from src.vector_store import search

def _normalized_location(value):
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))

def _route_records(text):
    return [
        record.strip()
        for record in re.split(r"(?=^ROUTE\s+\d+\s*:)", text, flags=re.IGNORECASE | re.MULTILINE)
        if re.search(r"^ROUTE\s+\d+\s*:", record, flags=re.IGNORECASE | re.MULTILINE)
    ]

def _matches_endpoints(record, start, destination):
    header = re.search(r"^ROUTE\s+\d+\s*:\s*(.+)$", record, flags=re.IGNORECASE | re.MULTILINE)
    if header:
        title = re.split(
            r"\s+(?:Starting Point|Destination|Route|Directions?|Important)\s*:",
            header.group(1).strip(),
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]
        route_prefix = re.compile(
            rf"^\s*{re.escape(start.strip())}\s*(?:->|\bTO\b)\s*{re.escape(destination.strip())}(?=\s|[.;]|$)",
            flags=re.IGNORECASE,
        )
        if route_prefix.search(title):
            return True

    fields = {
        _normalized_location(match.group(1)): _normalized_location(match.group(2))
        for match in re.finditer(
            r"(?<!\w)(Starting Point|Destination)\s*:\s*(.+?)\s*(?=(?:Starting Point|Destination|Route|Directions?|Important)\s*:|$)",
            record,
            flags=re.IGNORECASE | re.MULTILINE,
        )
    }
    return (
        fields.get("starting point") == _normalized_location(start)
        and fields.get("destination") == _normalized_location(destination)
    )

def find_directions(start, destination):
    q=f"ROUTE starting point {start} destination {destination} directions"
    hits=search(q, top_k=6)
    selected=[]
    for hit in hits:
        for record in _route_records(hit["text"]):
            if _matches_endpoints(record, start.strip(), destination.strip()):
                selected.append({**hit, "text": record})
    return selected

def directions_answer(start, destination):
    hits = find_directions(start, destination)
    question = f"How do I get from {start.strip()} to {destination.strip()}?"
    response, hits = answer_with_context(
        question,
        hits,
        system_instruction="Give clear, step-by-step directions only when the supplied route source explicitly supports them. Do not join separate routes, infer missing turns, or invent distances or travel times. Preserve any route verification warning.",
    )
    return response, hits
