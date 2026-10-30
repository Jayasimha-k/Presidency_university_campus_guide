import json, re
from config import IMAGE_DIR, METADATA_FILE

QUERY_STOPWORDS={"a","an","and","at","block","can","campus","do","floor","for","from","how","i","is","me","near","of","on","or","path","route","show","the","to","what","where","which","with"}

def load_metadata():
    try: return json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return {"images": []}

def matches(query, context="", limit=6):
    files=sorted(p for p in IMAGE_DIR.iterdir() if p.is_file() and p.suffix.lower() in {".jpg",".jpeg",".png",".webp"}) if IMAGE_DIR.exists() else []
    query_terms=set(re.findall(r"[a-z0-9]+", query.lower()))-QUERY_STOPWORDS
    context_terms=set(re.findall(r"[a-z0-9]+", context.lower()))-QUERY_STOPWORDS
    metadata={
        item["filename"]: item
        for item in load_metadata().get("images", [])
        if isinstance(item, dict) and isinstance(item.get("filename"), str)
    }
    found=[]
    for path in files:
        name=path.name
        title=re.sub(r"[_-]+", " ", path.stem)
        item={"filename":name,"title":title,"keywords":re.findall(r"[a-z0-9]+", title.lower())}
        item.update(metadata.get(name, {}))
        searchable=set(re.findall(
            r"[a-z0-9]+",
            " ".join([name, *(str(item.get(k,"")) for k in ("title","location","keywords","description"))]).lower(),
        ))
        query_score=sum(1 for term in query_terms if term in searchable)
        filename_terms=set(re.findall(r"[a-z0-9]+",path.stem.lower()))-QUERY_STOPWORDS
        if query_terms and query_terms==filename_terms:
            query_score+=5
        context_score=sum(1 for term in context_terms if len(term)>2 and term in searchable)
        if query_score or context_score: found.append((query_score,context_score,name,item))
    return [x[3] for x in sorted(found,reverse=True)[:limit]]

def _clean_route_stop(value):
    stop=re.sub(r"\s+", " ", value).strip(" .,:;")
    stop=re.sub(r"^(?:verified|described|direct)\s+(?:route|path|connection)\s+(?:to|toward|towards)\s+", "", stop, flags=re.IGNORECASE)
    return stop.strip(" .,:;")

def _route_stops(record, start, destination):
    route_match=re.search(
        r"\bRoute\s*:\s*(.*?)(?=\s+Directions?\s*:|$)",
        record,
        flags=re.IGNORECASE,
    )
    if route_match:
        stops=[_clean_route_stop(part) for part in re.split(r"\s*->\s*", route_match.group(1))]
        stops=[stop for stop in stops if stop]
        if len(stops)>1:
            return stops

    text=record
    endpoint_title=re.match(
        rf"^\s*ROUTE\s+\d+\s*:\s*{re.escape(start.strip())}\s*(?:->|\bTO\b)\s*{re.escape(destination.strip())}(?=\s|[.;]|$)",
        text,
        flags=re.IGNORECASE,
    )
    if endpoint_title:
        text=text[endpoint_title.end():]

    parts=re.split(r"\s*->\s*",text)
    start_norm=" ".join(re.findall(r"[a-z0-9]+",start.casefold()))
    destination_norm=" ".join(re.findall(r"[a-z0-9]+",destination.casefold()))
    for index,part in enumerate(parts):
        normalized=" ".join(re.findall(r"[a-z0-9]+",part.casefold()))
        if normalized.endswith(start_norm):
            stops=[start.strip()]
            for step in parts[index+1:]:
                stop=_clean_route_stop(step)
                normalized_stop=" ".join(re.findall(r"[a-z0-9]+",stop.casefold()))
                if normalized_stop.startswith(destination_norm):
                    if stops[-1].casefold()!=destination.casefold():
                        stops.append(destination.strip())
                    return stops
                if stop:
                    stops.append(stop)
            break
    return []

def route_images(hits, start, destination):
    """Return one available image per route stop, with the destination photo last."""
    images=[]
    seen=set()
    for hit in hits:
        stops=_route_stops(hit["text"],start,destination)
        if len(stops)>1:
            for stop in stops[:-1]:
                if re.search(r"\bfloor\b",stop,flags=re.IGNORECASE):
                    continue
                candidates=matches(stop,limit=1)
                if not candidates or candidates[0]["filename"] in seen:
                    continue
                image=dict(candidates[0])
                image["title"]=stop
                images.append(image)
                seen.add(image["filename"])
            break

    destination_images=matches(destination,limit=1)
    if destination_images and destination_images[0]["filename"] not in seen:
        image=dict(destination_images[0])
        image["title"]=image.get("location") or image.get("title") or destination
        image["route_stop"]="Final destination"
        images.append(image)
    return images
