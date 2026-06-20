---
title: AI Resume Screener
emoji: 📄
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
---

# AI Resume Screening System

An intelligent resume screening and skill gap analysis system that leverages AI/ML to match resumes with job descriptions, extract skills, and provide actionable recommendations.

## 🚀 Features

- **Resume Parsing**: Supports PDF and DOCX formats with robust text extraction
- **Skill Extraction**: Advanced pattern matching to identify technical and soft skills
- **Semantic Matching**: Uses Sentence Transformers for semantic similarity calculation
- **Multi-Resume Comparison**: Compare multiple resumes against a single job description
- **Critical Skills Weighting**: Assign custom weights to critical job requirements
- **AI-Powered Recommendations**: Generate personalized improvement suggestions
- **PDF Export**: Comprehensive reports with analysis results
- **Real-time Analysis**: Interactive dashboard with instant feedback

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Interactive web UI)
- **NLP**: Sentence Transformers (all-MiniLM-L6-v2 model)
- **Text Processing**: spaCy, NLTK, PyPDF2, python-docx
- **PDF Generation**: ReportLab
- **Backend**: Python 3.x

## 📋 Prerequisites

- Python 3.8+
- pip package manager

## 📦 Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd ai-resume-screening
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## 🚀 Usage

1. Run the Streamlit application:
```bash
streamlit run app/streamlit_app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Enter candidate name (for PDF report naming)

4. Select analysis mode:
   - **Single Resume**: Detailed analysis of one resume
   - **Group Resumes**: Compare multiple resumes against job description

5. Upload resume(s) in PDF or DOCX format

6. Paste the job description

7. Click "Analyze" to get results

## 📊 Analysis Results

- **Match Score**: Overall compatibility percentage
- **Skills Comparison**: Skills found vs required
- **Missing Skills**: Identified gaps
- **Critical Skills Analysis**: Weighted scoring for important requirements
- **AI Recommendations**: Personalized improvement suggestions

## 🔧 Configuration

In the sidebar, you can:
- Define critical skills with custom weights
- Enable debug mode for extraction insights
- Access configuration options

## 📁 Project Structure

```
ai-resume-screening/
├── app/
│   └── streamlit_app.py          # Main Streamlit application with UI components
├── embeddings/
│   ├── __init__.py               # Package initializer
│   ├── similarity_engine.py      # Semantic similarity calculations using Sentence Transformers
│   └── skill_extractor.py        # Skill extraction and categorization with pattern matching
├── generation/
│   ├── __init__.py               # Package initializer
│   └── recommendation_generator.py # AI recommendation generation with template-based suggestions
├── preprocessing/
│   ├── __init__.py               # Package initializer
│   ├── resume_parser.py          # Resume text extraction from PDF/DOCX formats
│   ├── jd_parser.py              # Job description processing and cleaning
│   └── text_cleaner.py           # Text normalization utilities
├── tests/                        # Comprehensive test suite
│   ├── debug_similarity.py       # Similarity engine debugging tests
│   ├── debug_skills.py           # Skill extraction debugging tests
│   ├── full_pipeline_test.py     # End-to-end pipeline tests
│   ├── test_fixes.py             # Bug fix validation tests
│   ├── test_imports.py           # Import validation tests
│   ├── test_problematic_resume.py # Problematic resume handling tests
│   ├── test_recommendations.py   # Recommendation generation tests
│   └── test_skill_extraction.py  # Skill extraction validation tests
├── .gitignore                    # Git ignore rules
├── QUICKSTART.md                 # Quick start guide
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
└── run_app.bat                   # Windows startup script
```

## 🤖 AI/ML Components

- **Sentence Transformers**: Semantic similarity using all-MiniLM-L6-v2 model
- **Pattern Matching**: Regular expressions for skill extraction
- **Weighted Scoring**: Customizable importance for critical skills
- **Template-based Recommendations**: Context-aware improvement suggestions

## 📈 Multi-Resume Comparison

The system supports analyzing multiple resumes simultaneously:
- Rank candidates by match score
- Side-by-side comparison table
- Detailed skill gap analysis for each candidate
- Visual indicators for top performers

## 🛡️ Privacy & Security

- All processing happens locally
- No external API calls (except for initial model download)
- Data never leaves your machine
- Secure handling of resume information

## 🚧 Known Limitations

- Image-based PDFs (scanned documents) may not extract text properly
- Complex layouts in DOCX files may affect parsing accuracy
- Initial model download required (~80MB)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues or questions, please open an issue in the GitHub repository.