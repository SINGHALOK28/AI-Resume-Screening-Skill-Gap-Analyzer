"""Test script to verify all imports work correctly."""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    print("Testing imports...")
    from preprocessing.resume_parser import extract_resume_text
    print("[OK] resume_parser imported")
    
    from preprocessing.jd_parser import extract_jd_text
    print("[OK] jd_parser imported")
    
    from preprocessing.text_cleaner import clean_text
    print("[OK] text_cleaner imported")
    
    from embeddings.skill_extractor import extract_skills, categorize_skills
    print("[OK] skill_extractor imported")
    
    from embeddings.similarity_engine import get_similarity_engine
    print("[OK] similarity_engine imported")
    
    from generation.recommendation_generator import get_recommendation_generator
    print("[OK] recommendation_generator imported")
    
    print("\n[SUCCESS] All imports successful!")
    
except Exception as e:
    print(f"\n[ERROR] Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

