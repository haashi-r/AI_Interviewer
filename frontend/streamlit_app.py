import streamlit as st
import sys
import os
import asyncio
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import backend components
from core.interview_agent import interview_agent
from core.evaluator import evaluator
from utils.report_generator import report_generator
from config.settings import settings

# Page configuration
st.set_page_config(
    page_title="Excel Mock Interviewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2E86AB;
    }
    
    .user-message {
        background: #e3f2fd;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #2196F3;
    }
    
    .assistant-message {
        background: #f3e5f5;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #9C27B0;
    }
    
    .progress-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .metric-card {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 8px;
        border-left: 4px solid #2E86AB;
    }
    
    .score-display {
        font-size: 2rem;
        font-weight: bold;
        color: #2E86AB;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize Streamlit session state"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = "not_started"
    if 'candidate_name' not in st.session_state:
        st.session_state.candidate_name = ""
    if 'candidate_email' not in st.session_state:
        st.session_state.candidate_email = ""
    if 'evaluation_complete' not in st.session_state:
        st.session_state.evaluation_complete = False
    if 'final_evaluation' not in st.session_state:
        st.session_state.final_evaluation = None

def display_header():
    """Display main application header"""
    st.markdown("""
    <div class="main-header">
        <h1>📊 AI-Powered Excel Mock Interviewer</h1>
        <p>Comprehensive Excel Skills Assessment</p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with progress and information"""
    with st.sidebar:
        st.header("📈 Interview Progress")
        
        if st.session_state.session_id:
            progress = interview_agent.get_interview_progress(st.session_state.session_id)
            
            if "error" not in progress:
                st.markdown(f"**Candidate:** {progress.get('candidate_name', 'N/A')}")
                st.markdown(f"**Phase:** {progress.get('phase', 'Unknown').title()}")
                st.markdown(f"**Questions Answered:** {progress.get('questions_answered', 0)}")
                
                # Progress bar
                max_questions = settings.MAX_QUESTIONS
                progress_percent = min(100, (progress.get('questions_answered', 0) / max_questions) * 100)
                st.progress(progress_percent / 100)
                
                # Current score
                if progress.get('current_score', 0) > 0:
                    st.markdown("### Current Performance")
                    st.markdown(f"<div class='score-display'>{progress['current_score']:.1f}%</div>", unsafe_allow_html=True)
                
                # Elapsed time
                elapsed_minutes = progress.get('elapsed_time', 0)
                st.markdown(f"**Time Elapsed:** {elapsed_minutes:.1f} minutes")
                
                # Difficulty level
                st.markdown(f"**Current Level:** {progress.get('difficulty_level', 'Basic').title()}")
                
                # Category performance
                if progress.get('category_performance'):
                    st.markdown("### Category Performance")
                    for category, score in progress['category_performance'].items():
                        st.markdown(f"**{category}:** {score:.1f}%")
        
        else:
            st.info("Start an interview to see progress")
        
        # Information section
        st.markdown("---")
        st.header("ℹ️ About This Assessment")
        st.markdown("""
        **What we evaluate:**
        - Technical accuracy (40%)
        - Depth of knowledge (25%)
        - Problem-solving approach (20%)
        - Communication clarity (15%)
        
        **Duration:** 20-25 minutes
        **Questions:** Up to 15 adaptive questions
        **Difficulty:** Automatically adjusts based on performance
        """)
        
        # Reset button
        if st.session_state.interview_started:
            st.markdown("---")
            if st.button("🔄 Reset Interview", type="secondary"):
                reset_interview()

def reset_interview():
    """Reset interview session"""
    if st.session_state.session_id:
        interview_agent.cleanup_session(st.session_state.session_id)
    
    # Clear session state
    st.session_state.session_id = None
    st.session_state.interview_started = False
    st.session_state.conversation_history = []
    st.session_state.current_phase = "not_started"
    st.session_state.candidate_name = ""
    st.session_state.candidate_email = ""
    st.session_state.evaluation_complete = False
    st.session_state.final_evaluation = None
    
    st.rerun()

def start_interview_form():
    """Display form to start new interview"""
    st.header("🚀 Start Your Excel Skills Assessment")
    
    with st.form("start_interview"):
        col1, col2 = st.columns(2)
        
        with col1:
            candidate_name = st.text_input(
                "Full Name *",
                placeholder="Enter your full name",
                help="This will appear on your assessment report"
            )
        
        with col2:
            candidate_email = st.text_input(
                "Email Address (Optional)",
                placeholder="your.email@example.com",
                help="For sending the assessment report"
            )
        
        # Instructions
        st.markdown("### 📋 Before You Begin")
        st.markdown("""
        - **Duration:** Approximately 20-25 minutes
        - **Questions:** Adaptive questioning based on your performance
        - **Topics:** Formulas, functions, data analysis, pivot tables, and more
        - **Approach:** Explain your thinking process clearly
        - **Tip:** There are often multiple correct approaches - share what you know!
        """)
        
        submitted = st.form_submit_button("Start Interview", type="primary")
        
        if submitted:
            if candidate_name.strip():
                # Start the interview
                session_id = interview_agent.start_interview(
                    candidate_name.strip(),
                    candidate_email.strip() if candidate_email.strip() else None
                )
                
                st.session_state.session_id = session_id
                st.session_state.candidate_name = candidate_name.strip()
                st.session_state.candidate_email = candidate_email.strip()
                st.session_state.interview_started = True
                st.session_state.current_phase = "introduction"
                
                st.rerun()
            else:
                st.error("Please enter your name to continue.")

# Helper function to run async code in Streamlit
def run_async(coro):
    """Helper function to run async code properly in Streamlit"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's already a running loop, use asyncio.create_task
            return loop.run_until_complete(coro)
        else:
            return asyncio.run(coro)
    except RuntimeError:
        # If we can't get the event loop, try creating a new one
        try:
            return asyncio.run(coro)
        except RuntimeError:
            # As a last resort, create a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

def handle_interview_interaction():
    """Handle the main interview conversation"""
    
    if not st.session_state.session_id:
        st.error("No active interview session. Please start a new interview.")
        return
    
    # Get welcome message if starting
    if not st.session_state.conversation_history:
        try:
            welcome_message = run_async(interview_agent.get_welcome_message(st.session_state.session_id))
            st.session_state.conversation_history.append(("assistant", welcome_message))
        except Exception as e:
            st.error(f"Error starting interview: {str(e)}")
            return
    
    # Display conversation history
    display_conversation_history()
    
    # Check if interview is completed
    progress = interview_agent.get_interview_progress(st.session_state.session_id)
    if progress.get('is_completed', False):
        display_completion_section()
        return
    
    # Input for user response
    with st.form(key="response_form", clear_on_submit=True):
        user_input = st.text_area(
            "Your Response:",
            placeholder="Type your answer here... Explain your thinking process clearly.",
            height=100,
            help="Be specific and detailed in your explanations. Share your thought process!"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.form_submit_button("Submit Answer", type="primary")
        with col2:
            if st.session_state.current_phase == "assessment":
                st.caption(f"Question {progress.get('questions_answered', 0) + 1} of {settings.MAX_QUESTIONS}")
    
    if submit_button and user_input.strip():
        process_user_response(user_input.strip())

def process_user_response(user_input: str):
    """Process user response and get AI reply"""
    
    # Add user message to history
    st.session_state.conversation_history.append(("user", user_input))
    
    # Show processing indicator
    with st.spinner("Processing your response..."):
        try:
            # Get AI response using the helper function
            ai_response, metadata = run_async(
                interview_agent.process_response(
                    st.session_state.session_id,
                    user_input
                )
            )
            
            # Add AI response to history
            st.session_state.conversation_history.append(("assistant", ai_response))
            
            # Update phase if changed
            if metadata.get('phase'):
                st.session_state.current_phase = metadata['phase']
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing response: {str(e)}")
            st.session_state.conversation_history.append(
                ("assistant", "I apologize for the technical difficulty. Please try again.")
            )

def display_conversation_history():
    """Display the conversation history"""
    
    st.header("💬 Interview Conversation")
    
    for i, (role, message) in enumerate(st.session_state.conversation_history):
        if role == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong> {message}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <strong>Interviewer:</strong> {message}
            </div>
            """, unsafe_allow_html=True)

def extract_scores_from_evaluation(evaluation):
    """Extract and properly format scores from evaluation object"""
    try:
        # Try different ways to access the scores
        if hasattr(evaluation, 'overall_scores'):
            scores = evaluation.overall_scores
            
            # If it's an object with attributes
            if hasattr(scores, 'overall_score'):
                return {
                    'overall_score': float(getattr(scores, 'overall_score', 0)),
                    'technical_score': float(getattr(scores, 'technical_score', 0)),
                    'depth_score': float(getattr(scores, 'depth_score', 0)),
                    'problem_solving_score': float(getattr(scores, 'problem_solving_score', 0)),
                    'communication_score': float(getattr(scores, 'communication_score', 0))
                }
            
            # If it's a dictionary
            elif isinstance(scores, dict):
                return {
                    'overall_score': float(scores.get('overall_score', 0)),
                    'technical_score': float(scores.get('technical_score', 0)),
                    'depth_score': float(scores.get('depth_score', 0)),
                    'problem_solving_score': float(scores.get('problem_solving_score', 0)),
                    'communication_score': float(scores.get('communication_score', 0))
                }
            
            # If it has a to_dict method
            elif hasattr(scores, 'to_dict'):
                scores_dict = scores.to_dict()
                return {
                    'overall_score': float(scores_dict.get('overall_score', 0)),
                    'technical_score': float(scores_dict.get('technical_score', 0)),
                    'depth_score': float(scores_dict.get('depth_score', 0)),
                    'problem_solving_score': float(scores_dict.get('problem_solving_score', 0)),
                    'communication_score': float(scores_dict.get('communication_score', 0))
                }
        
        # If none of the above work, try to access evaluation directly as dict
        elif isinstance(evaluation, dict):
            overall_scores = evaluation.get('overall_scores', {})
            return {
                'overall_score': float(overall_scores.get('overall_score', 0)),
                'technical_score': float(overall_scores.get('technical_score', 0)),
                'depth_score': float(overall_scores.get('depth_score', 0)),
                'problem_solving_score': float(overall_scores.get('problem_solving_score', 0)),
                'communication_score': float(overall_scores.get('communication_score', 0))
            }
        
        # Fallback - return zeros
        return {
            'overall_score': 0.0,
            'technical_score': 0.0,
            'depth_score': 0.0,
            'problem_solving_score': 0.0,
            'communication_score': 0.0
        }
        
    except Exception as e:
        print(f"Error extracting scores: {e}")
        # Return default scores
        return {
            'overall_score': 0.0,
            'technical_score': 0.0,
            'depth_score': 0.0,
            'problem_solving_score': 0.0,
            'communication_score': 0.0
        }

def get_safe_attribute(obj, attr_name, default=None):
    """Safely get attribute from object"""
    try:
        if hasattr(obj, attr_name):
            value = getattr(obj, attr_name, default)
            if callable(value):
                return value()
            return value
        elif isinstance(obj, dict):
            return obj.get(attr_name, default)
        else:
            return default
    except Exception:
        return default

def display_completion_section():
    """Display completion section with results and report options"""
    
    st.header("🎉 Interview Completed!")
    
    # Get final evaluation
    progress = interview_agent.get_interview_progress(st.session_state.session_id)
    interview_state = interview_agent.get_interview_state(st.session_state.session_id)
    
    if interview_state:
        # Check if evaluation is already complete
        if not st.session_state.evaluation_complete:
            try:
                # Generate evaluation (this might take a moment)
                with st.spinner("Generating your detailed assessment..."):
                    evaluation = run_async(evaluator.evaluate_interview(interview_state))
                    st.session_state.final_evaluation = evaluation
                    st.session_state.evaluation_complete = True
                
            except Exception as e:
                st.error(f"Error generating final evaluation: {str(e)}")
                st.markdown("The interview has been completed, but we're having trouble generating the detailed report.")
                return
        
        # Use cached evaluation if available
        evaluation = st.session_state.final_evaluation
        
        if evaluation:
            # Display results
            display_results_summary(evaluation, progress)
            
            # Report generation options
            display_report_options(evaluation, interview_state, progress)
        else:
            st.error("Unable to generate evaluation. Please try refreshing the page.")

def display_results_summary(evaluation, progress):
    """Display results summary"""
    
    st.markdown("### 📊 Your Performance Summary")
    
    # Extract scores properly
    scores = extract_scores_from_evaluation(evaluation)
    
    # Overall score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="score-display">{scores['overall_score']:.1f}/100</div>
            <div>Overall Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        skill_level = get_safe_attribute(evaluation, 'skill_level', 'Novice')
        if hasattr(skill_level, 'value'):
            skill_level = skill_level.value
        skill_level_display = str(skill_level).title() if skill_level else 'Novice'
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="score-display">{skill_level_display}</div>
            <div>Skill Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="score-display">{progress.get('questions_answered', 0)}</div>
            <div>Questions Answered</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Score breakdown
    st.markdown("### 📈 Score Breakdown")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Technical Accuracy (40%):** {scores['technical_score']:.1f}/100")
        st.markdown(f"**Depth of Knowledge (25%):** {scores['depth_score']:.1f}/100")
    
    with col2:
        st.markdown(f"**Problem Solving (20%):** {scores['problem_solving_score']:.1f}/100")
        st.markdown(f"**Communication (15%):** {scores['communication_score']:.1f}/100")
    
    # Key insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Key Strengths")
        key_strengths = get_safe_attribute(evaluation, 'key_strengths', [])
        if key_strengths:
            for strength in key_strengths[:4]:  # Top 4
                st.markdown(f"• {strength}")
        else:
            st.markdown("• No specific strengths identified")
    
    with col2:
        st.markdown("### 🎯 Areas for Improvement")
        areas_for_improvement = get_safe_attribute(evaluation, 'areas_for_improvement', [])
        if areas_for_improvement:
            for improvement in areas_for_improvement[:4]:  # Top 4
                st.markdown(f"• {improvement}")
        else:
            st.markdown("• Continue practicing Excel skills")
    
    # Hiring recommendation
    st.markdown("### 🎯 Assessment Summary")
    
    try:
        if hasattr(evaluation, 'get_hiring_recommendation'):
            recommendation = evaluation.get_hiring_recommendation()
        else:
            # Generate recommendation based on overall score
            overall_score = scores['overall_score']
            if overall_score >= 80:
                recommendation = "Strong Hire - Excellent Excel skills demonstrated"
            elif overall_score >= 60:
                recommendation = "Hire - Good Excel skills with minor development areas"
            elif overall_score >= 40:
                recommendation = "Consider with Training - Basic skills present, needs development"
            else:
                recommendation = "No Hire - Insufficient Excel skills for role requirements"
        
        if "Strong Hire" in recommendation:
            st.success(f"**{recommendation}**")
        elif "Hire" in recommendation and "No" not in recommendation:
            st.info(f"**{recommendation}**")
        elif "Consider" in recommendation:
            st.warning(f"**{recommendation}**")
        else:
            st.error(f"**{recommendation}**")
            
    except Exception as e:
        st.error(f"**Assessment Complete** - See detailed scores above")

def display_report_options(evaluation, interview_state, progress):
    """Display report generation options"""
    
    st.markdown("### 📄 Get Your Detailed Report")
    
    # Extract scores properly for report
    scores = extract_scores_from_evaluation(evaluation)
    
    # Get skill level
    skill_level = get_safe_attribute(evaluation, 'skill_level', 'Novice')
    if hasattr(skill_level, 'value'):
        skill_level = skill_level.value
    skill_level_display = str(skill_level).title() if skill_level else 'Novice'
    
    # Get hiring recommendation
    try:
        if hasattr(evaluation, 'get_hiring_recommendation'):
            hiring_recommendation = evaluation.get_hiring_recommendation()
        else:
            overall_score = scores['overall_score']
            if overall_score >= 80:
                hiring_recommendation = "Strong Hire - Excellent Excel skills demonstrated"
            elif overall_score >= 60:
                hiring_recommendation = "Hire - Good Excel skills with minor development areas"
            elif overall_score >= 40:
                hiring_recommendation = "Consider with Training - Basic skills present, needs development"
            else:
                hiring_recommendation = "No Hire - Insufficient Excel skills for role requirements"
    except Exception:
        hiring_recommendation = "Assessment completed - see detailed scores"
    
    # Prepare report data with proper score handling
    report_data = {
        "candidate_info": {
            "name": st.session_state.candidate_name,
            "email": st.session_state.candidate_email
        },
        "scores": scores,  # Use the properly extracted scores
        "skill_level": skill_level_display,
        "hiring_recommendation": hiring_recommendation,
        "key_strengths": get_safe_attribute(evaluation, 'key_strengths', ["Assessment completed"]),
        "improvement_areas": get_safe_attribute(evaluation, 'areas_for_improvement', ["Continue practicing Excel skills"]),
        "development_recommendations": get_safe_attribute(evaluation, 'recommendations', ["Take online courses to learn basic Excel skills"]),
        "consistency_analysis": f"Performance consistency: {get_safe_attribute(evaluation, 'consistency_score', 0):.1f}%",
        "readiness_for_role": get_safe_attribute(evaluation, 'readiness_assessment', "Assessment completed"),
        "overall_impression": f"Demonstrated {skill_level_display} level Excel skills",
        "duration": f"{progress.get('elapsed_time', 0):.1f}",
        "total_questions": progress.get('questions_answered', 0),
        "category_performance": progress.get('category_performance', {})
    }
    
 
    
    # PDF Download Section
    if st.button("📄 Download PDF Report", type="primary"):
        try:
            pdf_bytes = report_generator.generate_pdf_report(report_data)
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"Excel_Assessment_{st.session_state.candidate_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
            st.success("PDF report generated successfully!")
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            # Show detailed error for debugging
            st.exception(e)
    
    # Option to start new interview
    st.markdown("---")
    if st.button("🔄 Start New Interview", type="secondary"):
        reset_interview()

def main():
    """Main application function"""
    
    init_session_state()
    display_header()
    display_sidebar()
    
    # Main content area
    if not st.session_state.interview_started:
        start_interview_form()
    else:
        # Run interview interaction
        handle_interview_interaction()

if __name__ == "__main__":
    main()











