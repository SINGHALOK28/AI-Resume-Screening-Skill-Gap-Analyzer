"""
Debug script to test similarity computation and skill extraction
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from embeddings.skill_extractor import extract_skills
from embeddings.similarity_engine import get_similarity_engine

def test_similarity_debug():
    print("DEBUGGING SIMILARITY COMPUTATION")
    print("="*60)
    
    # Test with sample resume and job description
    sample_resume = """
    John Doe
    Software Engineer
    
    TECHNICAL SKILLS
    • Python, JavaScript, React
    • Experience with web development
    • Familiar with databases and cloud technologies
    """
    
    sample_jd = """
    We are looking for a Software Engineer with:
    • Python and JavaScript experience
    • React development skills
    • Web application development
    • Database management knowledge
    • Cloud platform experience
    """
    
    print("Resume text:")
    print(sample_resume.strip())
    print("\n" + "-"*40)
    print("Job Description:")
    print(sample_jd.strip())
    
    # Extract skills
    resume_skills = extract_skills(sample_resume)
    jd_skills = extract_skills(sample_jd)
    
    print(f"\nResume skills: {resume_skills}")
    print(f"JD skills: {jd_skills}")
    
    # Compute similarity
    engine = get_similarity_engine()
    similarity_score = engine.compute_similarity(sample_resume, sample_jd)
    
    print(f"\nSimilarity score: {similarity_score:.4f} ({similarity_score*100:.2f}%)")
    
    # Test with completely different content
    print("\n" + "="*60)
    print("TESTING WITH UNRELATED CONTENT")
    
    unrelated_resume = """
    Jane Smith
    Marketing Coordinator
    
    EXPERIENCE
    • Marketing campaigns
    • Social media management
    • Content creation
    """
    
    unrelated_jd = """
    Software Engineer position requiring:
    • Python programming
    • JavaScript development
    • Database management
    """
    
    print("Unrelated Resume:")
    print(unrelated_resume.strip())
    print("\n" + "-"*40)
    print("Unrelated JD:")
    print(unrelated_jd.strip())
    
    unrelated_skills_resume = extract_skills(unrelated_resume)
    unrelated_skills_jd = extract_skills(unrelated_jd)
    
    print(f"\nResume skills: {unrelated_skills_resume}")
    print(f"JD skills: {unrelated_skills_jd}")
    
    unrelated_score = engine.compute_similarity(unrelated_resume, unrelated_jd)
    print(f"\nSimilarity score: {unrelated_score:.4f} ({unrelated_score*100:.2f}%)")
    
    # Test with empty skills but related content
    print("\n" + "="*60)
    print("TESTING WITH NO EXTRACTED SKILLS BUT RELATED CONTENT")
    
    resume_no_skills = """
    John Engineer
    I have worked on many software projects
    My experience includes building applications
    I have knowledge in programming and development
    """
    
    jd_no_skills = """
    Looking for someone with programming experience
    Experience building applications required
    Knowledge in development and programming needed
    """
    
    print("Resume (no clear skills):")
    print(resume_no_skills.strip())
    print("\n" + "-"*40)
    print("JD (no clear skills):")
    print(jd_no_skills.strip())
    
    no_skills_resume = extract_skills(resume_no_skills)
    no_skills_jd = extract_skills(jd_no_skills)
    
    print(f"\nResume skills: {no_skills_resume}")
    print(f"JD skills: {no_skills_jd}")
    
    no_skills_score = engine.compute_similarity(resume_no_skills, jd_no_skills)
    print(f"\nSimilarity score: {no_skills_score:.4f} ({no_skills_score*100:.2f}%)")

if __name__ == "__main__":
    test_similarity_debug()