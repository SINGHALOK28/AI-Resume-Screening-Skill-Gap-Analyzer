# JD Parser Module
# Parses and extracts information from job descriptions.

# PURPOSE: Parse and extract information from job descriptions
# COMPONENTS: Text extraction, cleaning, and preprocessing
# INPUTS: Job description text
# OUTPUTS: Processed job description text ready for analysis
# WORKFLOW: Extract → Clean → Normalize → Prepare for comparison
# LOGIC: Apply same processing as resume text for consistency

# WHY: Process job descriptions consistently with resumes
# WHAT: Prepares job description text for skill extraction and comparison
# HOW: Uses same cleaning and normalization methods as resume processing


# Function to extract and normalize job description text
def extract_jd_text(text):
    """
    Extract and normalize job description text.
    
    Args:
        text: Raw job description text
    
    Returns:
        str: Normalized job description text
    """
    if not text:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized_text = text.lower().strip()
    
    # Remove excessive whitespace
    normalized_text = " ".join(normalized_text.split())
    
    return normalized_text


# Function to parse job description into sections (optional enhancement)
def parse_jd_sections(jd_text):
    """
    Parse job description into sections (optional enhancement).
    
    Args:
        jd_text: Job description text
    
    Returns:
        dict: Dictionary with parsed sections
    """
    # Initialize sections dictionary
    sections = {
        'requirements': '',
        'responsibilities': '',
        'qualifications': '',
        'full_text': jd_text.lower()
    }
    
    # Convert text to lowercase for keyword matching
    text_lower = jd_text.lower()
    
    # Define keywords for each section type
    keywords = {
        'requirements': ['requirements', 'required', 'must have', 'must possess'],
        'responsibilities': ['responsibilities', 'duties', 'will', 'you will'],
        'qualifications': ['qualifications', 'qualify', 'education', 'degree']
    }
    
    # Try to extract sections (basic implementation)
    # Split text into lines for processing
    lines = jd_text.split('\n')
    # Track current section being processed
    current_section = None
    
    # Process each line to identify sections
    for line in lines:
        line_lower = line.lower().strip()
        # Check if line contains keywords for any section
        for section, section_keywords in keywords.items():
            if any(keyword in line_lower for keyword in section_keywords):
                current_section = section
                break
        
        # Add line to current section if applicable
        if current_section and current_section in sections:
            sections[current_section] += line + " "
    
    return sections

