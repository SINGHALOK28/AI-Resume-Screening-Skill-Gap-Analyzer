"""
AI Resume Screening Application
Streamlit UI for resume-job matching with skill gap analysis
"""

# Imports for the Streamlit web interface
import streamlit as st
import sys
import os
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import core modules for resume processing
from preprocessing.resume_parser import extract_resume_text
from preprocessing.jd_parser import extract_jd_text
from preprocessing.text_cleaner import clean_text
from embeddings.skill_extractor import extract_skills, categorize_skills, get_skill_categories
from embeddings.similarity_engine import get_similarity_engine
from generation.recommendation_generator import get_recommendation_generator



def setup_page():
    """Configure Streamlit page settings and custom CSS."""
    # Page configuration
    st.set_page_config(
        page_title="AI Resume Screening System",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for UI styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .skill-badge {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            margin: 0.25rem;
            font-size: 0.85rem;
        }
        .missing-skill {
            background-color: #f44336;
        }
        </style>
    """, unsafe_allow_html=True)


def generate_pdf_report(
    resume_skills: list,
    jd_skills: list,
    missing_skills: list,
    match_score: float,
    feedback: str,
    critical_skills_scores: dict = None
) -> BytesIO:
    """Generate PDF report of the analysis."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles for the PDF
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1f77b4',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#333333',
        spaceAfter=12
    )
    
    # Build PDF content
    story.append(Paragraph("AI Resume Screening Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Match Score
    story.append(Paragraph(f"<b>Overall Match Score: {match_score:.2%}</b>", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Resume Skills
    story.append(Paragraph("Resume Skills", heading_style))
    if resume_skills:
        skills_text = ", ".join(resume_skills[:30])
        story.append(Paragraph(skills_text, styles['Normal']))
    else:
        story.append(Paragraph("No skills extracted.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Job Description Skills
    story.append(Paragraph("Job Description Skills", heading_style))
    if jd_skills:
        skills_text = ", ".join(jd_skills[:30])
        story.append(Paragraph(skills_text, styles['Normal']))
    else:
        story.append(Paragraph("No skills extracted.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Missing Skills
    if missing_skills:
        story.append(Paragraph("Missing Skills", heading_style))
        for skill in missing_skills[:20]:
            story.append(Paragraph(f"• {skill}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Critical Skills Analysis
    if critical_skills_scores:
        story.append(Paragraph("Critical Skills Analysis", heading_style))
        for skill, score in list(critical_skills_scores.items())[:10]:
            story.append(Paragraph(f"• {skill}: {score:.2%}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Recommendations
    story.append(Paragraph("Recommendations", heading_style))
    # Clean HTML tags from feedback for PDF
    feedback_clean = feedback.replace("##", "").replace("###", "").replace("**", "").replace("✅", "").replace("⚠️", "").replace("❌", "")
    for line in feedback_clean.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def process_single_resume(resume_file, jd_text, critical_skills):
    """Process a single resume file against job description."""
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Extract resume text
        status_text.text("📄 Extracting text from resume...")
        progress_bar.progress(10)
        resume_text = extract_resume_text(resume_file)
        
        # Validate extraction
        if not resume_text or len(resume_text.strip()) < 20:
            raise Exception("Failed to extract sufficient text from resume. The file might be:\n"
                          "- Password protected\n"
                          "- Image-based PDF (scanned document)\n"
                          "- Corrupted or empty\n"
                          "Please try a different file format or ensure the PDF contains selectable text.")
        
        # Note: resume_text is already cleaned in extract_resume_text
        # Only do light cleaning if needed (the extract_resume_text already cleaned it)
        # Don't over-clean as it might remove important skill information
        if len(resume_text) > 0:
            # Just ensure it's properly formatted, don't remove important content
            resume_text = resume_text.strip()
        
        # Store raw text for debugging (optional)
        if 'debug_mode' in st.session_state and st.session_state.get('debug_mode', False):
            st.session_state['raw_resume_text'] = resume_text[:1000]  # First 1000 chars
        
        # Step 2: Process job description
        status_text.text("📋 Processing job description...")
        progress_bar.progress(20)
        jd_text_processed = extract_jd_text(jd_text)
        jd_text_processed = clean_text(jd_text_processed)
        
        # Step 3: Extract skills
        status_text.text("🔍 Extracting skills from resume and job description...")
        progress_bar.progress(40)
        
        # Extract skills - use original text before final cleaning for better matching
        # The text has already been cleaned in extract_resume_text, so we use it as-is
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text_processed)
        
        # Debug: Show what was found
        if st.session_state.get('debug_mode', False):
            st.session_state['debug_resume_skills'] = resume_skills
            st.session_state['debug_resume_text_sample'] = resume_text[:500].lower()
        
        # Step 4: Find missing skills
        status_text.text("📊 Analyzing skill gaps...")
        progress_bar.progress(50)
        resume_skills_lower = [s.lower() for s in resume_skills]
        missing_skills = [skill for skill in jd_skills if skill.lower() not in resume_skills_lower]
        
        # Step 5: Load similarity engine (cached in session state)
        status_text.text("🤖 Loading AI model (first time may take a minute)...")
        progress_bar.progress(60)
        if 'similarity_engine' not in st.session_state:
            similarity_engine = get_similarity_engine()
            st.session_state['similarity_engine'] = similarity_engine
        else:
            similarity_engine = st.session_state['similarity_engine']
        
        # Step 6: Compute similarity
        status_text.text("🧮 Computing semantic similarity...")
        progress_bar.progress(75)
        if critical_skills:
            match_score, critical_skills_scores = similarity_engine.compute_weighted_similarity(
                resume_text, jd_text_processed, critical_skills
            )
        else:
            match_score = similarity_engine.compute_similarity(resume_text, jd_text_processed)
            critical_skills_scores = {}
        
        # Step 7: Generate recommendations (use template-based for speed)
        status_text.text("💡 Generating recommendations...")
        progress_bar.progress(90)
        if 'recommendation_generator' not in st.session_state:
            recommendation_generator = get_recommendation_generator(use_local=False)  # Use template-based for speed
            st.session_state['recommendation_generator'] = recommendation_generator
        else:
            recommendation_generator = st.session_state['recommendation_generator']
        
        feedback = recommendation_generator.generate_feedback(
            missing_skills, resume_skills, match_score
        )
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Small delay to show completion
        import time
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
            
        # Store results in session state
        return {
            'resume_skills': resume_skills,
            'jd_skills': jd_skills,
            'missing_skills': missing_skills,
            'match_score': match_score,
            'feedback': feedback,
            'critical_skills_scores': critical_skills_scores,
            'resume_text': resume_text[:1000] if len(resume_text) > 1000 else resume_text,  # Store preview for debug
            'resume_text_length': len(resume_text)  # Store full length
        }
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Error processing resume: {str(e)}")
        st.exception(e)
        return None


def process_multiple_resumes(resume_files, jd_text, critical_skills):
    """Process multiple resume files against job description and compare."""
    st.info(f"📊 Comparing {len(resume_files)} resumes against the job description")
    
    results = []
    for i, file in enumerate(resume_files):
        try:
            # Progress tracking
            progress_bar = st.progress((i+1)/len(resume_files))
            status_text = st.empty()
            status_text.text(f"📄 Processing resume {i+1}/{len(resume_files)}: {file.name}...")
            
            # Extract resume text
            resume_text = extract_resume_text(file)
            
            # Validate extraction
            if not resume_text or len(resume_text.strip()) < 20:
                st.warning(f"⚠️ Could not extract sufficient text from {file.name}")
                continue
            
            # Process job description
            jd_text_processed = extract_jd_text(jd_text)
            jd_text_processed = clean_text(jd_text_processed)
            
            # Extract skills
            resume_skills = extract_skills(resume_text)
            jd_skills = extract_skills(jd_text_processed)
            
            # Find missing skills
            resume_skills_lower = [s.lower() for s in resume_skills]
            missing_skills = [skill for skill in jd_skills if skill.lower() not in resume_skills_lower]
            
            # Load similarity engine
            if 'similarity_engine' not in st.session_state:
                similarity_engine = get_similarity_engine()
                st.session_state['similarity_engine'] = similarity_engine
            else:
                similarity_engine = st.session_state['similarity_engine']
            
            # Compute similarity
            if critical_skills:
                match_score, critical_skills_scores = similarity_engine.compute_weighted_similarity(
                    resume_text, jd_text_processed, critical_skills
                )
            else:
                match_score = similarity_engine.compute_similarity(resume_text, jd_text_processed)
                critical_skills_scores = {}
            
            # Generate recommendations for the top candidate only
            if i == 0:  # Generate detailed feedback for the best match
                if 'recommendation_generator' not in st.session_state:
                    recommendation_generator = get_recommendation_generator(use_local=False)
                    st.session_state['recommendation_generator'] = recommendation_generator
                else:
                    recommendation_generator = st.session_state['recommendation_generator']

                feedback = recommendation_generator.generate_feedback(
                    missing_skills, 
                    resume_skills, 
                    match_score
                )
            else:
                feedback = ""  # Only generate detailed feedback for top match
            
            # Store results
            results.append({
                'filename': file.name,
                'match_score': match_score,
                'resume_skills': resume_skills,
                'jd_skills': jd_skills,
                'missing_skills': missing_skills,
                'feedback': feedback,
                'critical_skills_scores': critical_skills_scores,
                'resume_text': resume_text[:1000] if len(resume_text) > 1000 else resume_text,
                'resume_text_length': len(resume_text)
            })
        except Exception as e:
            st.warning(f"⚠️ Error processing {file.name}: {str(e)}")
            continue
    
    # Sort results by match score
    results.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Display comparison results
    st.success(f"✅ Analysis complete! Compared {len(results)} resumes.")
    
    # Comparison table
    comparison_data = []
    for res in results:
        comparison_data.append({
            'Resume': res['filename'],
            'Match Score': f"{res['match_score']:.2%}",
            'Skills Found': len(res['resume_skills']),
            'Missing Skills': len(res['missing_skills'])
        })
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)
    
    # Show top 3 candidates
    st.subheader("🏆 Top Candidates")
    for i, res in enumerate(results[:3]):
        with st.container():
            score_color = "#2E8B57" if res['match_score'] >= 0.7 else "#FF8C00" if res['match_score'] >= 0.4 else "#DC143C"
            html_content = f"<div style='background-color: {score_color}; padding: 10px; border-radius: 5px; margin: 5px 0;'><strong>{res['filename']}</strong> - Match Score: {res['match_score']:.2%}</div>"
            st.markdown(html_content, unsafe_allow_html=True)
            
            # Show key skills
            if res['resume_skills']:
                st.write(f"**Skills ({len(res['resume_skills'])}):** {', '.join(res['resume_skills'][:5])}{', ...' if len(res['resume_skills']) > 5 else ''}")
            if res['missing_skills']:
                st.write(f"**Missing ({len(res['missing_skills'])}):** {', '.join(res['missing_skills'][:5])}{', ...' if len(res['missing_skills']) > 5 else ''}")
            
            if i == 0:  # Only show detailed feedback for top candidate
                st.session_state['results'] = res  # Store top result for detailed view
    
    # Show all resume comparisons side-by-side
    st.subheader("📋 All Resume Comparisons")
    
    # Create a dataframe with detailed comparison
    detailed_comparison_data = []
    for res in results:
        detailed_comparison_data.append({
            'Resume': res['filename'],
            'Match Score': f"{res['match_score']:.2%}",
            'Skills Found': len(res['resume_skills']),
            'Missing Skills': len(res['missing_skills']),
            'Resume Skills': ', '.join(res['resume_skills'][:5]) + ('...' if len(res['resume_skills']) > 5 else ''),
            'JD Skills': ', '.join(res['jd_skills'][:5]) + ('...' if len(res['jd_skills']) > 5 else ''),
            'Top Missing Skills': ', '.join(res['missing_skills'][:5]) + ('...' if len(res['missing_skills']) > 5 else '')
        })
    
    detailed_df = pd.DataFrame(detailed_comparison_data)
    st.dataframe(detailed_df, use_container_width=True)
    
    # Only show detailed view for top candidate
    if results:
        top_result = results[0]
        st.subheader(f"💡 Detailed Analysis for Top Candidate: {top_result['filename']}")
        
        # Store top result for the detailed view
        st.session_state['results'] = top_result
        
    return results


def display_debug_info():
    """Display debug information if enabled."""
    if st.session_state.get('debug_mode', False) and 'results' in st.session_state:
        with st.expander("🔧 Debug: Extracted Resume Text Preview", expanded=False):
            results = st.session_state['results']
            preview_text = results.get('resume_text', 'No text extracted')
            total_length = results.get('resume_text_length', len(preview_text))
            st.text_area("Extracted text preview (first 1000 chars):", preview_text, height=200, disabled=True)
            st.caption(f"Total characters extracted: {total_length}")
            if total_length < 50:
                st.warning("⚠️ Very little text was extracted. The resume might be image-based or corrupted.")
        
        # Debug skill extraction
        with st.expander("🔧 Debug: Skill Extraction Analysis", expanded=False):
            if 'debug_resume_skills' in st.session_state:
                st.write("**Skills Found:**", st.session_state['debug_resume_skills'])
                st.write("**Number of skills:**", len(st.session_state['debug_resume_skills']))
                
                # Show sample text that was searched
                if 'debug_resume_text_sample' in st.session_state:
                    st.write("**Sample text searched (first 500 chars):**")
                    st.text(st.session_state['debug_resume_text_sample'])
                
                # Show which skills from database were checked
                from embeddings.skill_extractor import TECHNICAL_SKILLS, SOFT_SKILLS
                all_skills = TECHNICAL_SKILLS.union(SOFT_SKILLS)
                st.write(f"**Total skills in database:** {len(all_skills)}")
                
                # Show a few example skills that should match
                sample_text = st.session_state.get('debug_resume_text_sample', '').lower()
                if sample_text:
                    st.write("**Testing a few common skills:**")
                    test_skills = ['python', 'java', 'sql', 'javascript', 'html', 'css', 'machine learning']
                    for test_skill in test_skills:
                        if test_skill in sample_text:
                            st.write(f"✅ '{test_skill}' found in text")
                        else:
                            st.write(f"❌ '{test_skill}' NOT found in text")
            else:
                st.info("Run an analysis first to see debug information.")


def display_results():
    """Display analysis results."""
    if 'results' in st.session_state:
        results = st.session_state['results']
        
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        # Match Score
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Match Score", f"{results['match_score']:.2%}")
        with col2:
            st.metric("Resume Skills", len(results['resume_skills']))
        with col3:
            st.metric("Missing Skills", len(results['missing_skills']))
        
        # Skills comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Skills Found in Resume")
            if results['resume_skills']:
                categorized = categorize_skills(results['resume_skills'])
                for category, skills in categorized.items():
                    st.markdown(f"**{category.replace('_', ' ').title()}:**")
                    skills_display = " ".join([f'<span class="skill-badge">{skill}</span>' for skill in skills[:20]])
                    st.markdown(skills_display, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.info("No skills extracted from resume.")
        
        with col2:
            st.subheader("📋 Skills in Job Description")
            if results['jd_skills']:
                categorized = categorize_skills(results['jd_skills'])
                for category, skills in categorized.items():
                    st.markdown(f"**{category.replace('_', ' ').title()}:**")
                    skills_display = " ".join([f'<span class="skill-badge">{skill}</span>' for skill in skills[:20]])
                    st.markdown(skills_display, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.info("No skills extracted from job description.")
        
        # Missing Skills
        if results['missing_skills']:
            st.subheader("❌ Missing Skills")
            missing_display = " ".join([
                f'<span class="skill-badge missing-skill">{skill}</span>' 
                for skill in results['missing_skills'][:30]
            ])
            st.markdown(missing_display, unsafe_allow_html=True)
        
        # Critical Skills Analysis
        if results['critical_skills_scores']:
            st.subheader("⭐ Critical Skills Analysis")
            critical_df_data = {
                'Skill': list(results['critical_skills_scores'].keys()),
                'Score': [f"{v:.2%}" for v in results['critical_skills_scores'].values()]
            }
            st.dataframe(pd.DataFrame(critical_df_data), use_container_width=True)
        
        # Recommendations
        st.subheader("💡 AI Recommendations")
        st.markdown(results['feedback'])
        
        # PDF Export
        st.markdown("---")
        st.subheader("📥 Export Results")
        
        pdf_buffer = generate_pdf_report(
            results['resume_skills'],
            results['jd_skills'],
            results['missing_skills'],
            results['match_score'],
            results['feedback'],
            results.get('critical_skills_scores', {})
        )
        
        # Get candidate name from session state for filename
        candidate_name = st.session_state.get('candidate_name', '')
        # Sanitize candidate name for use in filename
        sanitized_name = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if sanitized_name:
            file_name = f"resume_analysis_report_{sanitized_name.replace(' ', '_')}.pdf"
        else:
            file_name = "resume_analysis_report.pdf"
        
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_buffer,
            file_name=file_name,
            mime="application/pdf",
            use_container_width=True
        )


def main():
    """Main application function."""
    # Setup page configuration and styling
    setup_page()
    
    st.markdown('<div class="main-header">📄 AI Resume Screening & Skill Gap Analyzer</div>', unsafe_allow_html=True)
    
    # Name input for candidate
    candidate_name = st.text_input(
        "Candidate Name",
        placeholder="Enter candidate's name for PDF report",
        help="Name will be used in the PDF report filename"
    )
    
    # Analysis mode selection
    analysis_mode = st.radio(
        "Analysis Mode",
        options=["Single Resume", "Group Resumes"],
        horizontal=True,
        help="Choose between single resume analysis or group comparison"
    )
    
    # Info banner for first-time users
    if 'similarity_engine' not in st.session_state:
        st.info("ℹ️ **First time?** The AI model will download on first use (~80MB, takes 1-2 minutes). Subsequent runs will be much faster!")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Critical skills input
        st.subheader("Critical Skills (Optional)")
        critical_skills_text = st.text_area(
            "Enter critical skills (one per line) with optional weights (format: skill:weight)",
            height=150,
            help="Example:\npython:2.0\nmachine learning:1.5\nsql:1.0"
        )

        critical_skills = {}
        if critical_skills_text:
            for line in critical_skills_text.strip().split('\n'):
                if ':' in line:
                    parts = line.split(':')
                    skill = parts[0].strip()
                    try:
                        weight = float(parts[1].strip())
                        critical_skills[skill] = weight
                    except:
                        critical_skills[skill] = 1.0
                else:
                    critical_skills[line.strip()] = 1.0
        
        st.markdown("---")
        
        # Debug mode toggle
        debug_mode = st.checkbox("🔧 Debug Mode", help="Show extracted text preview and debugging info")
        st.session_state['debug_mode'] = debug_mode
        
        st.markdown("---")
        st.info("💡 **Tip:** Add critical skills to get weighted scoring and better recommendations.")
    
    # Main content with two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Upload Resume(s)")
        if analysis_mode == "Single Resume":
            resume_file = st.file_uploader(
                "Choose a PDF or DOCX file",
                type=['pdf', 'docx', 'doc'],
                help="Upload a single resume in PDF or DOCX format",
                accept_multiple_files=False
            )
        else:  # Group Resumes mode
            resume_file = st.file_uploader(
                "Choose PDF or DOCX files",
                type=['pdf', 'docx', 'doc'],
                help="Upload multiple resumes in PDF or DOCX format",
                accept_multiple_files=True
            )
    
    with col2:
        st.subheader("📋 Job Description")
        jd_text = st.text_area(
            "Paste the job description here",
            height=200,
            help="Paste the complete job description text"
        )
    
    # Store candidate name in session state
    st.session_state['candidate_name'] = candidate_name

    # Process button
    if st.button(f"🔍 Analyze {analysis_mode}", type="primary", use_container_width=True):
        if not resume_file:
            st.error(f"❌ Please upload at least one resume file for {analysis_mode} analysis.")
            return
        
        if not jd_text:
            st.error("❌ Please provide a job description.")
            return
        
        # Handle single vs multiple resume processing
        if analysis_mode == "Group Resumes":
            # Process multiple resumes with comparison
            process_multiple_resumes(resume_file, jd_text, critical_skills)
        else:
            # Process single resume
            result = process_single_resume(resume_file, jd_text, critical_skills)
            if result:
                st.session_state['results'] = result
    
    # Display debug info if enabled
    display_debug_info()
    
    # Display results if available
    display_results()


if __name__ == "__main__":
    main()