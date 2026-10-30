import chromadb
from config import CHROMA_DIR, COLLECTION_NAME, TOP_K
from src.embeddings import embed_texts
from src.knowledge_ingestion import read_sources, fingerprint, chunks

def collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

def current_fingerprint():
    items = read_sources()
    return fingerprint(items) if any(body for _, body in items) else ""

def index(force=False):
    items = read_sources()
    if not items or not any(body for _, body in items):
        return {"ok": False, "message": "No non-empty .txt knowledge-base files were found."}
    fp = fingerprint(items); col = collection()
    if not force and col.count() and col.metadata.get("source_fingerprint") == fp:
        return {"ok": True, "message": "Knowledge base is already indexed.", "count": col.count(), "fingerprint": fp}
    docs = chunks(items)
    if not docs:
        return {"ok": False, "message": "No text chunks could be created."}
    # Rebuild the collection to avoid stale/duplicate documents after edits.
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try: client.delete_collection(COLLECTION_NAME)
    except Exception: pass
    col = client.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine", "source_fingerprint": fp})
    batch = 64
    for i in range(0, len(docs), batch):
        part = docs[i:i+batch]
        col.add(ids=[x["id"] for x in part], documents=[x["text"] for x in part], embeddings=embed_texts([x["text"] for x in part]), metadatas=[{"source":x["source"], "chunk":x["chunk"]} for x in part])
    return {"ok": True, "message": "Index created.", "count": col.count(), "fingerprint": fp}

def search(query, top_k=TOP_K, source: str | list[str] | None = None):
    col = collection()
    if not col.count(): return []
    if source == []:
        return []
    if isinstance(source, str):
        filters = {"where": {"source": source}}
    elif source:
        filters = {"where": {"source": {"$in": source}}}
    else:
        filters = {}
    result = col.query(query_embeddings=embed_texts([query]), n_results=min(top_k, col.count()), include=["documents", "metadatas", "distances"], **filters)
    return [{"text":d,"source":m.get("source","unknown"),"chunk":m.get("chunk"),"distance":dist} for d,m,dist in zip(result["documents"][0],result["metadatas"][0],result["distances"][0])]
