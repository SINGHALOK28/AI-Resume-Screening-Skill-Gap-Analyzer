# Text Cleaner Module
# Cleans and normalizes text extracted from documents.

# PURPOSE: Clean and normalize text extracted from documents
# COMPONENTS: Character normalization, whitespace handling, encoding fixes
# INPUTS: Raw text from document extraction
# OUTPUTS: Cleaned, normalized text ready for processing
# WORKFLOW: Normalize encoding → Clean whitespace → Fix punctuation → Standardize format
# LOGIC: Remove noise while preserving meaningful content

# WHY: Prepare extracted text for skill extraction and analysis
# WHAT: Removes noise and standardizes text format
# HOW: Applies regex patterns and string operations to clean text

# Import library for regular expressions
import re


def clean_text(text):
    """
    Clean and normalize text for processing while preserving important information.
    
    Args:
        text: Raw text to clean
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove null bytes and control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', text)
    
    # Fix common encoding issues
    text = text.replace('\u2019', "'")
    text = text.replace('\u2018', "'")
    text = text.replace('\u201C', '"')
    text = text.replace('\u201D', '"')
    text = text.replace('\u2013', '-')
    text = text.replace('\u2014', '--')
    text = text.replace('\u2026', '...')
    
    # Normalize whitespace but preserve structure
    # Replace multiple spaces with single space (but keep newlines)
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    
    # Normalize line breaks
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\r', '\n', text)
    
    # Remove excessive dashes
    text = re.sub(r'-{3,}', '---', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Final strip
    text = text.strip()
    
    return text


def remove_stopwords_custom(text, custom_stopwords=None):
    """
    Remove common stopwords (optional, for specific use cases).
    
    Args:
        text: Text to process
        custom_stopwords: List of custom stopwords to remove
    
    Returns:
        str: Text with stopwords removed
    """
    if not text:
        return ""
    
    if custom_stopwords is None:
        custom_stopwords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
    
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in custom_stopwords]
    
    return " ".join(filtered_words)


def extract_email_phone(text):
    """
    Extract email and phone numbers from text (optional utility).
    
    Args:
        text: Text to extract from
    
    Returns:
        dict: Dictionary with email and phone
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    return {
        'emails': emails,
        'phones': phones
    }

