# app/streamlit_app.py
# -*- coding: utf-8 -*-
"""Streamlit UI for the University of Westminster Handbook of Academic Regulations RAG chatbot."""
import datetime
import html
import json
import os
import sys
import traceback
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _APP_DIR.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

from evaluation.prompt_templates import build_prompt as build_evaluation_prompt
from theme_inject import inject_app_theme

PROJECT_ROOT = _PROJECT_ROOT
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma_db_handbook"
CHUNKS_JSON = PROJECT_ROOT / "data" / "processed" / "academic_handbook_2025_26_chunks.json"

# ------------------------------
# 0) BOOTSTRAP
# ------------------------------
load_dotenv()
try:
    if not os.getenv("OPENAI_API_KEY") and "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

OPENAI_MODEL_DEFAULT = "gpt-4o-mini"

EMBED_MODEL_NAME = "intfloat/e5-base-v2"
COLLECTION_NAME = "academic_handbook_2025_26"
DOCUMENT_SHORT = "Handbook of Academic Regulations 2025–2026"
PROMPT_STYLE_OPTIONS = {
    "strict": "Prompt A - Strict grounding",
    "semi_flexible": "Prompt B - Semi-flexible",
    "loose": "Prompt C - Loose",
}

# ------------------------------
# 1) PAGE CONFIG + STYLE
# ------------------------------
st.set_page_config(
    page_title="Westminster Academic Regulations Assistant",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_app_theme()

@st.cache_resource(show_spinner=False)
def get_openai_client():
    try:
        return OpenAI()
    except Exception as e:
        st.error("No OpenAI API key found. Set OPENAI_API_KEY in your environment or .env file.")
        raise e


@st.cache_resource(show_spinner=False)
def get_collection():
    embed_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL_NAME
    )
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return chroma_client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_func,
    )

try:
    with open(CHUNKS_JSON, encoding="utf-8") as f:
        TOTAL_CHUNKS = len(json.load(f))
except Exception:
    TOTAL_CHUNKS = None

# ------------------------------
# 2) HELPERS
# ------------------------------
def normalize_query_english(user_query: str) -> str:
    """Handbook index is English; interface accepts English questions only."""
    return (user_query or "").strip()


def retrieve_context(query: str, top_k: int = 3):
    collection = get_collection()
    res = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    sims = [1 - float(d) for d in dists]
    return list(zip(docs, metas, sims))


def _meta_tag(meta: dict) -> str:
    cl = meta.get("clause") or "—"
    pt = meta.get("part") or "—"
    sec = meta.get("section") or "—"
    return f"[Clause {cl} | Part {pt} | Section {sec}]"


def build_context_block(results):
    lines = []
    for doc, meta, _ in results:
        snippet = doc.strip()
        if len(snippet) > 1200:
            snippet = snippet[:1200] + "…"
        lines.append(f"{_meta_tag(meta)}\n{snippet}")
    return "\n\n".join(lines)


def _retrieval_similarity_line(results) -> str:
    parts = []
    for i, (_, meta, sim) in enumerate(results, 1):
        cl = meta.get("clause") or "—"
        parts.append(f"Rank {i}: clause {cl}, similarity ≈ {sim:.3f}")
    return "\n".join(parts)


def build_prompt(user_q: str, context_block: str, results, prompt_style: str) -> str:
    sim_line = _retrieval_similarity_line(results)
    return build_evaluation_prompt(
        prompt_style=prompt_style,
        question=user_q,
        context_block=context_block,
        sim_line=sim_line,
    )


def generate_answer(model_name, prompt, temperature=0.2):
    client = get_openai_client()
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content


