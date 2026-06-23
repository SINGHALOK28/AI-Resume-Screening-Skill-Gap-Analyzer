---
title: AI Resume Screener
emoji: 📄
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
---

# 📄 AI Resume Screening & Ranking System

An end-to-end intelligent recruitment solution that automates the resume screening process using Advanced NLP, Semantic Matching, and AI-driven insights. This system helps recruiters identify top talent by matching resumes against Job Descriptions (JD) with high precision.

---

## 🌟 Summary
The **AI Resume Screening System** bridges the gap between manual recruitment and automated efficiency. By leveraging **Sentence Transformers** and **Heuristic Extraction**, it provides a multidimensional analysis of candidates, including skill gap analysis, experience verification, and ATS compatibility checks.

---

## 🚀 Key Features

### 🔍 Core Analysis
- **Advanced Resume Parsing**: High-accuracy extraction from PDF and DOCX using OCR and structured parsing.
- **Semantic Match Scoring**: Deep learning-based similarity calculation between candidate profiles and job requirements.
- **Skill Gap Analysis**: Automated identification of "Must-Have" vs. "Nice-to-Have" skills.
- **Critical Skill Weighting**: Recruiter-defined importance for specific technical competencies.

### 📈 Intelligence & Insights
- **ATS Compatibility Checker**: Scans for resume formatting issues and keyword optimization.
- **Experience Profiling**: Automatically extracts years of experience and matches against JD seniority requirements.
- **AI Recommendations**: Personalized feedback for candidates on how to improve their match score.
- **Interview Question Generator**: Tailored questions based on the candidate's missing skills and experience.

### 🛠️ User Experience
- **Interactive Dashboard**: Real-time feedback and visualization of scores.
- **Group Screening**: Compare dozens of resumes simultaneously to rank the top candidates.
- **Exportable Reports**: Generate professional PDF analysis reports for hiring managers.

---

## ⚙️ How It Works (The Pipeline)

The system operates in four distinct stages:

1.  **Preprocessing**: Resumes are converted to clean text. OCR is utilized for scanned PDFs to ensure no data is missed.
2.  **Extraction & Normalization**: 
    -   Skills are extracted using a combination of pattern matching and a comprehensive skill database.
    -   Entities like Experience, Contact Info, and Education are parsed into structured formats.
    -   Skills are normalized (e.g., "JS", "Javascript", "ES6" all map to "JavaScript").
3.  **Analysis Engine**:
    -   **Semantic Engine**: Computes vector similarity between the JD and Resume.
    -   **Tiered Scoring**: Evaluates candidates based on "Must-Have" vs "Nice-to-Have" skill tiers.
    -   **Experience Fit**: Calculates the delta between required and actual years of experience.
4.  **Generation Layer**:
    -   Generates learning paths for missing skills.
    -   Rewrites resume bullet points for better ATS alignment.
    -   Creates a composite score breakdown for final ranking.

---

## � Project Structure

```text
ai-resume-screening/
├── analysis/               # Core scoring & logic
│   ├── anonymizer.py       # PII removal for unbiased screening
│   ├── ats_checker.py      # Format & keyword density analysis
│   ├── experience_extractor.py # Years of experience parsing
│   ├── jd_tier_parser.py   # Skill categorization (Must/Nice to have)
│   ├── pipeline.py         # Unified analysis entry point
│   └── score_breakdown.py  # Composite score calculation
├── config/                 # Customizable skill databases & profiles
├── embeddings/             # NLP & Semantic Search
│   ├── similarity_engine.py # Sentence-Transformers implementation
│   └── skill_extractor.py   # Pattern-based skill discovery
├── frontend/               # UI Components
│   ├── streamlit_app.py    # Main dashboard implementation
│   └── ui_components.py    # Reusable Streamlit widgets
├── generation/             # AI-driven content creation
│   ├── interview_questions.py # Dynamic question generation
│   ├── learning_paths.py    # Skill development suggestions
│   └── recommendation_generator.py # Match feedback
├── preprocessing/          # Data ingestion
│   ├── ocr_parser.py       # Scanned PDF support
│   └── resume_parser.py    # Text extraction logic
├── utils/                  # Helper functions & history management
├── app.py                  # Application entry point
├── Dockerfile              # Containerization config
└── requirements.txt        # Dependency list
```

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **NLP Models**: [Sentence-Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`)
- **Text Processing**: [spaCy](https://spacy.io/), [NLTK](https://www.nltk.org/)
- **Document Handling**: `PyPDF2`, `python-docx`, `pdf2image`, `pytesseract`
- **Visualization**: `Plotly`, `Pandas`

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Tesseract OCR (for scanned PDF support)

### Installation

1. **Clone & Navigate**:
   ```bash
   git clone <repo-url>
   cd ai-resume-screening
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. **Run Application**:
   ```bash
   streamlit run app.py
   ```

---

## 🐳 Docker Deployment

To run the system in a containerized environment:

```bash
docker build -t resume-screener .
docker run -p 8501:8501 resume-screener
```

---

## 🚀 Deployment Guide

To get your own live link, you can deploy this project using **Hugging Face Spaces** or **Streamlit Community Cloud**.

### 1. Deploying to Hugging Face Spaces (Recommended)
Hugging Face Spaces is ideal for this project as it natively supports Docker and Streamlit.

1.  **Create a Space**: Go to [Hugging Face Spaces](https://huggingface.co/new-space).
2.  **Configure**:
    - **Space Name**: `AI-Resume-Screener` (or your choice).
    - **SDK**: Select **Docker**.
    - **Template**: Choose **Blank**.
3.  **Upload Files**: Connect your GitHub repository or upload all project files (including the `Dockerfile`, `app.py`, and `requirements.txt`).
4.  **Build**: Hugging Face will automatically detect the `Dockerfile` and start building the container.
5.  **Live**: Once the build is "Running", your live link will be visible at the top!

### 2. Deploying to Streamlit Community Cloud
If you prefer a direct GitHub-to-Live workflow without Docker:

1.  **Push to GitHub**: Ensure your code is pushed to a public repository.
2.  **Sign in to Streamlit**: Go to [share.streamlit.io](https://share.streamlit.io/).
3.  **New App**: Click "New app" and select your repository, branch, and `app.py` as the main file.
4.  **Deploy**: Click "Deploy". Streamlit will install dependencies from `requirements.txt` and launch the app.

---

## 📺 Live Demo
You can access the live application here:
**[AI Resume Screening & Skill Gap Analyzer](https://huggingface.co/spaces/singhalok19/AI-Resume-Screener)**

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.