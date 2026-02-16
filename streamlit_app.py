"""
Netflix Metadata Extractor - Streamlit Demo
Run with: streamlit run streamlit_app.py
"""
import os
import time
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.extractor import NetflixExtractor
from src.schemas import ContentMetadata


# --- Page Configuration ---
st.set_page_config(
    page_title="Netflix Metadata Extractor",
    page_icon="🎬",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #E50914;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #808080;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        color: white;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #E50914;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #b0b0b0;
        margin-top: 0.3rem;
    }
    .success-badge {
        background: #0d7a3e;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
    }
    .fail-badge {
        background: #E50914;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
    }
    .genre-tag {
        background: #2d2d44;
        color: #E8E8E8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 2px 4px;
    }
    div[data-testid="stTabs"] button {
        font-size: 1.05rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Sample Descriptions ---
SAMPLE_DESCRIPTIONS = {
    "Select a sample...": "",
    "🧬 Sci-Fi Drama (3%)": "In a future where the elite inhabit an island paradise far from the crowded slums, you get one chance to join the 3% saved from squalor.",
    "🌍 Disaster Thriller (7:19)": "After a devastating earthquake hits Mexico City, trapped survivors from all walks of life wait to be rescued while trying desperately to stay alive.",
    "👻 Horror Mystery (23:59)": "When an army recruit is found dead, his fellow soldiers are forced to confront a terrifying secret that's haunting their jungle island training camp.",
    "🃏 Crime Thriller (21)": "A brilliant group of students become card-counting experts with the intent of swindling millions out of Las Vegas casinos by playing blackjack.",
    "🏫 Social Drama (187)": "After one of his high school students attacks him, dedicated teacher Trevor Garfield grows weary of the gang warfare in the New York City school system and moves to California to teach there, thinking it must be a less hostile environment.",
}


# --- Initialize Extractor ---
@st.cache_resource
def get_extractor():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return NetflixExtractor(api_key=api_key)


def display_metadata(metadata: ContentMetadata, col=None):
    """Display extracted metadata with styled formatting."""
    target = col if col else st

    # Genres as tags
    genres_html = " ".join(f'<span class="genre-tag">{g}</span>' for g in metadata.genres)
    target.markdown(f"**Genres:** {genres_html}", unsafe_allow_html=True)

    # Themes as tags
    themes_html = " ".join(f'<span class="genre-tag">{t}</span>' for t in metadata.themes)
    target.markdown(f"**Themes:** {themes_html}", unsafe_allow_html=True)

    # Mood and audience
    target.markdown(f"**Mood:** {metadata.mood}")
    target.markdown(f"**Target Audience:** {metadata.target_audience}")

    # Content warnings
    if metadata.content_warnings:
        warnings_html = " ".join(f'<span class="genre-tag">⚠️ {w}</span>' for w in metadata.content_warnings)
        target.markdown(f"**Content Warnings:** {warnings_html}", unsafe_allow_html=True)
    else:
        target.markdown("**Content Warnings:** None detected")


def display_metrics(elapsed_time: float, retries: int, success: bool):
    """Display extraction metrics in a row."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{elapsed_time:.2f}s</div>
            <div class="metric-label">Extraction Time</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{retries}</div>
            <div class="metric-label">Retries Needed</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        badge = "success-badge" if success else "fail-badge"
        status = "✓ Valid" if success else "✗ Failed"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value"><span class="{badge}">{status}</span></div>
            <div class="metric-label">Schema Validation</div>
        </div>
        """, unsafe_allow_html=True)


# =========================
# MAIN APP
# =========================
st.markdown('<div class="main-header">🎬 Netflix Metadata Extractor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered content metadata extraction using Claude · Built with Anthropic API + Pydantic</div>', unsafe_allow_html=True)

extractor = get_extractor()

if extractor is None:
    st.error("⚠️ ANTHROPIC_API_KEY not found. Please set it in your `.env` file.")
    st.stop()

# --- Tabs ---
tab1, tab2 = st.tabs(["🎯 Single Extraction", "📦 Batch Processing"])

# =========================
# TAB 1: Single Extraction
# =========================
with tab1:
    st.markdown("### Extract metadata from a movie or show description")

    # Sample dropdown
    sample = st.selectbox("Try a sample description:", list(SAMPLE_DESCRIPTIONS.keys()))
    sample_text = SAMPLE_DESCRIPTIONS.get(sample, "")

    # Text input
    description = st.text_area(
        "Or enter your own description:",
        value=sample_text,
        height=120,
        placeholder="Paste a movie or show description here..."
    )

    # Extract button
    if st.button("🚀 Extract Metadata", type="primary", use_container_width=True):
        if not description.strip():
            st.warning("Please enter a description first.")
        else:
            with st.spinner("Extracting metadata with Claude..."):
                start = time.time()
                result = extractor.extract(description)
                elapsed = time.time() - start

            # Metrics row
            st.markdown("---")
            display_metrics(elapsed, result["retries"], result["success"])
            st.markdown("---")

            if result["success"]:
                # Two columns: visual + raw JSON
                col1, col2 = st.columns([3, 2])

                with col1:
                    st.markdown("### 📋 Extracted Metadata")
                    display_metadata(result["metadata"])

                with col2:
                    st.markdown("### 🔧 Raw JSON Output")
                    st.json(result["metadata"].model_dump())
            else:
                st.error(f"Extraction failed: {result['error']}")
                if result.get("raw_response"):
                    with st.expander("See raw API response"):
                        st.code(result["raw_response"])

