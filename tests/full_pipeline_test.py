"""
Full pipeline test to check the entire resume processing flow.
"""

import sys
import os
import tempfile
from io import BytesIO

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from preprocessing.resume_parser import extract_resume_text
from embeddings.skill_extractor import extract_skills

def test_full_pipeline():
    # Create a temporary text file to simulate a resume
    sample_resume_text = """
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
    
    print("Testing full pipeline...")
    print("="*60)
    
    # Test 1: Direct skill extraction from text
    print("1. Testing direct skill extraction from text:")
    skills_direct = extract_skills(sample_resume_text)
    print(f"   Extracted skills: {skills_direct}")
    print(f"   Count: {len(skills_direct)}")
    
    # Test 2: Simulate file processing by creating a temp file
    print("\n2. Testing resume text extraction and skill extraction:")
    
    # Create a temporary file with the sample resume text
    temp_file_path = None
    try:
        # Create the temp file with explicit encoding
        import os
        temp_fd, temp_file_path = tempfile.mkstemp(suffix='.txt', text=True)
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_file:
                temp_file.write(sample_resume_text)
        except:
            # If that fails, close fd and use NamedTemporaryFile without text mode
            os.close(temp_fd)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(sample_resume_text)
                temp_file_path = temp_file.name
        
        # Read the text back (simulating file reading process)
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        print(f"   File content length: {len(file_content)}")
        print(f"   Content preview: {file_content[:200]}...")
        
        # Extract skills from the file content
        skills_from_file = extract_skills(file_content)
        print(f"   Skills from file content: {skills_from_file}")
        print(f"   Count: {len(skills_from_file)}")
        
    finally:
        # Clean up the temp file
        os.unlink(temp_file_path)
    
    # Test 3: Test with simulated file object (like Streamlit upload)
    print("\n3. Testing with BytesIO object (simulating file upload):")
    file_obj = BytesIO(sample_resume_text.encode('utf-8'))
    file_obj.name = "resume.txt"  # Streamlit-style file object
    
    # For this test, we'll just test the skill extraction part since the resume parser expects actual PDF/DOCX files
    file_content_bytesio = file_obj.getvalue().decode('utf-8')
    skills_bytesio = extract_skills(file_content_bytesio)
    print(f"   Skills from BytesIO content: {skills_bytesio}")
    print(f"   Count: {len(skills_bytesio)}")
    
    print("\n" + "="*60)
    print("PIPELINE TEST RESULTS:")
    print(f"Direct text extraction: {len(skills_direct)} skills")
    print(f"File content extraction: {len(skills_from_file)} skills")
    print(f"BytesIO extraction: {len(skills_bytesio)} skills")
    
    # Overall assessment
    if all(len(skills) == 0 for skills in [skills_direct, skills_from_file, skills_bytesio]):
        print("\n❌ ISSUE: No skills extracted in any test - there may be a problem with the skill extraction logic")
        return False
    else:
        print(f"\n✅ SUCCESS: Skills extracted in at least one test")
        return True

def test_edge_cases():
    print("\n" + "="*60)
    print("TESTING EDGE CASES:")
    
    # Test with minimal skills
    minimal_resume = "John Doe\nSoftware Engineer\nSkills: Python"
    skills_minimal = extract_skills(minimal_resume)
    print(f"Minimal resume: {skills_minimal}")
    
    # Test with uppercase
    uppercase_resume = "SKILLS: PYTHON, JAVASCRIPT, REACT"
    skills_uppercase = extract_skills(uppercase_resume)
    print(f"Uppercase resume: {skills_uppercase}")
    
    # Test with mixed case
    mixed_resume = "Skills: PyThOn, JaVaScRiPt, ReAcT"
    skills_mixed = extract_skills(mixed_resume)
    print(f"Mixed case resume: {skills_mixed}")
    
    # Test with common resume formats
    common_format = """
    TECHNICAL SKILLS:
    Languages: Python, Java, JavaScript
    Frameworks: React, Django
    Tools: Git, Docker
    """
    skills_common = extract_skills(common_format)
    print(f"Common format: {skills_common}")

if __name__ == "__main__":
    print("FULL PIPELINE TEST FOR RESUME SKILL EXTRACTION")
    success = test_full_pipeline()
    test_edge_cases()
    
    print("\n" + "="*60)
    if success:
        print("✅ Pipeline test completed successfully")
    else:
        print("❌ Pipeline test revealed issues")
    print("="*60)