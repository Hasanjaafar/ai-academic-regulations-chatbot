# -*- coding: utf-8 -*-
"""Inject global CSS into the Streamlit parent document.

Streamlit's st.markdown often strips or exposes <style> blocks as plain text.
Loading styles via components + parent.document keeps them applied to the real page.
"""
import json

import streamlit.components.v1 as components

FONT_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"

APP_CSS = """
:root {
  --bg: #f0f4f8;
  --bg-gradient: linear-gradient(165deg, #f8fafc 0%, #eef2ff 45%, #f0f4f8 100%);
  --surface: #ffffff;
  --text: #0f172a;
  --text-muted: #64748b;
  --accent: #4f46e5;
  --accent-hover: #4338ca;
  --accent-soft: #eef2ff;
  --border: #e2e8f0;
  --shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 4px 12px rgba(15, 23, 42, 0.04);
  --shadow-lg: 0 12px 40px -12px rgba(15, 23, 42, 0.15);
  --radius: 16px;
  --radius-sm: 12px;
}

html, body, .stApp {
  font-family: "Inter", system-ui, -apple-system, sans-serif !important;
  background: var(--bg-gradient) !important;
  color: var(--text) !important;
}
[data-testid="stAppViewContainer"] {
  background: transparent !important;
}
.block-container {
  padding: 1.25rem 1.5rem 2rem !important;
  max-width: 920px !important;
}

.app-hero {
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #7c3aed 100%);
  border-radius: var(--radius);
  padding: 1.75rem 1.75rem 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-lg);
  color: #fff !important;
}
.app-hero h1 {
  font-size: 1.65rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 0.35rem 0;
  color: #fff !important;
  border: none;
}
.app-hero .tagline {
  font-size: 0.95rem;
  opacity: 0.92;
  margin: 0;
  font-weight: 400;
  line-height: 1.5;
}
.app-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: rgba(255,255,255,0.2);
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  margin-bottom: 0.75rem;
}

.chat-shell {
  min-height: 120px;
  margin-bottom: 0.5rem;
}
.empty-state {
  text-align: center;
  padding: 2.5rem 1.5rem;
  background: var(--surface);
  border-radius: var(--radius);
  border: 1px dashed var(--border);
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 1rem;
}
.empty-state strong { color: var(--text); }

.chat-row {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  margin-bottom: 1.15rem;
  animation: uwFadeIn 0.35s ease;
}
@keyframes uwFadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
.chat-row-user { flex-direction: row-reverse; }
.chat-avatar {
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 700;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}
.user-av {
  background: var(--accent-soft);
  color: var(--accent);
  border: 1px solid #c7d2fe;
}
.bot-av {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid var(--border);
}
.msg {
  flex: 1;
  min-width: 0;
  padding: 1rem 1.15rem;
  border-radius: var(--radius-sm);
  line-height: 1.65;
  word-wrap: break-word;
  white-space: pre-wrap;
  font-size: 0.9375rem;
  max-width: 100%;
}
.msg.user {
  background: linear-gradient(145deg, #4f46e5, #6366f1);
  color: #f8fafc !important;
  border: none;
  box-shadow: var(--shadow);
  border-bottom-right-radius: 6px;
}
.msg.bot {
  background: var(--surface);
  color: var(--text) !important;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  border-bottom-left-radius: 6px;
}

.retrieval-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 1rem 1.15rem;
  margin: 0.75rem 0 1rem;
  box-shadow: var(--shadow);
}
.retrieval-panel h4 {
  margin: 0 0 0.65rem 0;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}
.retrieval-line {
  font-size: 0.9rem;
  padding: 0.4rem 0;
  border-bottom: 1px solid #f1f5f9;
  color: var(--text);
}
.retrieval-line:last-child { border-bottom: none; }

.src-card {
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: var(--radius-sm);
  padding: 1rem 1.1rem;
  margin-bottom: 0.65rem;
  color: var(--text);
  box-shadow: 0 1px 2px rgba(15,23,42,0.04);
}
.src-title {
  font-weight: 600;
  color: var(--accent);
  font-size: 0.95rem;
}
.src-meta {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}
.badge {
  background: var(--accent-soft);
  color: var(--accent);
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.72rem;
  font-weight: 600;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #fafbfc 0%, #f1f5f9 100%) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdown"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdown"] h3 {
  font-size: 0.95rem !important;
  font-weight: 600 !important;
  color: var(--text) !important;
}
.sidebar-brand {
  padding: 0.5rem 0 1.25rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
}
.sidebar-brand-title {
  font-weight: 700;
  font-size: 1rem;
  color: var(--text);
  letter-spacing: -0.02em;
}
.sidebar-brand-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.stSelectbox label, .stSlider label {
  font-size: 0.85rem !important;
  font-weight: 500 !important;
}
[data-baseweb="select"] > div {
  border-radius: 10px !important;
}
.stSlider [data-baseweb="slider"] { padding-top: 0.5rem !important; }

.stChatInput textarea {
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow) !important;
  font-family: inherit !important;
}
.stChatInput {
  padding-bottom: 0.5rem;
}

.stButton>button {
  background: linear-gradient(180deg, #4f46e5, #4338ca) !important;
  color: #fff !important;
  border-radius: 12px !important;
  border: none !important;
  font-weight: 600 !important;
  padding: 0.5rem 1rem !important;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.35) !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
.stButton>button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4) !important;
}

.app-footer {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-align: center;
  margin-top: 2.5rem;
  padding: 1.25rem 1rem;
  line-height: 1.55;
  border-top: 1px solid var(--border);
  max-width: 52rem;
  margin-left: auto;
  margin-right: auto;
}

.stSpinner > div {
  border-color: var(--accent) transparent transparent transparent !important;
}

.streamlit-expanderHeader {
  font-weight: 600 !important;
  font-size: 0.9rem !important;
}
"""


def inject_app_theme() -> None:
    """Append Inter font + APP_CSS to parent document (idempotent)."""
    css_json = json.dumps(APP_CSS)
    href_json = json.dumps(FONT_URL)
    components.html(
        f"""
        <script>
        (function() {{
            try {{
                const p = window.parent.document;
                if (!p.getElementById("uw-reg-font")) {{
                    const l = p.createElement("link");
                    l.id = "uw-reg-font";
                    l.rel = "stylesheet";
                    l.href = {href_json};
                    p.head.appendChild(l);
                }}
                if (!p.getElementById("uw-reg-styles")) {{
                    const s = p.createElement("style");
                    s.id = "uw-reg-styles";
                    s.textContent = {css_json};
                    p.head.appendChild(s);
                }}
            }} catch (e) {{}}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )
