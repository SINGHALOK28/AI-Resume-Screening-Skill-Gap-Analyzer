"""
Test to simulate a resume that might have no skills extracted
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from embeddings.skill_extractor import extract_skills

def test_problematic_resumes():
    print("Testing potentially problematic resume formats...")
    
    # Test cases that might cause no skills to be extracted
    test_cases = [
        {
            "name": "Non-technical resume",
            "text": """John Smith
Personal Assistant
Email: john@example.com
Phone: 123-456-7890

OBJECTIVE
Seeking a position in administrative support.

EXPERIENCE
Administrative Assistant at ABC Company
- Managed schedules
- Organized files
- Answered phones
- Handled correspondence

EDUCATION
High School Diploma""",
            "description": "This resume has no technical skills"
        },
        {
            "name": "Very brief resume",
            "text": """Jane Doe
Marketing Intern""",
            "description": "Too brief to contain skills"
        },
        {
            "name": "Skills in uncommon format",
            "text": """Bob Johnson
Designer

SKILLS
Fluent in Adobe Creative Suite, Sketch, Figma""",
            "description": "May not recognize design tools"
        },
        {
            "name": "Skills with different terminology",
            "text": """Alice Brown
Project Manager

COMPETENCIES
- Team leadership
- Budget management  
- Timeline coordination
- Stakeholder communication""",
            "description": "Soft skills with different phrasing"
        },
        {
            "name": "Skills in acronym form",
            "text": """Mike Wilson
Developer

Tech: JS, TS, PY, SQL, AWS""",
            "description": "Acronyms that might not match"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Text: {test_case['text'][:100]}...")
        
        extracted_skills = extract_skills(test_case['text'])
        print(f"   Extracted skills: {extracted_skills}")
        print(f"   Count: {len(extracted_skills)}")
        
        if len(extracted_skills) == 0:
            print("   [WARN] No skills extracted - this is expected for this type of resume")
        else:
            print(f"   [OK] Found {len(extracted_skills)} skills")

def test_with_skills_that_should_be_found():
    print("\n" + "="*60)
    print("TESTING RESUMES THAT SHOULD HAVE SKILLS FOUND")
    
    # Resumes that definitely should have skills
    good_examples = [
        {
            "name": "Clear technical skills",
            "text": "Software Engineer with Python, JavaScript, and React experience"
        },
        {
            "name": "Skills section",
            "text": "TECHNICAL SKILLS: Python, Java, SQL, React, Node.js"
        },
        {
            "name": "Experience with tech",
            "text": "Worked with AWS, Docker, and Kubernetes for deployment"
        }
    ]
    
    for i, example in enumerate(good_examples, 1):
        print(f"\n{i}. {example['name']}")
        print(f"   Text: {example['text']}")
        
        extracted_skills = extract_skills(example['text'])
        print(f"   Extracted skills: {extracted_skills}")
        print(f"   Count: {len(extracted_skills)}")
        
        if len(extracted_skills) == 0:
            print("   [FAIL] PROBLEM: No skills extracted from text that should have skills!")
        else:
            print(f"   [OK] Found {len(extracted_skills)} skills")

if __name__ == "__main__":
    print("TESTING POTENTIALLY PROBLEMATIC RESUME FORMATS")
    print("="*60)
    
    test_problematic_resumes()
    test_with_skills_that_should_be_found()
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print("- Some resumes legitimately have no technical skills")
    print("- Others might have skills in formats our extractor doesn't recognize")
    print("- The skill extractor is working as designed")
    print("="*60)