def render_message(text: str, sender: str):
    safe = html.escape(text or "")
    is_user = sender == "user"
    row_class = "chat-row-user" if is_user else "chat-row-bot"
    av_label = "You" if is_user else "AI"
    av_class = "user-av" if is_user else "bot-av"
    bubble_class = "user" if is_user else "bot"
    st.markdown(
        f'<div class="chat-row {row_class}">'
        f'<div class="chat-avatar {av_class}">{av_label}</div>'
        f'<div class="msg {bubble_class}">{safe}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_retrieved_clauses_topk(results):
    """Transparency for examiners: which clauses were retrieved (Top-K)."""
    lines_html = []
    for i, (_, meta, sim) in enumerate(results, 1):
        cl = meta.get("clause") or ""
        label = f"Clause {cl}" if cl else "Section / heading (no clause id)"
        lines_html.append(
            f'<div class="retrieval-line">{i}. <strong>{html.escape(label)}</strong> — similarity ≈ {sim:.3f}</div>'
        )
    st.markdown(
        '<div class="retrieval-panel"><h4>Retrieved clauses (Top-K)</h4>'
        + "".join(lines_html)
        + "</div>",
        unsafe_allow_html=True,
    )


def render_sources(results):
    with st.expander("View full source excerpts", expanded=False):
        for doc, meta, sim in results:
            cl = meta.get("clause") or "—"
            body = doc[:1200] + "…" if len(doc) > 1200 else doc
            st.markdown(
                f"""
                <div class="src-card">
                  <div class="src-title">Clause {html.escape(str(cl))} <span class="badge">≈ {sim:.2f}</span></div>
                  <div class="src-meta">{html.escape(DOCUMENT_SHORT)}</div>
                  <div style="margin-top: 10px; font-size: 0.88rem; line-height: 1.55; color: #334155;">{html.escape(body)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def log_interaction(question, answer, results):
    if not question or not answer:
        return
    os.makedirs(PROJECT_ROOT / "logs", exist_ok=True)
    log_path = PROJECT_ROOT / "logs" / "chat_logs.jsonl"
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "retrieved_clauses": [_meta_tag(m) for _, m, _ in results],
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def initialize_session_state():
    defaults = {
        "history": [],
        "conversation_memory": [],
        "feedback_given": False,
        "last_feedback": None,
        "last_question": None,
        "last_answer": None,
        "last_results": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_conversation():
    st.session_state["history"] = []
    st.session_state["conversation_memory"] = []
    st.session_state["last_question"] = None
    st.session_state["last_answer"] = None
    st.session_state["last_results"] = []
    st.session_state["feedback_given"] = False
    st.session_state["last_feedback"] = None


# ------------------------------
# 3) SIDEBAR
# ------------------------------
initialize_session_state()

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
          <div class="sidebar-brand-title">Regulations Assistant</div>
          <div class="sidebar-brand-sub">University of Westminster · RAG</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.header("Settings")
    st.caption("English questions only — answers in English.")

    st.markdown("### Model & retrieval")
    model_name = st.selectbox(
        "Response model",
        [OPENAI_MODEL_DEFAULT, "gpt-4o"],
        key="model_name",
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05, key="temperature")
    top_k = st.slider("Chunks to retrieve", 1, 7, 3, 1, key="top_k")
    prompt_style = st.selectbox(
        "Prompt style",
        list(PROMPT_STYLE_OPTIONS.keys()),
        format_func=lambda style: PROMPT_STYLE_OPTIONS[style],
        key="prompt_style",
    )
    st.caption("Prompt A/B/C matches the styles used in the evaluation experiments.")

    st.markdown("---")
    st.header("System")
    st.markdown(
        f"""
• **Embedding model:** `{EMBED_MODEL_NAME}`  
• **Collection:** `{COLLECTION_NAME}`  
• **Chroma path:** `{CHROMA_PATH.name}`  
"""
    )
    if TOTAL_CHUNKS:
        st.markdown(f"• **Indexed chunks:** `{TOTAL_CHUNKS}`")

    st.markdown("---")
    if st.button("Clear conversation"):
        reset_conversation()
        st.rerun()


# ------------------------------
# 4) HEADER
# ------------------------------
st.markdown(
    f"""
    <div class="app-hero">
      <div class="app-badge">Official handbook · RAG</div>
      <h1>Academic Regulations Assistant</h1>
      <p class="tagline">Grounded answers from the indexed <strong>{DOCUMENT_SHORT}</strong> (English). Ask about assessments, appeals, exams, progression, and more.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
if not st.session_state["history"]:
    st.markdown(
        """
        <div class="empty-state">
          <strong>Start a conversation</strong><br>
          Ask in <strong>English</strong>. The assistant retrieves matching clauses and answers with citations.
        </div>
        """,
        unsafe_allow_html=True,
    )
for msg in st.session_state["history"]:
    render_message(msg["content"], msg.get("role", "assistant"))
st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------
# 6) CHAT
# ------------------------------
user_q = st.chat_input("Ask about assessments, mitigating circumstances, progression, exams…")
active_question = user_q

if active_question:
    st.session_state["history"].append({"role": "user", "content": active_question})
    render_message(active_question, "user")

    try:
        with st.spinner("Searching the handbook and generating an answer…"):
            model_name = st.session_state["model_name"]
            temperature = st.session_state["temperature"]
            top_k = st.session_state["top_k"]
            prompt_style = st.session_state["prompt_style"]
            retrieval_query = normalize_query_english(active_question)
            results = retrieve_context(retrieval_query, top_k=top_k)
            ctx = build_context_block(results)
            prompt = build_prompt(active_question, ctx, results, prompt_style)
            answer = generate_answer(model_name, prompt, temperature=temperature)

        render_message(answer, "assistant")
        st.session_state["history"].append({"role": "assistant", "content": answer})
        st.session_state["conversation_memory"].append(
            {"question": active_question, "answer": answer}
        )
        render_retrieved_clauses_topk(results)
        render_sources(results)
        st.session_state["last_question"] = active_question
        st.session_state["last_answer"] = answer
        st.session_state["last_results"] = results
        st.session_state["feedback_given"] = False

        log_interaction(active_question, answer, results)

    except Exception as e:
        st.error("Something went wrong while generating the answer.")
        st.code("".join(traceback.format_exc()), language="python")


if st.session_state.get("last_answer"):
    try:
        _fb = st.container(border=True)
    except TypeError:
        _fb = st.container()
    with _fb:
        st.markdown("##### Was this answer helpful?")
        col1, col2 = st.columns(2)
        os.makedirs(PROJECT_ROOT / "logs", exist_ok=True)
        feedback_path = PROJECT_ROOT / "logs" / "feedback.jsonl"

        if "feedback_given" not in st.session_state:
            st.session_state["feedback_given"] = False

        clicked_yes = col1.button("Yes", disabled=st.session_state["feedback_given"])
        clicked_no = col2.button("No", disabled=st.session_state["feedback_given"])

        if clicked_yes and not st.session_state["feedback_given"]:
            st.session_state["feedback_given"] = True
            st.session_state["last_feedback"] = True
            with open(feedback_path, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "question": st.session_state.get("last_question"),
                            "answer": st.session_state.get("last_answer"),
                            "helpful": True,
                            "timestamp": datetime.datetime.now().isoformat(),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            st.success("Thanks — feedback saved.")

        elif clicked_no and not st.session_state["feedback_given"]:
            st.session_state["feedback_given"] = True
            st.session_state["last_feedback"] = False
            with open(feedback_path, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "question": st.session_state.get("last_question"),
                            "answer": st.session_state.get("last_answer"),
                            "helpful": False,
                            "timestamp": datetime.datetime.now().isoformat(),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            st.warning("Feedback recorded.")


st.markdown(
    """
    <div class="app-footer">
    <strong>Disclaimer</strong> — This tool retrieves excerpts from the University of Westminster Handbook of Academic Regulations.
    It is not a substitute for formal advice from the Academic Registrar’s Department. For decisions affecting your studies, use the official handbook and university staff.
    </div>
    """,
    unsafe_allow_html=True,
)
