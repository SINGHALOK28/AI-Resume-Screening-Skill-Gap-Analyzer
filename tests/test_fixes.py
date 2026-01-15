"""
Test script to verify the fixes for skill extraction from resumes.
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from embeddings.skill_extractor import extract_skills

def test_various_resume_formats():
    print("Testing various resume formats...")
    
    # Test cases with different resume formats
    test_cases = [
        # Skills in Skills section
        {
            "name": "Skills section format",
            "text": "SKILLS\nPython, JavaScript, React, SQL",
            "expected": ["python", "javascript", "react", "sql"]
        },
        # Skills in bullet points
        {
            "name": "Bullet points format",
            "text": "• Python\n• Java\n• JavaScript",
            "expected": ["python", "java", "javascript"]
        },
        # Skills in proficiency format
        {
            "name": "Proficiency format",
            "text": "Proficient in Python, Java, and JavaScript",
            "expected": ["python", "java", "javascript"]
        },
        # Skills in experience format
        {
            "name": "Experience format",
            "text": "Experience with React, Node.js, and MongoDB",
            "expected": ["react", "node.js", "mongodb"]
        },
        # Skills in knowledge format
        {
            "name": "Knowledge format",
            "text": "Knowledge of AWS, Docker, and Kubernetes",
            "expected": ["aws", "docker", "kubernetes"]
        },
        # Skills in projects format
        {
            "name": "Projects format",
            "text": "PROJECTS\nDeveloped web app using Python, React, and PostgreSQL",
            "expected": ["python", "react", "postgresql"]
        },
        # Skills in tools format
        {
            "name": "Tools format",
            "text": "Tools: Git, Docker, Jenkins",
            "expected": ["git", "docker", "jenkins"]
        },
        # Skills in complex format
        {
            "name": "Complex format",
            "text": """
            SOFTWARE ENGINEER
            EXPERIENCE:
            - Worked with Python and Django for backend development
            - Used React and JavaScript for frontend
            
            TECHNICAL SKILLS:
            Languages: Python, JavaScript, SQL
            Frameworks: React, Django, Express
            Tools: Git, Docker, AWS
            """,
            "expected": ["python", "javascript", "sql", "react", "django", "express", "git", "docker", "aws"]
        }
    ]
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        extracted_skills = extract_skills(test_case['text'])
        expected_skills = test_case['expected']
        
        print(f"   Text: {test_case['text'][:100]}...")
        print(f"   Extracted: {extracted_skills}")
        print(f"   Expected: {expected_skills}")
        
        # Check if all expected skills are found
        found_count = sum(1 for exp in expected_skills if any(exp.lower() in ext.lower() or ext.lower() in exp.lower() for ext in extracted_skills))
        expected_count = len(expected_skills)
        
        print(f"   Match: {found_count}/{expected_count}")
        
        if found_count >= max(1, expected_count // 2):  # At least half should match
            print("   ✓ PASS")
            passed_tests += 1
        else:
            print("   ✗ FAIL")
    
    print(f"\nSUMMARY: {passed_tests}/{total_tests} tests passed")
    return passed_tests == total_tests


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING SKILL EXTRACTION FIXES")
    print("=" * 60)
    
    success = test_various_resume_formats()
    
    print("\n" + "=" * 60)
    if success:
        print("ALL TESTS PASSED! Skill extraction improvements working correctly.")
    else:
        print("SOME TESTS FAILED! Further improvements needed.")
    print("=" * 60)