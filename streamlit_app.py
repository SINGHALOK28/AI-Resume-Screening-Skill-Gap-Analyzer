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

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import core modules for resume processing
from preprocessing.resume_parser import extract_resume_text
from preprocessing.jd_parser import extract_jd_text
from preprocessing.text_cleaner import clean_text
from embeddings.skill_extractor import extract_skills, categorize_skills, get_skill_categories
from embeddings.similarity_engine import get_similarity_engine
from generation.recommendation_generator import get_recommendation_generator
from analysis.pipeline import run_full_analysis
from config.role_profiles import get_role_profile, list_role_profiles
from config.custom_skills import build_skill_database
from preprocessing.jd_loader import load_jd_text
from utils.history import add_to_history, get_history, history_to_json
from frontend.ui_components import (
    render_score_breakdown, render_jd_tiers, render_experience,
    render_skill_confidence, render_sections, render_ats_report,
    render_interview_questions, render_resume_suggestions,
    render_learning_paths, render_charts, render_history,
)


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


def process_single_resume(resume_file, jd_text, critical_skills, skill_database=None, anonymize=False, use_llm=False):
    """Process a single resume file against job description."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("📄 Extracting text from resume...")
        progress_bar.progress(10)
        resume_text = extract_resume_text(resume_file)
        filename = getattr(resume_file, "name", "")
        
        if not resume_text or len(resume_text.strip()) < 20:
            raise Exception("Failed to extract sufficient text from resume. The file might be:\n- Password protected\n- Image-based PDF (scanned document)\n- Corrupted or empty\nPlease try a different file format or ensure the PDF contains selectable text.")
        
        resume_text = resume_text.strip()
        
        if st.session_state.get('debug_mode', False):
            st.session_state['raw_resume_text'] = resume_text[:1000]
        
        status_text.text("🤖 Loading AI model (first time may take a minute)...")
        progress_bar.progress(40)
        if 'similarity_engine' not in st.session_state:
            st.session_state['similarity_engine'] = get_similarity_engine()
        similarity_engine = st.session_state['similarity_engine']
        
        if use_llm or 'recommendation_generator' not in st.session_state:
            st.session_state['recommendation_generator'] = get_recommendation_generator(use_local=use_llm)
        recommendation_generator = st.session_state['recommendation_generator']
        
        status_text.text("🔍 Running full analysis...")
        progress_bar.progress(70)
        
        result = run_full_analysis(
            resume_text=resume_text,
            jd_text=jd_text,
            critical_skills=critical_skills or None,
            similarity_engine=similarity_engine,
            recommendation_generator=recommendation_generator,
            skill_database=skill_database,
            anonymize=anonymize,
            filename=filename,
        )
        result['filename'] = filename
        result['jd_text'] = jd_text
        result['critical_skills'] = critical_skills
        result['skill_database'] = skill_database
        result['anonymize'] = anonymize
        result['use_llm'] = use_llm
        
        if st.session_state.get('debug_mode', False):
            st.session_state['debug_resume_skills'] = result['resume_skills']
            st.session_state['debug_resume_text_sample'] = resume_text[:500].lower()
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        import time
        time.sleep(0.3)
        progress_bar.empty()
        status_text.empty()
        return result
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Error processing resume: {str(e)}")
        st.exception(e)
        return None


def process_multiple_resumes(resume_files, jd_text, critical_skills, skill_database=None, anonymize=False, use_llm=False):
    """Process multiple resume files against job description and compare."""
    st.info(f"📊 Comparing {len(resume_files)} resumes against the job description")
    
    results = []
    if 'similarity_engine' not in st.session_state:
        st.session_state['similarity_engine'] = get_similarity_engine()
    similarity_engine = st.session_state['similarity_engine']
    
    if use_llm or 'recommendation_generator' not in st.session_state:
        st.session_state['recommendation_generator'] = get_recommendation_generator(use_local=use_llm)
    recommendation_generator = st.session_state['recommendation_generator']
    
    for i, file in enumerate(resume_files):
        try:
            progress_bar = st.progress((i + 1) / len(resume_files))
            status_text = st.empty()
            status_text.text(f"📄 Processing resume {i+1}/{len(resume_files)}: {file.name}...")
            
            resume_text = extract_resume_text(file)
            if not resume_text or len(resume_text.strip()) < 20:
                st.warning(f"⚠️ Could not extract sufficient text from {file.name}")
                continue
            
            result = run_full_analysis(
                resume_text=resume_text.strip(),
                jd_text=jd_text,
                critical_skills=critical_skills or None,
                similarity_engine=similarity_engine,
                recommendation_generator=recommendation_generator,
                skill_database=skill_database,
                anonymize=anonymize,
                filename=file.name,
            )
            result['filename'] = file.name
            results.append(result)
            progress_bar.empty()
            status_text.empty()
        except Exception as e:
            st.warning(f"⚠️ Error processing {file.name}: {str(e)}")
            continue
    
    if not results:
        st.error("❌ No resumes could be processed successfully.")
        return []
    
    results.sort(key=lambda x: x.get('composite_score', x.get('match_score', 0)), reverse=True)
    st.session_state['group_results'] = results
    st.success(f"✅ Analysis complete! Compared {len(results)} resumes.")
    
    df_data = [{
        'Rank': i + 1,
        'Resume': r['filename'],
        'Composite Score': r.get('composite_score', r['match_score']),
        'Match Score': r['match_score'],
        'Skills Found': len(r['resume_skills']),
        'Missing Skills': len(r['missing_skills']),
        'Must-Have Missing': len(r.get('missing_must_have', [])),
        'ATS Score': r.get('ats_report', {}).get('ats_score', 'N/A'),
        'Raw Skills': r['resume_skills']
    } for i, r in enumerate(results)]
    
    st.subheader("🔍 Advanced Candidate Filtering")
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        min_score = st.slider("Minimum Composite Score (%)", 0, 100, 0)
    with col_filter2:
        all_skills_in_batch = sorted(list(set(skill for r in results for skill in r['resume_skills'])))
        required_skills = st.multiselect("Must contain skills", options=all_skills_in_batch)
    
    filtered_data = []
    for row in df_data:
        if row['Composite Score'] * 100 < min_score:
            continue
        if required_skills and not all(s in row['Raw Skills'] for s in required_skills):
            continue
        
        # Format for display
        filtered_row = row.copy()
        filtered_row['Composite Score'] = f"{row['Composite Score']:.2%}"
        filtered_row['Match Score'] = f"{row['Match Score']:.2%}"
        del filtered_row['Raw Skills']
        filtered_data.append(filtered_row)
        
    if not filtered_data:
        st.warning("No candidates match the current filters.")
    else:
        filtered_df = pd.DataFrame(filtered_data)
        st.dataframe(filtered_df, use_container_width=True)
        
        st.download_button(
            label="📥 Download Filtered Results CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name="resume_comparison_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )
    
    st.subheader("🏆 Top Candidates")
    for i, res in enumerate(results[:3]):
        score = res.get('composite_score', res['match_score'])
        score_color = "#2E8B57" if score >= 0.7 else "#FF8C00" if score >= 0.4 else "#DC143C"
        st.markdown(
            f"<div style='background-color: {score_color}; padding: 10px; border-radius: 5px; margin: 5px 0;'>"
            f"<strong>{res['filename']}</strong> - Score: {score:.2%}</div>",
            unsafe_allow_html=True,
        )
        if res['resume_skills']:
            st.write(f"**Skills:** {', '.join(res['resume_skills'][:5])}")
        if res.get('missing_must_have'):
            st.write(f"**Missing must-have:** {', '.join(res['missing_must_have'][:5])}")
    
    if results:
        st.session_state['results'] = results[0]
    
    return results


def display_debug_info():
    """Display debug information if enabled."""
    if st.session_state.get('debug_mode', False) and 'results' in st.session_state:
        with st.expander("🔧 Debug: Extracted Resume Text Preview", expanded=False):
            results = st.session_state['results']
            preview_text = results.get('raw_resume_text', 'No text extracted')
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
    if 'results' not in st.session_state:
        return
    results = st.session_state['results']
    
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    composite = results.get('composite_score', results['match_score'])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Composite Score", f"{composite:.2%}")
    with col2:
        st.metric("Match Score", f"{results['match_score']:.2%}")
    with col3:
        st.metric("Resume Skills", len(results['resume_skills']))
    with col4:
        st.metric("Missing Skills", len(results['missing_skills']))
    
    tabs = st.tabs([
        "✏️ Editor", "Overview", "Scoring", "Skills", "Experience", "ATS",
        "Interview", "Suggestions", "Learning", "Charts",
    ])
    
    with tabs[0]:
        st.info("Review the raw text extracted from the resume and adjust the detected skills if the AI missed anything.")
        col_text, col_skills = st.columns([1, 1])
        with col_text:
            st.text_area("Raw Resume Text", results.get('raw_resume_text', 'No text found'), height=400, disabled=True)
            
        with col_skills:
            from embeddings.skill_extractor import TECHNICAL_SKILLS, SOFT_SKILLS
            all_options = sorted(list(set(list(TECHNICAL_SKILLS.union(SOFT_SKILLS)) + results['resume_skills'])))
            
            edited_skills = st.multiselect(
                "Extracted Skills (Add/Remove as needed)",
                options=all_options,
                default=results['resume_skills']
            )
            
            if st.button("Recalculate Analysis", type="primary"):
                with st.spinner("Recalculating with updated skills..."):
                    from analysis.pipeline import run_full_analysis
                    
                    new_result = run_full_analysis(
                        resume_text=results['raw_resume_text'],
                        jd_text=results.get('jd_text', ''),
                        critical_skills=results.get('critical_skills'),
                        similarity_engine=st.session_state['similarity_engine'],
                        recommendation_generator=st.session_state['recommendation_generator'],
                        skill_database=results.get('skill_database'),
                        anonymize=results.get('anonymize', False),
                        filename=results.get('filename', ''),
                        override_resume_skills=edited_skills
                    )
                    
                    new_result['filename'] = results.get('filename', '')
                    new_result['jd_text'] = results.get('jd_text', '')
                    new_result['critical_skills'] = results.get('critical_skills')
                    new_result['skill_database'] = results.get('skill_database')
                    new_result['anonymize'] = results.get('anonymize', False)
                    new_result['use_llm'] = results.get('use_llm', False)
                    
                    st.session_state['results'] = new_result
                    st.rerun()
                    
    with tabs[1]:
        render_jd_tiers(results)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Skills Found in Resume")
            if results['resume_skills']:
                categorized = categorize_skills(results['resume_skills'])
                for category, skills in categorized.items():
                    st.markdown(f"**{category.replace('_', ' ').title()}:**")
                    skills_display = " ".join([f"<span class='skill-badge'>{skill}</span>" for skill in skills[:20]])
                    st.markdown(skills_display, unsafe_allow_html=True)
            else:
                st.info("No skills extracted from resume.")
        with col2:
            st.subheader("📋 Skills in Job Description")
            if results['jd_skills']:
                categorized = categorize_skills(results['jd_skills'])
                for category, skills in categorized.items():
                    st.markdown(f"**{category.replace('_', ' ').title()}:**")
                    skills_display = " ".join([f"<span class='skill-badge'>{skill}</span>" for skill in skills[:20]])
                    st.markdown(skills_display, unsafe_allow_html=True)
            else:
                st.info("No skills extracted from job description.")
        if results['missing_skills']:
            st.subheader("❌ Missing Skills")
            missing_display = " ".join([
                f"<span class='skill-badge missing-skill'>{skill}</span>"
                for skill in results['missing_skills'][:30]
            ])
            st.markdown(missing_display, unsafe_allow_html=True)
        if results.get('critical_skills_scores'):
            st.subheader("⭐ Critical Skills Analysis")
            st.dataframe(pd.DataFrame({
                'Skill': list(results['critical_skills_scores'].keys()),
                'Score': [f"{v:.2%}" for v in results['critical_skills_scores'].values()],
            }), use_container_width=True, hide_index=True)
        st.subheader("💡 AI Recommendations")
        st.markdown(results['feedback'])
    
    with tabs[2]:
        if results.get('score_breakdown'):
            render_score_breakdown(results['score_breakdown'])
    
    with tabs[3]:
        render_skill_confidence(results.get('skill_confidence', []))
        render_sections(results.get('section_skills', {}))
    
    with tabs[4]:
        render_experience(results)
    
    with tabs[5]:
        render_ats_report(results.get('ats_report', {}))
    
    with tabs[6]:
        render_interview_questions(results.get('interview_questions', []))
    
    with tabs[7]:
        render_resume_suggestions(results.get('resume_suggestions', []))
    
    with tabs[8]:
        render_learning_paths(results.get('learning_paths', []))
    
    with tabs[9]:
        group = st.session_state.get('group_results')
        render_charts(results, group_results=group)
    
    st.markdown("---")
    st.subheader("📥 Export Results")
    pdf_buffer = generate_pdf_report(
        results['resume_skills'],
        results['jd_skills'],
        results['missing_skills'],
        results.get('composite_score', results['match_score']),
        results['feedback'],
        results.get('critical_skills_scores', {}),
    )
    candidate_name = st.session_state.get('candidate_name', '')
    sanitized_name = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    file_name = f"resume_analysis_report_{sanitized_name.replace(' ', '_')}.pdf" if sanitized_name else "resume_analysis_report.pdf"
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_buffer,
        file_name=file_name,
        mime="application/pdf",
        use_container_width=True,
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

    with st.sidebar:
        st.header("⚙️ Configuration")
        
        role_profile = st.selectbox(
            "Role Profile",
            options=list_role_profiles(),
            help="Pre-fill critical skills for common roles",
        )
        profile_skills = get_role_profile(role_profile)
        
        st.subheader("Critical Skills (Optional)")
        default_critical = "\n".join(f"{k}:{v}" for k, v in profile_skills.items()) if profile_skills else ""
        critical_skills_text = st.text_area(
            "Critical skills (skill:weight per line)",
            value=default_critical,
            height=120,
            help="Example:\npython:2.0\nmachine learning:1.5",
            key=f"critical_skills_{role_profile}",
        )
        
        critical_skills = {}
        if critical_skills_text:
            for line in critical_skills_text.strip().split('\n'):
                if ':' in line:
                    parts = line.split(':')
                    skill = parts[0].strip()
                    try:
                        critical_skills[skill] = float(parts[1].strip())
                    except ValueError:
                        critical_skills[skill] = 1.0
                elif line.strip():
                    critical_skills[line.strip()] = 1.0
        
        st.subheader("Custom Skill Database")
        custom_skills_text = st.text_area(
            "Add company-specific skills (one per line)",
            height=80,
            placeholder="internal-tool\nproprietary-api",
        )
        skill_database = build_skill_database(custom_skills_text)
        
        st.markdown("---")
        anonymize = st.checkbox("🕵️ Anonymized Screening", help="Remove PII before scoring")
        use_llm = st.checkbox("🧠 LLM Recommendations", help="Use local LLM (slower, needs GPU). Falls back to templates.")
        debug_mode = st.checkbox("🔧 Debug Mode")
        st.session_state['debug_mode'] = debug_mode
        
        st.markdown("---")
        with st.expander("🕐 Analysis History"):
            render_history(get_history(st.session_state))
            if get_history(st.session_state):
                st.download_button(
                    "Download History JSON",
                    data=history_to_json(st.session_state),
                    file_name="analysis_history.json",
                    mime="application/json",
                )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Upload Resume(s)")
        if analysis_mode == "Single Resume":
            resume_file = st.file_uploader(
                "Choose a PDF or DOCX file",
                type=['pdf', 'docx', 'doc'],
                accept_multiple_files=False,
            )
        else:
            resume_file = st.file_uploader(
                "Choose PDF or DOCX files",
                type=['pdf', 'docx', 'doc'],
                accept_multiple_files=True,
            )
    
    with col2:
        st.subheader("📋 Job Description")
        jd_text = st.text_area("Paste job description", height=150)
        jd_file = st.file_uploader(
            "Or upload JD file (PDF/DOCX)",
            type=['pdf', 'docx', 'doc'],
            key="jd_file",
        )
    
    st.session_state['candidate_name'] = candidate_name

    if st.button(f"🔍 Analyze {analysis_mode}", type="primary", use_container_width=True):
        if not resume_file:
            st.error(f"❌ Please upload at least one resume file for {analysis_mode} analysis.")
            return
        
        combined_jd = load_jd_text(jd_text, jd_file)
        if not combined_jd:
            st.error("❌ Please provide a job description (paste text or upload a file).")
            return
        
        kwargs = dict(
            critical_skills=critical_skills,
            skill_database=skill_database,
            anonymize=anonymize,
            use_llm=use_llm,
        )
        
        if analysis_mode == "Group Resumes":
            results = process_multiple_resumes(resume_file, combined_jd, **kwargs)
            for r in results:
                add_to_history(st.session_state, r, candidate_name, mode="group")
        else:
            result = process_single_resume(resume_file, combined_jd, **kwargs)
            if result:
                st.session_state['results'] = result
                add_to_history(st.session_state, result, candidate_name, mode="single")
    
    # Display debug info if enabled
    display_debug_info()
    
    # Display results if available
    display_results()


if __name__ == "__main__":
    main()
