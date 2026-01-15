"""
Diagnostic tool to debug skill extraction issues.
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from embeddings.skill_extractor import extract_skills, TECHNICAL_SKILLS, SOFT_SKILLS

def debug_skill_extraction(text):
    print("DEBUGGING SKILL EXTRACTION")
    print("="*50)
    print("Input text:")
    print(text[:500] + "..." if len(text) > 500 else text)
    print("\n" + "="*50)
    
    # Show all skills in database
    all_skills = TECHNICAL_SKILLS.union(SOFT_SKILLS)
    print(f"Total skills in database: {len(all_skills)}")
    
    # Show first 20 skills as sample
    print("Sample skills from database:", list(all_skills)[:20])
    
    # Try extraction
    extracted = extract_skills(text)
    print(f"\nExtracted skills: {extracted}")
    
    # Manual check - see if any skills appear in the text
    text_lower = text.lower()
    found_skills = []
    
    for skill in all_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    print(f"\nSkills found by manual search: {found_skills[:20]}")
    print(f"Total manually found: {len(found_skills)}")
    
    # Check text preprocessing
    import re
    processed_text = re.sub(r'[\r\n\t\v]+', ' ', text_lower)
    processed_text = re.sub(r'[;,|]+', ' ', processed_text)
    
    print(f"\nOriginal length: {len(text)}")
    print(f"Processed length: {len(processed_text)}")
    
    # Try to find some common skills manually
    common_skills = ['python', 'java', 'javascript', 'sql', 'react', 'angular', 'node.js', 'html', 'css', 'c++', 'c#', 'aws', 'docker', 'git']
    found_common = []
    for skill in common_skills:
        if skill in processed_text:
            found_common.append(skill)
    
    print(f"Common skills found: {found_common}")
    
    return extracted

if __name__ == "__main__":
    # Test with some sample resume text
    sample_resume = """
    John Doe
    Software Engineer
    
    CONTACT
    Email: john.doe@example.com
    Phone: (555) 123-4567
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with expertise in web development and cloud technologies.
    
    TECHNICAL SKILLS
    • Programming Languages: Python, JavaScript, Java
    • Web Technologies: React, Angular, Node.js, HTML, CSS
    • Databases: MySQL, PostgreSQL, MongoDB
    • Cloud & DevOps: AWS, Docker, Git
    • Frameworks: Django, Express, Spring
    
    EXPERIENCE
    Senior Software Developer at Tech Corp
    • Developed web applications using Python and JavaScript
    • Implemented REST APIs with Node.js and Express
    • Deployed applications to AWS using Docker containers
    • Collaborated with teams using Git version control
    
    EDUCATION
    B.S. Computer Science, University of Tech
    """
    
    print("Testing with sample resume...")
    result = debug_skill_extraction(sample_resume)
    print(f"\nFinal extracted skills: {result}")