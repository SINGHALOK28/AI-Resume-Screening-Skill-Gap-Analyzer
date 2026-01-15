# Similarity Engine Module
# Computes semantic similarity between resume and job description using embeddings.

# WHY: Need semantic matching beyond keyword overlap to understand context
# WHAT: Calculates similarity scores between resume and job description
# HOW: Uses sentence transformers to create embeddings and cosine similarity

# Purpose: Calculate semantic similarity between resume and job description
# Logic: Uses sentence transformers to create embeddings and cosine similarity
# Components: SentenceTransformer model, similarity calculations
# Inputs: Text strings (resume and job description)
# Outputs: Similarity score (0-1) and skill-based weighted scores

# Import sentence transformer library for semantic embeddings
from sentence_transformers import SentenceTransformer, util
# Import PyTorch for tensor operations
import torch
# Import NumPy for mathematical operations
import numpy as np
# Import type hints
from typing import Dict, Tuple


class SimilarityEngine:
    """Handles semantic similarity computation using sentence transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the similarity engine with a sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        # WHY: Need to load a pre-trained transformer model for embeddings
        # WHAT: Loads the sentence transformer model
        # HOW: Uses SentenceTransformer to initialize the model
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text (e.g., resume)
            text2: Second text (e.g., job description)
        
        Returns:
            float: Similarity score between 0 and 1
        """
        # WHY: Handle empty texts gracefully
        # WHAT: Check if either text is empty
        # HOW: Return 0.0 if either text is empty
        if not text1 or not text2:
            return 0.0
        
        # WHY: Improve performance on very long texts
        # WHAT: Truncate long texts to first 2000 characters
        # HOW: Slice text if longer than 2000 chars
        if len(text1) > 2000:
            text1 = text1[:2000]
        if len(text2) > 2000:
            text2 = text2[:2000]
        
        # WHY: Convert text to numerical vectors for similarity calculation
        # WHAT: Generate embeddings for both texts
        # HOW: Use sentence transformer model to encode texts
        emb1 = self.model.encode(text1, convert_to_tensor=False, show_progress_bar=False)
        emb2 = self.model.encode(text2, convert_to_tensor=False, show_progress_bar=False)
        
        # WHY: Calculate semantic similarity between vectors
        # WHAT: Compute cosine similarity of embeddings
        # HOW: Use dot product and norms to calculate cosine similarity
        similarity = float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
        
        # WHY: Ensure similarity score is in valid range [0,1]
        # WHAT: Clamp similarity to [0,1]
        # HOW: Use max/min functions to bound the value
        return max(0.0, min(1.0, similarity))  # Ensure between 0 and 1
    
    def compute_similarity_score(self, resume_text: str, jd_text: str) -> float:
        """
        Alias for compute_similarity for backward compatibility.
        
        Args:
            resume_text: Resume text
            jd_text: Job description text
        
        Returns:
            float: Similarity score
        """
        return self.compute_similarity(resume_text, jd_text)
    
    def compute_weighted_similarity(
        self, 
        resume_text: str, 
        jd_text: str, 
        critical_skills: Dict[str, float] = None
    ) -> Tuple[float, Dict[str, float]]:
        """
        Compute weighted similarity score based on critical skills.
        
        Args:
            resume_text: Resume text
            jd_text: Job description text
            critical_skills: Dictionary mapping skills to their weights
        
        Returns:
            Tuple: (weighted_score, skill_scores)
        """
        # WHY: Calculate baseline similarity without weights
        # WHAT: Get base semantic similarity
        # HOW: Call compute_similarity method
        base_score = self.compute_similarity(resume_text, jd_text)
        
        # WHY: Handle case where no critical skills are provided
        # WHAT: Return base score if no critical skills
        # HOW: Return base_score with empty skill scores dict
        if not critical_skills:
            return base_score, {}
        
        # WHY: Track which skills are present and their contribution
        # WHAT: Initialize data structures for skill scoring
        # HOW: Create dicts to store skill scores and totals
        skill_scores = {}
        total_weight = 0.0
        weighted_sum = 0.0
        
        # WHY: Make text comparison case-insensitive
        # WHAT: Convert texts to lowercase
        # HOW: Apply lower() method to both texts
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        # WHY: Evaluate presence of each critical skill
        # WHAT: Iterate through critical skills and assess their presence
        # HOW: Check if skill exists in both resume and job description
        for skill, weight in critical_skills.items():
            skill_lower = skill.lower()
            # Check if skill appears in both resume and JD
            in_resume = skill_lower in resume_lower
            in_jd = skill_lower in jd_lower
            
            # WHY: Only consider skills that appear in job description
            # WHAT: Process skills that are in the job description
            # HOW: Add weight to total if skill is in JD
            if in_jd:
                total_weight += weight
                # WHY: Reward presence of critical skills in resume
                # WHAT: Give full weight if skill present, 0 if missing
                # HOW: Set skill score to weight if present, 0.0 if absent
                if in_resume:
                    skill_scores[skill] = weight
                    weighted_sum += weight
                else:
                    skill_scores[skill] = 0.0
        
        # WHY: Combine weighted critical skills score with base similarity
        # WHAT: Balance critical skills importance with overall semantic similarity
        # HOW: Average the weighted score and base score
        if total_weight > 0:
            weighted_score = (weighted_sum / total_weight) * 0.5 + base_score * 0.5
        else:
            weighted_score = base_score
        
        return weighted_score, skill_scores
    
    def get_embeddings(self, text: str):
        """
        Get embeddings for a text.
        
        Args:
            text: Input text
        
        Returns:
            Tensor: Embedding vector
        """
        # WHY: Convert text to embedding vector representation
        # WHAT: Generate numerical vector for text
        # HOW: Use sentence transformer model to encode text
        # WHY: Convert text to embedding vector representation
        # WHAT: Generate numerical vector for text
        # HOW: Use sentence transformer model to encode text
        return self.model.encode(text, convert_to_tensor=True)


# Global instance for convenience
_similarity_engine = None


def get_similarity_engine(model_name: str = "all-MiniLM-L6-v2") -> SimilarityEngine:
    """
    Get or create a global similarity engine instance.
    
    Args:
        model_name: Model name
    
    Returns:
        SimilarityEngine: Engine instance
    """
    global _similarity_engine
    if _similarity_engine is None:
        _similarity_engine = SimilarityEngine(model_name)
    return _similarity_engine


def similarity_score(resume_text: str, jd_text: str) -> float:
    """
    Convenience function for computing similarity score.
    
    Args:
        resume_text: Resume text
        jd_text: Job description text
    
    Returns:
        float: Similarity score
    """
    # WHY: Provide simple interface for similarity calculation
    # WHAT: Compute similarity between resume and job description
    # HOW: Get engine instance and call compute_similarity
    engine = get_similarity_engine()
    return engine.compute_similarity(resume_text, jd_text)

