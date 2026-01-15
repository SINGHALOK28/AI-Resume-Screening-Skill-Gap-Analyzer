# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Setup Environment

```bash
# Create virtual environment
python -m venv genai_env

# Activate (Windows)
genai_env\Scripts\activate

# Activate (macOS/Linux)
source genai_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
streamlit run app/streamlit_app.py
```

### Step 3: Use the Application

1. Open your browser to `http://localhost:8501`
2. Upload a resume (PDF or DOCX)
3. Paste a job description
4. (Optional) Add critical skills in the sidebar
5. Click "Analyze Resume"
6. Review results and download PDF report

## 📝 Example Usage

### Using Modules Programmatically

```python
from preprocessing.resume_parser import extract_resume_text
from preprocessing.jd_parser import extract_jd_text
from embeddings.skill_extractor import extract_skills
from embeddings.similarity_engine import get_similarity_engine
from generation.recommendation_generator import get_recommendation_generator

# Extract text
resume_text = extract_resume_text("resume.pdf")
jd_text = extract_jd_text("Job description text here...")

# Extract skills
resume_skills = extract_skills(resume_text)
jd_skills = extract_skills(jd_text)

# Compute similarity
engine = get_similarity_engine()
match_score = engine.compute_similarity(resume_text, jd_text)

# Generate recommendations
missing_skills = [s for s in jd_skills if s.lower() not in [r.lower() for r in resume_skills]]
generator = get_recommendation_generator()
feedback = generator.generate_feedback(missing_skills, resume_skills, match_score)

print(f"Match Score: {match_score:.2%}")
print(f"Missing Skills: {missing_skills}")
print(f"Feedback: {feedback}")
```

## 🔧 Troubleshooting

### Issue: Model download is slow
**Solution**: First run downloads models (~80MB). Subsequent runs are faster.

### Issue: CUDA/GPU errors
**Solution**: System automatically uses CPU if GPU unavailable. This is normal.

### Issue: Import errors
**Solution**: Make sure you're in the project directory and virtual environment is activated.

### Issue: PDF parsing fails
**Solution**: Ensure PDF is not password-protected and is a valid PDF file.

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize skill database in `embeddings/skill_extractor.py`
- Adjust model settings in respective modules
- Add your own critical skills for weighted scoring

