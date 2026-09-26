"""Shared visual identity for the Streamlit frontend.

Palette/type choices are grounded in the subject (a clinical/instrument feel
for a biomedical research tool) rather than Streamlit's defaults — see
`inject_theme()` for the token system. Call `inject_theme()` once near the
top of every page, before any other `st.` calls that render content.
"""
from __future__ import annotations

import html

import streamlit as st

_SOURCE_COLORS = {
    "pubmed": ("#0B6E68", "#E6F2F0"),  # teal
    "semantic_scholar": ("#3B5BA5", "#E8ECF8"),  # indigo
    "chembl": ("#C98A2C", "#FBF0DD"),  # amber
    "rag_index": ("#6B5B95", "#EFEAF6"),  # muted violet — locally indexed
}
_SOURCE_LABELS = {
    "pubmed": "PubMed",
    "semantic_scholar": "Semantic Scholar",
    "chembl": "ChEMBL",
    "rag_index": "Indexed",
}

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@500;600;700&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #F4F6F5;
  --surface: #FFFFFF;
  --surface-alt: #EAF1EF;
  --border: #D3DDDA;
  --text: #142723;
  --text-muted: #55696A;
  --primary: #0B6E68;
  --primary-dark: #054D48;
  --accent: #C98A2C;
  --accent-ink: #6B4B14;
  --danger: #B84C3C;
  --success: #2E7D5B;
  --font-display: "Zilla Slab", Georgia, serif;
  --font-body: "Public Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0D1614;
    --surface: #14201D;
    --surface-alt: #1B2926;
    --border: #2A3A36;
    --text: #E7EFEC;
    --text-muted: #9FB4AF;
    --primary: #49C6B9;
    --primary-dark: #2E9C90;
    --accent: #E0AA52;
    --accent-ink: #2A1D06;
    --danger: #E08574;
    --success: #6FCB9F;
  }
}

html, body, [class*="css"] { font-family: var(--font-body); }
h1, h2, h3, .app-hero h1, .app-hero p.kicker {
  font-family: var(--font-display) !important;
  letter-spacing: -0.01em;
}
[data-testid="stAppViewContainer"] { background: var(--bg); }
[data-testid="stSidebar"] { background: var(--surface-alt); border-right: 1px solid var(--border); }

.app-hero {
  border: 1px solid var(--border);
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface-alt) 100%);
  border-radius: 14px;
  padding: 28px 32px;
  margin-bottom: 28px;
}
.app-hero p.kicker {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary);
  margin: 0 0 6px 0;
}
.app-hero h1 { font-size: 1.9rem; margin: 0 0 10px 0; color: var(--text); text-wrap: balance; }
.app-hero p.lede { font-family: var(--font-body); color: var(--text-muted); font-size: 1.02rem; max-width: 60ch; margin: 0; }

.stat-row { display: flex; gap: 14px; margin-top: 20px; flex-wrap: wrap; }
.stat-chip {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 16px;
  min-width: 130px;
}
.stat-chip .n { font-family: var(--font-mono); font-size: 1.3rem; color: var(--primary); font-weight: 600; }
.stat-chip .label { font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }

.domain-badge {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  padding: 3px 9px;
  border-radius: 999px;
  background: var(--surface-alt);
  border: 1px solid var(--border);
  color: var(--primary-dark);
  margin-bottom: 8px;
}

.ref-card {
  border: 1px solid var(--border);
  border-left: 3px solid var(--primary);
  background: var(--surface);
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 8px;
}
.ref-card .ref-title { font-weight: 600; color: var(--text); font-size: 0.94rem; }
.ref-card .ref-title a { color: var(--text); text-decoration: none; border-bottom: 1px solid var(--border); }
.ref-card .ref-title a:hover { border-bottom-color: var(--primary); }
.ref-card .ref-snippet { color: var(--text-muted); font-size: 0.85rem; margin-top: 3px; }
.ref-card .ref-error { color: var(--danger); font-size: 0.85rem; }

.source-pill {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.02em;
  padding: 2px 8px;
  border-radius: 999px;
  margin-bottom: 6px;
  font-weight: 600;
}

.tool-call-label {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--text-muted);
}

hr.section-rule { border: none; border-top: 1px solid var(--border); margin: 18px 0; }
</style>
"""


def inject_theme() -> None:
    # st.markdown(..., unsafe_allow_html=True) routes raw HTML through
    # Streamlit's markdown-sanitization pipeline, which doesn't reliably
    # treat <style> as a raw-text element — it can strip the tag but leave
    # its CSS text behind as visible content. st.html() renders the string
    # directly into the DOM instead, so the stylesheet actually applies.
    st.html(CSS)


def hero(kicker: str, title: str, lede: str, stats: list[tuple[str, str]] | None = None) -> None:
    stats_html = ""
    if stats:
        chips = "".join(
            f'<div class="stat-chip"><div class="n">{html.escape(n)}</div>'
            f'<div class="label">{html.escape(label)}</div></div>'
            for n, label in stats
        )
        stats_html = f'<div class="stat-row">{chips}</div>'

    st.html(
        f"""
        <div class="app-hero">
            <p class="kicker">{html.escape(kicker)}</p>
            <h1>{html.escape(title)}</h1>
            <p class="lede">{html.escape(lede)}</p>
            {stats_html}
        </div>
        """
    )


def domain_badge(text: str) -> None:
    st.html(f'<div class="domain-badge">{html.escape(text)}</div>')


def source_pill_html(source: str) -> str:
    fg, bg = _SOURCE_COLORS.get(source, ("#55696A", "#EAF1EF"))
    label = _SOURCE_LABELS.get(source, source or "source")
    return f'<span class="source-pill" style="color:{fg};background:{bg};">{html.escape(label)}</span>'
