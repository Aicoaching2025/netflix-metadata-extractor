# 🎬🍿 Netflix Metadata Extractor

### *AI-Powered Content Intelligence for Streaming Platforms*

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)
![Anthropic](https://img.shields.io/badge/Claude_API-Anthropic-cc785c?style=for-the-badge&logo=anthropic&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-Validated-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

**🎥 Extract genres, themes, mood & more from any movie or show description in seconds**

[🚀 **Try the Live App**](https://candace-ai.streamlit.app) · [📊 **View Portfolio**](https://rpubs.com/Candace63)

---

</div>

## 🌟 What Does It Do?

Ever wondered how streaming platforms tag thousands of titles with the right genres, moods, and content warnings? This project automates that process using **Claude AI**.

Drop in any movie or show description, and the extractor instantly returns:

| 🎭 Field | 📝 Example Output |
|---|---|
| **Genres** | `Sci-Fi`, `Drama`, `Thriller` |
| **Themes** | `survival`, `identity`, `power` |
| **Mood** | `dark`, `suspenseful`, `lighthearted` |
| **Audience** | `adults`, `teens`, `kids`, `family` |
| **Warnings** | `violence`, `language`, `frightening scenes` |

---

## 🎞️ How It Works

```
📝 Description
      ⬇️
🧠 Prompt Engineering
      ⬇️
🤖 Claude API (temperature=0)
      ⬇️
🔧 JSON Parsing + Cleanup
      ⬇️
✅ Pydantic Validation
      ⬇️
🔄 Auto-Retry (if needed)
      ⬇️
🎉 Structured Metadata Output
```

---

## 🏆 Evaluation Results

Tested on **60 Netflix titles** (10 manually annotated + 50 random samples):

| Metric | Score |
|---|---|
| ✅ Schema Compliance (1st try) | **100%** |
| ✅ Overall Success Rate | **100%** |
| 🎭 Genre Accuracy | **83.3%** |
| 👥 Target Audience Accuracy | **90.0%** |
| ⚠️ Content Warnings Accuracy | **85.0%** |
| 🎨 Mood Accuracy | **60.0%** |
| 📖 Theme Accuracy | **17.8%** |
| 🔄 Retry Rate | **0.0%** |

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/Aicoaching2025/netflix-metadata-extractor.git
cd netflix-metadata-extractor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Add Your API Key
Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Run It!
```bash
# 🧪 Test on 5 descriptions
python app.py test

# 📊 Full evaluation (60 descriptions)
python app.py evaluate

# 💬 Interactive mode
python app.py extract

# 🌐 Launch the web app
streamlit run streamlit_app.py
```

---

## 🎬 Features

### 🎯 Single Extraction
Paste any movie or show description and get instant structured metadata. Try one of the built-in samples or bring your own.

### 📦 Batch Processing
Upload a CSV with hundreds of titles and process them all at once. Download results as CSV or JSON.

### 🔄 Smart Retry Logic
If the AI response doesn't validate on the first try, the system automatically retries with error feedback — up to 2 times.

### ✅ Schema Validation
Every response is validated through Pydantic models to ensure consistent, reliable output every time.

---

## 📁 Project Structure

```
🎬 netflix-metadata-extractor/
│
├── 🧠 src/
│   ├── extractor.py      → Claude API calls + retry logic
│   ├── prompts.py         → Engineered prompt templates
│   ├── schemas.py         → Pydantic ContentMetadata model
│   └── evaluation.py      → Metrics & evaluation pipeline
│
├── 📊 data/
│   └── ground_truth.py    → 10 manually annotated examples
│
├── 🧪 tests/
│   └── test_extractor.py  → 13 unit tests + 3 integration tests
│
├── 🖥️ streamlit_app.py    → Interactive web demo
├── 🔧 app.py              → CLI entry point
├── 📋 requirements.txt
└── 🔒 .env                → API keys (not committed)
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| 🤖 **Anthropic Claude API** | LLM-powered metadata extraction |
| 📐 **Pydantic** | Response validation & schema enforcement |
| 🐼 **Pandas** | Data loading & manipulation |
| 🎈 **Streamlit** | Interactive web application |
| 🧪 **Pytest** | Automated testing suite |
| 🐍 **Python 3.13** | Core language |

---

## 👩🏽‍💻 Built By

**Candace Grant**
Lead STEM Teacher & Data Science Graduate Student

🔗 [Portfolio](https://rpubs.com/Candace63) · 🐙 [GitHub](https://github.com/Aicoaching2025)

---

<div align="center">

*🍿 Grab some popcorn and try the app! 🍿*

</div>
