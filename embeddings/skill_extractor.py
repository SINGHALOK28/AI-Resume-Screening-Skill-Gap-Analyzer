# Skill Extractor Module
# Extracts skills from text using pattern matching and NLP techniques.

# PURPOSE: Extract skills from text using pattern matching and NLP techniques
# COMPONENTS: Skill databases, pattern matching, context recognition
# INPUTS: Text string to extract skills from
# OUTPUTS: List of extracted skills
# WORKFLOW: Pattern matching → Context recognition → Skill validation → Categorization
# LOGIC: Multiple pattern matching approaches to catch skills in various formats

# WHY: Need to identify technical and soft skills from unstructured text
# WHAT: Extracts relevant skills from resume/job description
# HOW: Uses pattern matching against comprehensive skill databases

# Import library for regular expressions
import re
# Import type hints for function signatures
from typing import List, Dict, Set


# Comprehensive skill database
TECHNICAL_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "kotlin", "swift",
    "php", "ruby", "scala", "r", "matlab", "perl", "shell", "bash", "powershell",
    
    # Web Technologies
    "html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask",
    "spring", "asp.net", "laravel", "next.js", "nuxt.js", "jquery", "bootstrap",
    
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite", "cassandra",
    "elasticsearch", "dynamodb", "neo4j", "firebase",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "ci/cd", "terraform",
    "ansible", "chef", "puppet", "linux", "unix", "nginx", "apache",
    
    # Data Science & ML
    "machine learning", "deep learning", "neural networks", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "matplotlib", "seaborn", "jupyter", "data analysis", "data science", "statistics",
    
    # Big Data
    "hadoop", "spark", "kafka", "hive", "pig", "hbase", "storm",
    
    # Mobile
    "android", "ios", "react native", "flutter", "xamarin", "swift", "kotlin",
    
    # Other Technologies
    "blockchain", "ethereum", "solidity", "graphql", "rest api", "microservices",
    "agile", "scrum", "devops", "mlops", "data engineering"
}

SOFT_SKILLS = {
    "leadership", "communication", "teamwork", "problem solving", "critical thinking",
    "project management", "time management", "adaptability", "creativity", "analytical",
    "collaboration", "presentation", "negotiation", "mentoring", "agile methodology"
}


