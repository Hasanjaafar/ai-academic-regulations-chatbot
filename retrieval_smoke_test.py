# -*- coding: utf-8 -*-
"""
Smoke-test handbook retrieval (Chroma + e5-base-v2). Run from project root:

    python retrieval_smoke_test.py

Requires an existing collection built with upgrade_embeddings.ipynb / Meta_data.ipynb:
  data/chroma_db_handbook  collection: academic_handbook_2025_26
"""
from __future__ import annotations

import sys
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

# Match Meta_data.ipynb / upgrade_embeddings.ipynb
EMBED_MODEL_NAME = "intfloat/e5-base-v2"
CHROMA_PATH = "data/chroma_db_handbook"
COLLECTION_NAME = "academic_handbook_2025_26"
TOP_K = 3

# (topic label, query text)
QUERIES: list[tuple[str, str]] = [
    ("coursework late submission", "Late coursework submission penalties and extensions"),
    ("progression and award boards", "Progression and Award Board ratification decisions"),
    ("English language requirements", "English language proficiency requirement for international students"),
    ("RPL / RPCL", "Recognition of prior certificated learning RPCL credit"),
    ("RPL / RPCL", "Prior experiential learning RPEL criteria"),
    ("assessment principles", "Principles of assessment intended learning outcomes"),
    ("exams / late arrival", "Examination late arrival missing the start"),
    ("exams / late arrival", "In-class test or examination attendance rules"),
    ("coursework late submission", "Coursework submitted after deadline without extension"),
    ("assessment principles", "Board of Examiners and external examiner"),
]


def main() -> int:
    root = Path(__file__).resolve().parent
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    embed_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL_NAME
    )
    client = chromadb.PersistentClient(path=str(root / CHROMA_PATH))
    try:
        col = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embed_func,
        )
    except Exception as e:
        print(
            "Could not open collection %r under %s\n%s"
            % (COLLECTION_NAME, root / CHROMA_PATH, e),
            file=sys.stderr,
        )
        print(
            "Build the index first (upgrade_embeddings.ipynb or Meta_data.ipynb).",
            file=sys.stderr,
        )
        return 1

    width = 72
    for topic, q in QUERIES:
        print("=" * width)
        print("TOPIC:", topic)
        print("QUERY:", q)
        res = col.query(
            query_texts=[q],
            n_results=TOP_K,
            include=["documents", "metadatas", "distances"],
        )
        docs = res["documents"][0]
        metas = res["metadatas"][0]
        dists = res["distances"][0]
        for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists), 1):
            sim = 1.0 - float(dist)
            cl = meta.get("clause") or "—"
            pt = meta.get("part") or "—"
            sec = meta.get("section") or "—"
            preview = " ".join(doc.split())[:420]
            print("  %d. sim=%.3f | part=%s sec=%s clause=%s" % (i, sim, pt, sec, cl))
            print("     %s" % preview)
            if len(preview) >= 420:
                print("     …")
        print()

    print("Done. (%d queries × top-%d)" % (len(QUERIES), TOP_K))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
