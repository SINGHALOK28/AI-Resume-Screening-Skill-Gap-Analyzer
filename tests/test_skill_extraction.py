"""Test script to verify skill extraction is working."""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from embeddings.skill_extractor import extract_skills

# Test with sample resume text
test_text = """
John Doe
Software Engineer

Skills:
- Python programming
- Java development
- SQL databases
- JavaScript and HTML/CSS
- Machine Learning
- Data Analysis
- React and Node.js
- AWS cloud services
- Docker and Kubernetes
- Git version control

Experience:
Worked with Python, Java, and SQL on various projects.
Used machine learning algorithms for data analysis.
Proficient in JavaScript, HTML, and CSS for web development.
"""

print("Testing skill extraction...")
print("\nTest text:")
print(test_text[:200] + "...")
print("\n" + "="*50)

skills = extract_skills(test_text)

print(f"\nExtracted {len(skills)} skills:")
for skill in skills:
    print(f"  - {skill}")

print("\n" + "="*50)
print("Expected skills: Python, Java, SQL, JavaScript, HTML, CSS, Machine Learning, React, Node.js, AWS, Docker, Kubernetes, Git")
print(f"\nTest {'PASSED' if len(skills) > 5 else 'FAILED'} - Found {len(skills)} skills")