def extract_skills(text: str, skill_database: Set[str] = None) -> List[str]:
    """
    Extract skills from text using pattern matching and NLP techniques.
    
    Args:
        text: Input text to extract skills from
        skill_database: Custom skill database (uses default if None)
    
    Returns:
        List[str]: List of extracted skills
    """
    if not text:
        return []
    
    if skill_database is None:
        skill_database = TECHNICAL_SKILLS.union(SOFT_SKILLS)
    
    # Keep original text for case-sensitive matching, but also use lowercase
    text_lower = text.lower()
    found_skills = []
    
    # Separate single-letter skills from multi-letter skills
    single_letter_skills = {s for s in skill_database if len(s.strip()) == 1}
    multi_letter_skills = skill_database - single_letter_skills
    
    # First, match multi-letter skills (more reliable)
    # Sort by length (longer first) to match "machine learning" before "learning"
    for skill in sorted(multi_letter_skills, key=lambda x: (-len(x), x.lower())):
        skill_lower = skill.lower()
        skill_escaped = re.escape(skill_lower)
        
        # Build flexible patterns
        patterns = []
        
        # Standard word boundary pattern
        patterns.append(r'\b' + skill_escaped + r'\b')
        
        # Pattern with punctuation after (e.g., "Python,", "Java;")
        patterns.append(r'\b' + skill_escaped + r'[,;:•]')
        
        # Pattern with punctuation before (e.g., ", Python", "; Java")
        patterns.append(r'[,;:•]\s*' + skill_escaped + r'\b')
        
        # Pattern for skills at start/end of line
        patterns.append(r'^' + skill_escaped + r'\b')
        patterns.append(r'\b' + skill_escaped + r'$')
        
        # For skills with special characters (like C++, C#), handle them specially
        if '+' in skill or '#' in skill or '.' in skill:
            # Escape special regex chars but allow the special chars
            special_pattern = re.escape(skill_lower).replace(r'\+', r'\+').replace(r'\#', r'#').replace(r'\.', r'\.')
            patterns.append(r'\b' + special_pattern + r'\b')
        
        # Check if any pattern matches (case-insensitive)
        matched = False
        for pattern in patterns:
            try:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matched = True
                    break
            except re.error:
                # Skip invalid patterns
                continue
        
        # Fallback: Simple substring match for very common skills if strict matching fails
        # This helps catch skills that might be in tables or formatted text
        if not matched and len(skill_lower) >= 3:  # Only for skills with 3+ characters
            # Check if skill appears as a whole word (not part of another word)
            # Look for skill surrounded by non-word characters or at boundaries
            simple_pattern = r'[^a-z]' + skill_escaped + r'[^a-z]'
            if re.search(simple_pattern, text_lower, re.IGNORECASE):
                matched = True
        
        if matched:
            found_skills.append(skill)
    
    # For single-letter skills (like "R" for R programming), use stricter matching
    # Only match if it appears in programming/technical context
    for skill in single_letter_skills:
        skill_lower = skill.lower()
        
        # Skip if it's just a common letter in text (not a skill)
        # Check if it appears as part of common words (like "the", "are", "for", etc.)
        # We'll only match if it's clearly a standalone skill reference
        
        # More strict pattern: R should be followed by programming-related terms or be in a list
        # Pattern: R followed by space and (programming, language, statistical, data, etc.)
        # OR: "R," or "R " at end of line or followed by punctuation
        strict_patterns = [
            r'\b' + re.escape(skill_lower) + r'\s+(programming|language|statistical|data|analysis|development|studio)',
            r'\b' + re.escape(skill_lower) + r'[,;]',  # R, or R;
            r'\b' + re.escape(skill_lower) + r'\s*$',  # R at end of line
            r'programming\s+in\s+' + re.escape(skill_lower),  # "programming in R"
            r'using\s+' + re.escape(skill_lower),  # "using R"
            r'experience\s+with\s+' + re.escape(skill_lower),  # "experience with R"
            r'proficient\s+in\s+' + re.escape(skill_lower),  # "proficient in R"
            r'knowledge\s+of\s+' + re.escape(skill_lower),  # "knowledge of R"
        ]
        
        # Check if any strict pattern matches
        matches_strict = any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in strict_patterns)
        
        # Also check if it's in a skills list format (comma-separated)
        # Look for patterns like "Python, R, SQL" or "Skills: R, Python"
        # Must be surrounded by other skills or in a skills section
        skills_list_patterns = [
            r'(skills?|technologies?|languages?|tools?|proficient|experience)[\s:]*[^.]{0,100}\b' + re.escape(skill_lower) + r'\b',
            r'\b(python|java|sql|javascript|html|css)[\s,]+' + re.escape(skill_lower) + r'\b',  # After known skills
            r'\b' + re.escape(skill_lower) + r'[\s,]+(python|java|sql|javascript|html|css)\b',  # Before known skills
        ]
        in_skills_list = any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in skills_list_patterns)
        
        # Additional check: R should appear as standalone (not part of common words)
        # Look for patterns where R is clearly a skill reference
        # Examples: "R,", "R.", "R ", "R programming", "in R", etc.
        standalone_patterns = [
            r'[^a-z]' + re.escape(skill_lower) + r'[,;.]',  # R, R; R.
            r'[^a-z]' + re.escape(skill_lower) + r'\s',  # R followed by space
            r'[^a-z]' + re.escape(skill_lower) + r'$',  # R at end
            r'^' + re.escape(skill_lower) + r'[^a-z]',  # R at start
        ]
        is_standalone = any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in standalone_patterns)
        
        # Only add if it matches strict patterns AND appears standalone
        if (matches_strict or in_skills_list) and is_standalone:
            found_skills.append(skill)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in found_skills:
        if skill.lower() not in seen:
            seen.add(skill.lower())
            unique_skills.append(skill)
    
    return unique_skills


def extract_skills_with_context(text: str, skill_database: Set[str] = None) -> Dict[str, List[str]]:
    """
    Extract skills with context (where they appear in the text).
    
    Args:
        text: Input text
        skill_database: Custom skill database
    
    Returns:
        Dict: Skills with their context sentences
    """
    if not text:
        return {}
    
    if skill_database is None:
        skill_database = TECHNICAL_SKILLS.union(SOFT_SKILLS)
    
    text_lower = text.lower()
    sentences = re.split(r'[.!?]+', text)
    skills_with_context = {}
    
    for skill in skill_database:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            # Find sentences containing the skill
            contexts = [s.strip() for s in sentences if re.search(pattern, s.lower(), re.IGNORECASE)]
            if contexts:
                skills_with_context[skill] = contexts[:3]  # Limit to 3 contexts
    
    return skills_with_context


