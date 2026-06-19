# Recommendation Generator Module
# Generates personalized recommendations based on skill gaps.

# PURPOSE: Generate personalized recommendations based on skill gaps and match scores
# COMPONENTS: Template-based recommendations, LLM integration, feedback formatting
# INPUTS: Missing skills, resume skills, match score
# OUTPUTS: Personalized feedback and improvement suggestions
# WORKFLOW: Analyze gaps → Generate recommendations → Format feedback
# LOGIC: Template-based or LLM-based recommendations depending on availability

# WHY: Provide actionable feedback to improve resume-job match
# WHAT: Creates personalized recommendations for skill improvement
# HOW: Uses templates or transformer models for feedback generation

# Import transformer pipeline for LLM integration
# Import transformer pipeline for LLM integration
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
# Import type hints
from typing import List, Dict
# Import PyTorch for GPU operations
import torch
# Import skill extraction functions for enhanced categorization
from embeddings.skill_extractor import get_skill_categories


class RecommendationGenerator:
    """Generates recommendations using language models."""
    
    def __init__(self, model_name: str = "gpt2", use_local: bool = True):
        """
        Initialize the recommendation generator.
        
        Args:
            model_name: Name of the language model
            use_local: Whether to use local model (True) or API (False)
        """
        self.model_name = model_name
        self.use_local = use_local
        self.generator = None
        
        if use_local:
            try:
                self.generator = pipeline(
                    "text-generation",
                    model=model_name,
                    tokenizer=model_name,
                    max_length=512,
                    device=0 if torch.cuda.is_available() else -1
                )
            except Exception as e:
                print(f"Warning: Could not load local model {model_name}: {e}")
                print("Falling back to template-based recommendations.")
                self.generator = None
    
    def generate_feedback(
        self, 
        missing_skills: List[str], 
        resume_skills: List[str] = None,
        match_score: float = None
    ) -> str:
        """
        Generate feedback and recommendations.
        
        Args:
            missing_skills: List of missing skills
            resume_skills: List of skills found in resume
            match_score: Overall match score
        
        Returns:
            str: Generated feedback
        """
        if not missing_skills:
            return self._generate_positive_feedback(resume_skills, match_score)
        
        if self.generator:
            return self._generate_with_llm(missing_skills, resume_skills, match_score)
        else:
            return self._generate_template_based(missing_skills, resume_skills, match_score)
    
    def _generate_with_llm(
        self, 
        missing_skills: List[str], 
        resume_skills: List[str] = None,
        match_score: float = None
    ) -> str:
        """Generate feedback using LLM."""
        match_score_str = f"{match_score:.2%}" if match_score else "Not provided"
        
        prompt = f"""<|system|>
You are an expert career advisor helping job seekers improve their resumes. Be specific, actionable, and encouraging. Focus on practical steps with real-world applications and market relevance.
</s>
<|user|>
Analyze the following information and provide detailed, actionable recommendations:

MATCH ANALYSIS:
- Overall Match Score: {match_score_str}
- Missing Skills: {', '.join(missing_skills[:15]) if missing_skills else 'None'}
- Current Skills: {', '.join(resume_skills[:15]) if resume_skills else 'None'}

Provide structured recommendations with:
1. Brief assessment
2. Critical skills gap analysis
3. Immediate actionable steps
4. Professional Development Strategy
5. Long-term career growth path
</s>
<|assistant|>
"""
        
        try:
            result = self.generator(
                prompt,
                max_length=512,  # Increased length for more detailed output
                min_length=150,  # Ensure sufficient content is generated
                num_return_sequences=1,
                temperature=0.6,  # Slightly lower for more focused output
                top_p=0.9,        # Use nucleus sampling for better quality
                repetition_penalty=1.2,  # Reduce repetitive text
                do_sample=True
            )
            
            # Extract the generated text after our prompt
            generated_text = result[0]['generated_text']
            # Find the part after the assistant tag
            if '<|assistant|>' in generated_text:
                response = generated_text.split('<|assistant|>')[-1].strip()
            else:
                response = generated_text[len(prompt):].strip()
            
            response = '## AI Career Advisor Recommendations\n\n' + response
            
            return response
        except Exception as e:
            print(f"Error generating with LLM: {e}")
            return self._generate_template_based(missing_skills, resume_skills, match_score)
    
    def _generate_template_based(
        self, 
        missing_skills: List[str], 
        resume_skills: List[str] = None,
        match_score: float = None
    ) -> str:
        """Generate feedback using templates."""
        feedback = "## Recommendations for Resume Enhancement\n\n"
        if match_score is not None:
            if match_score >= 0.8:
                feedback += "🎉 **Excellent Match:** Your resume aligns very well with the job requirements.\n\n"
            elif match_score >= 0.6:
                feedback += "👍 **Good Match:** Your resume shows solid alignment with the job requirements.\n\n"
            elif match_score >= 0.4:
                feedback += "⚠️ **Moderate Match:** Your resume has potential but needs some improvements.\n\n"
            else:
                feedback += "❌ **Needs Improvement:** Your resume requires significant enhancements to match the job requirements.\n\n"
        
        if missing_skills:
            feedback += f"### Skills Gap Analysis ({len(missing_skills)} skills to address)\n\n"
            feedback += "The following skills are required in the job description but not found in your resume:\n\n"
            
            # Categorize missing skills to provide more targeted recommendations
            tech_skills = []
            soft_skills = []
            tools_frameworks = []
            other_skills = []
            
            # Define categories for better recommendations
            tech_keywords = {'python', 'java', 'javascript', 'sql', 'c++', 'c#', 'go', 'rust', 'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'aws', 'azure', 'gcp', 'docker', 'kubernetes'}
            soft_keywords = {'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking', 'adaptability', 'creativity', 'collaboration', 'presentation'}
            tool_keywords = {'git', 'github', 'jira', 'confluence', 'excel', 'tableau', 'power bi', 'tensorflow', 'pytorch', 'kafka', 'spark', 'hadoop'}
            
            for skill in missing_skills[:15]:
                skill_lower = skill.lower()
                if any(keyword in skill_lower for keyword in tech_keywords):
                    tech_skills.append(skill)
                elif any(keyword in skill_lower for keyword in soft_keywords):
                    soft_skills.append(skill)
                elif any(keyword in skill_lower for keyword in tool_keywords):
                    tools_frameworks.append(skill)
                else:
                    other_skills.append(skill)
            
            # Provide specific recommendations based on skill type
            for skill in tech_skills:
                feedback += f"• **{skill.title()} (Technical)**\n"
                feedback += f"  - Take an online course (Udemy, Coursera, edX) to gain foundational knowledge\n"
                feedback += f"  - Create a small project demonstrating this skill and add it to your portfolio\n"
                feedback += f"  - Include any academic projects or coursework that used this technology\n\n"
            
            for skill in soft_skills:
                feedback += f"• **{skill.title()} (Soft Skill)**\n"
                feedback += f"  - Add specific examples in your resume of how you've demonstrated this skill\n"
                feedback += f"  - Consider volunteer work or team projects that showcase this capability\n"
                feedback += f"  - Include metrics or outcomes that resulted from this skill\n\n"
            
            for skill in tools_frameworks:
                feedback += f"• **{skill.title()} (Tool/Framework)**\n"
                feedback += f"  - Complete hands-on tutorials to gain practical experience\n"
                feedback += f"  - Document your experience with this tool in a GitHub repository\n"
                feedback += f"  - Mention any informal training or self-learning you've done\n\n"
            
            for skill in other_skills:
                feedback += f"• **{skill.title()}**\n"
                feedback += f"  - Research industry-standard certifications or training programs\n"
                feedback += f"  - Find ways to incorporate this skill into current projects\n"
                feedback += f"  - Network with professionals who use this skill daily\n\n"
        
        if resume_skills:
            feedback += f"\n### Your Strengths ({len(resume_skills)} skills identified)\n\n"
            feedback += "Skills you already possess that align with the job requirements:\n"
            feedback += ", ".join(resume_skills[:20])
            if len(resume_skills) > 20:
                feedback += f" and {len(resume_skills) - 20} more..."
            feedback += "\n\n"
            
            # Suggest how to better highlight existing skills
            feedback += "### How to Leverage Your Existing Skills\n\n"
            feedback += "1. **Reorganize Your Resume:** Place your strongest matching skills prominently in your skills section.\n"
            feedback += "2. **Quantify Impact:** Add specific metrics and achievements related to these skills.\n"
            feedback += "3. **Align Terminology:** Use the same terms from the job description for your existing skills.\n"
            feedback += "4. **Expand Descriptions:** Add more detail about how you've applied these skills in previous roles.\n\n"
        
        feedback += "### Strategic Next Steps\n\n"
        feedback += "1. **Immediate Actions (Week 1-2):** Address the most critical missing skills identified above.\n"
        feedback += "2. **Resume Optimization:** Incorporate job-specific keywords and align your experience with required skills.\n"
        feedback += "3. **Skill Building:** Dedicate 5-10 hours per week to developing the highest-priority missing skills.\n"
        feedback += "4. **Portfolio Enhancement:** Create or update projects that demonstrate the required skills.\n"
        feedback += "5. **Application Strategy:** Tailor your cover letter to highlight how you're addressing these skill gaps.\n\n"
        
        if match_score and match_score < 0.5:
            feedback += "### Priority Focus Areas\n\n"
            feedback += "Focus on acquiring these skills first as they are most critical for this role:\n"
            for i, skill in enumerate(missing_skills[:5], 1):
                feedback += f"{i}. {skill.title()}\n"
            
        return feedback
    
    def _generate_positive_feedback(self, resume_skills: List[str] = None, match_score: float = None) -> str:
        """Generate positive feedback when no skills are missing."""
        feedback = "## Excellent Match! 🎉\n\n"
        feedback += "Your resume shows a strong alignment with the job requirements.\n\n"
        
        if resume_skills:
            feedback += f"**Skills Found:** {len(resume_skills)} relevant skills identified.\n\n"
        
        if match_score:
            feedback += f"**Match Score:** {match_score:.2%}\n\n"
        
        feedback += "### Tips to Further Strengthen Your Application:\n\n"
        feedback += "1. Highlight your most relevant projects and achievements\n"
        feedback += "2. Quantify your impact with specific metrics\n"
        feedback += "3. Customize your resume summary to match the job description\n"
        feedback += "4. Prepare examples that demonstrate your key skills\n"
        
        return feedback


# Global instance for convenience
_recommendation_generator = None


def get_recommendation_generator(model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", use_local: bool = True) -> RecommendationGenerator:
    """
    Get or create a global recommendation generator instance.
    
    Args:
        model_name: Model name
        use_local: Whether to use local model
    
    Returns:
        RecommendationGenerator: Generator instance
    """
    global _recommendation_generator
    if _recommendation_generator is None:
        _recommendation_generator = RecommendationGenerator(model_name, use_local)
    return _recommendation_generator


def generate_feedback(missing_skills: List[str], resume_skills: List[str] = None, match_score: float = None) -> str:
    """
    Convenience function for generating feedback.
    
    Args:
        missing_skills: List of missing skills
        resume_skills: List of resume skills
        match_score: Match score
    
    Returns:
        str: Generated feedback
    """
    generator = get_recommendation_generator()
    return generator.generate_feedback(missing_skills, resume_skills, match_score)

