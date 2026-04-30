# clevels_ai/vectorstore.py
import json
from pathlib import Path
import numpy as np
import faiss
from .config import settings
from .logger import logger

INDEX_PATH = Path(settings.VECTOR_INDEX_PATH)
META_PATH = Path(settings.VECTOR_META_PATH)

def _ensure_index(dim: int):
    if INDEX_PATH.exists():
        idx = faiss.read_index(str(INDEX_PATH))
        return idx
    # IndexFlatL2 with id map
    flat = faiss.IndexFlatL2(dim)
    idx = faiss.IndexIDMap(flat)
    faiss.write_index(idx, str(INDEX_PATH))
    return idx

def _load_meta():
    if META_PATH.exists():
        try:
            return json.loads(META_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            logger.exception("Failed to load meta json: %s", e)
            return {}
    return {}

def _save_meta(meta: dict):
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

def upsert(namespace: str, docs: list, embeddings: list):
    """
    docs: list of dicts with 'id' and 'text' fields
    embeddings: list of numpy arrays
    """
    if not docs:
        return
    dim = embeddings[0].shape[0]
    idx = _ensure_index(dim)
    meta = _load_meta()
    # use incremental integer ids
    start_id = max([int(x) for x in meta.keys()] or [-1]) + 1
    ids = []
    vectors = []
    for i, (doc, emb) in enumerate(zip(docs, embeddings)):
        doc_id = start_id + i
        ids.append(doc_id)
        vectors.append(emb.astype("float32"))
        meta[str(doc_id)] = {"namespace": namespace, "text": doc["text"], "source": doc.get("source", "")}
    vectors = np.vstack(vectors)
    idx.add_with_ids(vectors, np.array(ids, dtype="int64"))
    faiss.write_index(idx, str(INDEX_PATH))
    _save_meta(meta)

def search(query_emb, top_k=5, namespace=None):
    if not INDEX_PATH.exists() or not META_PATH.exists():
        return []
    idx = faiss.read_index(str(INDEX_PATH))
    q = query_emb.reshape(1, -1).astype("float32")
    D, I = idx.search(q, top_k)
    meta = _load_meta()
    results = []
    # I are ids
    for dist, iid in zip(D[0], I[0]):
        if iid == -1:
            continue
        key = str(int(iid))
        item = meta.get(key)
        if not item:
            continue
        if namespace and item.get("namespace") != namespace:
            continue
        results.append({"score": float(dist), "text": item.get("text"), "source": item.get("source", "")})
    return results