def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """
    Categorize extracted skills into groups.
    
    Args:
        skills: List of skills
    
    Returns:
        Dict: Categorized skills
    """
    categorized = {
        'programming_languages': [],
        'web_technologies': [],
        'databases': [],
        'cloud_devops': [],
        'data_science_ml': [],
        'big_data': [],
        'mobile': [],
        'soft_skills': [],
        'other': []
    }
    
    for skill in skills:
        skill_lower = skill.lower()
        categorized_flag = False
        
        if skill_lower in TECHNICAL_SKILLS:
            if skill_lower in ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'kotlin', 'swift', 'php', 'ruby', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell']:
                categorized['programming_languages'].append(skill)
                categorized_flag = True
            elif skill_lower in ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'asp.net', 'laravel', 'next.js', 'nuxt.js', 'jquery', 'bootstrap']:
                categorized['web_technologies'].append(skill)
                categorized_flag = True
            elif skill_lower in ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra', 'elasticsearch', 'dynamodb', 'neo4j', 'firebase']:
                categorized['databases'].append(skill)
                categorized_flag = True
            elif skill_lower in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd', 'terraform', 'ansible', 'chef', 'puppet', 'linux', 'unix', 'nginx', 'apache']:
                categorized['cloud_devops'].append(skill)
                categorized_flag = True
            elif skill_lower in ['machine learning', 'deep learning', 'neural networks', 'nlp', 'natural language processing', 'computer vision', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter', 'data analysis', 'data science', 'statistics']:
                categorized['data_science_ml'].append(skill)
                categorized_flag = True
            elif skill_lower in ['hadoop', 'spark', 'kafka', 'hive', 'pig', 'hbase', 'storm']:
                categorized['big_data'].append(skill)
                categorized_flag = True
            elif skill_lower in ['android', 'ios', 'react native', 'flutter', 'xamarin', 'swift', 'kotlin']:
                categorized['mobile'].append(skill)
                categorized_flag = True
        
        if skill_lower in SOFT_SKILLS:
            categorized['soft_skills'].append(skill)
            categorized_flag = True
        
        if not categorized_flag:
            categorized['other'].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}


def get_skill_categories(skills: List[str]) -> Dict[str, List[str]]:
    """
    Categorize skills into real-world relevant groups for better analysis.
    
    Args:
        skills: List of skills to categorize
    
    Returns:
        Dict: Skills grouped by category
    """
    categories = {
        'Programming Languages': [],
        'Web Development': [],
        'Databases': [],
        'Cloud Platforms': [],
        'DevOps & Tools': [],
        'Data Science & ML': [],
        'Mobile Development': [],
        'Soft Skills': [],
        'Industry Certifications': [],
        'Business Skills': [],
        'Other Technical': []
    }
    
    # Define category keywords
    prog_langs = {'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'kotlin', 'swift',
                  'php', 'ruby', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell'}
    web_dev = {'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
               'spring', 'asp.net', 'laravel', 'next.js', 'nuxt.js', 'jquery', 'bootstrap', 'svelte'}
    databases = {'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra',
                'elasticsearch', 'dynamodb', 'neo4j', 'firebase', 'snowflake', 'redshift'}
    cloud = {'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
             'ci/cd', 'openshift', 'ecs', 'eks', 'aks'}
    devops = {'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack', 'trello', 'linux', 'unix'}
    data_ml = {'machine learning', 'deep learning', 'neural networks', 'nlp', 'natural language processing',
               'computer vision', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
               'matplotlib', 'seaborn', 'jupyter', 'data analysis', 'data science', 'statistics',
               'hadoop', 'spark', 'kafka', 'hive', 'big data', 'mlops', 'data engineering'}
    mobile = {'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova'}
    soft_skills = {'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
                   'project management', 'time management', 'adaptability', 'creativity', 'analytical',
                   'collaboration', 'presentation', 'negotiation', 'mentoring', 'agile methodology'}
    business = {'business analysis', 'product management', 'marketing', 'sales', 'finance', 'accounting',
                'strategic planning', 'stakeholder management', 'agile', 'scrum', 'kanban'}
    
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in prog_langs:
            categories['Programming Languages'].append(skill)
        elif skill_lower in web_dev:
            categories['Web Development'].append(skill)
        elif skill_lower in databases:
            categories['Databases'].append(skill)
        elif skill_lower in cloud:
            categories['Cloud Platforms'].append(skill)
        elif skill_lower in devops:
            categories['DevOps & Tools'].append(skill)
        elif any(s in skill_lower for s in data_ml):
            categories['Data Science & ML'].append(skill)
        elif skill_lower in mobile:
            categories['Mobile Development'].append(skill)
        elif skill_lower in soft_skills:
            categories['Soft Skills'].append(skill)
        elif skill_lower in business:
            categories['Business Skills'].append(skill)
        else:
            categories['Other Technical'].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}