# =========================
# TAB 2: Batch Processing
# =========================
with tab2:
    st.markdown("### Process multiple descriptions at once")
    st.markdown("Upload a CSV with `Title` and `Description` columns.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        # Validate columns
        required_cols = {"Title", "Description"}
        if not required_cols.issubset(set(df.columns)):
            # Try case-insensitive match
            col_map = {c.lower(): c for c in df.columns}
            if "title" in col_map and "description" in col_map:
                df = df.rename(columns={col_map["title"]: "Title", col_map["description"]: "Description"})
            else:
                st.error(f"CSV must have 'Title' and 'Description' columns. Found: {list(df.columns)}")
                st.stop()

        df_clean = df[["Title", "Description"]].dropna()
        st.markdown(f"**Found {len(df_clean)} rows with descriptions.**")

        # Preview
        with st.expander("Preview data"):
            st.dataframe(df_clean.head(10))

        # Slider for number to process
        n = st.slider("Number of descriptions to process:", min_value=1, max_value=min(100, len(df_clean)), value=min(10, len(df_clean)))

        if st.button("🚀 Process Batch", type="primary", use_container_width=True):
            items = [
                {"title": row["Title"], "description": row["Description"]}
                for _, row in df_clean.head(n).iterrows()
            ]

            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []

            start = time.time()
            for i, item in enumerate(items):
                status_text.text(f"Processing {i+1}/{n}: {item['title']}...")
                result = extractor.extract(item["description"])
                result["title"] = item["title"]
                result["description"] = item["description"]
                results.append(result)
                progress_bar.progress((i + 1) / n)

            elapsed = time.time() - start
            status_text.text(f"Done! Processed {n} descriptions in {elapsed:.1f}s")

            # --- Batch Metrics ---
            st.markdown("---")
            successes = sum(1 for r in results if r["success"])
            first_try = sum(1 for r in results if r["success"] and r["retries"] == 0)
            retried = sum(1 for r in results if r["success"] and r["retries"] > 0)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Processed", n)
            with col2:
                st.metric("Success Rate", f"{successes/n*100:.0f}%")
            with col3:
                st.metric("1st Try Success", f"{first_try/n*100:.0f}%")
            with col4:
                st.metric("Avg Time", f"{elapsed/n:.1f}s")

            st.markdown("---")

            # --- Results Table ---
            rows = []
            for r in results:
                if r["success"]:
                    m = r["metadata"]
                    rows.append({
                        "Title": r["title"],
                        "Genres": ", ".join(m.genres),
                        "Themes": ", ".join(m.themes),
                        "Mood": m.mood,
                        "Audience": m.target_audience,
                        "Warnings": ", ".join(m.content_warnings) if m.content_warnings else "None",
                        "Retries": r["retries"],
                        "Status": "✓"
                    })
                else:
                    rows.append({
                        "Title": r["title"],
                        "Genres": "",
                        "Themes": "",
                        "Mood": "",
                        "Audience": "",
                        "Warnings": "",
                        "Retries": r["retries"],
                        "Status": "✗"
                    })

            results_df = pd.DataFrame(rows)
            st.dataframe(results_df, use_container_width=True)

            # --- Download Results ---
            csv_data = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_data,
                file_name="netflix_extraction_results.csv",
                mime="text/csv",
                use_container_width=True
            )

            # --- Download full JSON ---
            json_results = []
            for r in results:
                entry = {
                    "title": r["title"],
                    "description": r["description"],
                    "success": r["success"],
                    "retries": r["retries"],
                }
                if r["success"]:
                    entry["metadata"] = r["metadata"].model_dump()
                else:
                    entry["error"] = r["error"]
                json_results.append(entry)

            st.download_button(
                label="📥 Download Full Results as JSON",
                data=json.dumps(json_results, indent=2),
                file_name="netflix_extraction_results.json",
                mime="application/json",
                use_container_width=True
            )

# --- Sidebar ---
with st.sidebar:
    st.markdown("## About This Project")
    st.markdown("""
    This app uses **Claude** (Anthropic API) to extract structured metadata from Netflix show and movie descriptions.

    **How it works:**
    1. A description is sent to Claude with a structured prompt
    2. Claude returns JSON with genres, themes, mood, audience, and warnings
    3. The response is validated with Pydantic schemas
    4. If validation fails, the system retries with error feedback

    **Tech Stack:**
    - 🤖 Anthropic Claude API
    - 📐 Pydantic for validation
    - 🐍 Python
    - 🎈 Streamlit
    """)

    st.markdown("---")
    st.markdown("## Architecture")
    st.markdown("""
```
    Description
        ↓
    Prompt Engineering
        ↓
    Claude API (temp=0)
        ↓
    JSON Parsing
        ↓
    Pydantic Validation
        ↓
    Retry (if needed)
        ↓
    Structured Output
```
    """)

    st.markdown("---")
    st.markdown("Built by **Candace Grant** · [Portfolio](https://rpubs.com/Candace63)")