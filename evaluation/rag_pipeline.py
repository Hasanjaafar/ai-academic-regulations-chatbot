# -*- coding: utf-8 -*-
"""Chroma retrieval + context formatting for evaluation (mirrors app logic, no Streamlit)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma_db_handbook"
EMBED_MODEL_NAME = "intfloat/e5-base-v2"
COLLECTION_NAME = "academic_handbook_2025_26"


def get_collection():
    embed_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL_NAME
    )
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_func,
    )


def meta_tag(meta: dict[str, Any]) -> str:
    cl = meta.get("clause") or "—"
    pt = meta.get("part") or "—"
    sec = meta.get("section") or "—"
    return f"[Clause {cl} | Part {pt} | Section {sec}]"


def retrieve(
    collection,
    query: str,
    top_k: int,
) -> list[tuple[str, dict[str, Any], float]]:
    res = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    sims = [1.0 - float(d) for d in dists]
    return list(zip(docs, metas, sims))


def build_context_block(results: list[tuple[str, dict[str, Any], float]]) -> str:
    lines = []
    for doc, meta, _ in results:
        snippet = doc.strip()
        if len(snippet) > 1200:
            snippet = snippet[:1200] + "…"
        lines.append(f"{meta_tag(meta)}\n{snippet}")
    return "\n\n".join(lines)


def similarity_line(results: list[tuple[str, dict[str, Any], float]]) -> str:
    parts = []
    for i, (_, meta, sim) in enumerate(results, 1):
        cl = meta.get("clause") or "—"
        parts.append(f"Rank {i}: clause {cl}, similarity ≈ {sim:.3f}")
    return "\n".join(parts)


def format_similarity_scores_csv(results: list[tuple[str, dict[str, Any], float]]) -> str:
    """Semicolon-separated scores (rank order)."""
    return ";".join(f"{sim:.4f}" for _, _, sim in results)


def format_retrieved_clauses_csv(results: list[tuple[str, dict[str, Any], float]]) -> str:
    """Clause ids only, semicolon-separated (empty string if heading chunk has no clause)."""
    ids = []
    for _, meta, _ in results:
        cl = meta.get("clause")
        ids.append(str(cl).strip() if cl else "")
    return ";".join(ids)
