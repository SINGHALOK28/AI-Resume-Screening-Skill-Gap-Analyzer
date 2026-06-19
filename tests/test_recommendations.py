"""
Test script to verify improved recommendation generation
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from generation.recommendation_generator import get_recommendation_generator

def test_recommendations():
    print("Testing improved recommendations...")
    
    # Create generator
    generator = get_recommendation_generator(use_local=False)  # Use template-based for testing
    
    # Test 1: With missing skills
    print("\n1. Testing with missing skills:")
    missing_skills = ["python", "javascript", "react"]
    resume_skills = ["java", "sql", "git"]
    feedback = generator._generate_template_based(missing_skills, resume_skills, 0.45)
    safe_feedback = feedback.encode('ascii', 'ignore').decode('ascii')
    print(safe_feedback[:500] + "..." if len(safe_feedback) > 500 else safe_feedback)
    
    # Test 2: High match score
    print("\n2. Testing high match score:")
    feedback2 = generator._generate_template_based([], ["python", "javascript", "react"], 0.85)
    safe_feedback2 = feedback2.encode('ascii', 'ignore').decode('ascii')
    print(safe_feedback2[:300] + "..." if len(safe_feedback2) > 300 else safe_feedback2)
    
    # Test 3: Positive feedback
    print("\n3. Testing positive feedback:")
    positive_feedback = generator._generate_positive_feedback(["python", "javascript", "react"], 0.90)
    safe_positive_feedback = positive_feedback.encode('ascii', 'ignore').decode('ascii')
    print(safe_positive_feedback)
    
    print("\n[OK] All recommendation tests completed!")

if __name__ == "__main__":
    test_recommendations()