import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging

from models.interview_state import InterviewState, InterviewPhase, QuestionDifficulty, QuestionResponse
from models.evaluation_models import InterviewEvaluation
from core.question_bank import question_bank
from core.evaluator import evaluator
from utils.llm_client import llm_client
from config.settings import settings

class ExcelInterviewAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_interviews: Dict[str, InterviewState] = {}
    
    def start_interview(
        self, 
        candidate_name: str, 
        candidate_email: Optional[str] = None
    ) -> str:
        """Start a new interview session"""
        
        session_id = str(uuid.uuid4())
        
        interview_state = InterviewState(
            session_id=session_id,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            current_phase=InterviewPhase.INTRODUCTION,
            start_time=datetime.now()
        )
        
        self.active_interviews[session_id] = interview_state
        
        # Log interview start
        self.logger.info(f"Started interview for {candidate_name}, session: {session_id}")
        
        return session_id
    
    async def get_welcome_message(self, session_id: str) -> str:
        """Generate personalized welcome message"""
        
        interview_state = self.active_interviews.get(session_id)
        if not interview_state:
            return "I'm sorry, but I couldn't find your interview session. Please restart the interview."
        
        welcome_prompt = f"""
You are an expert Excel interviewer conducting a technical assessment. Generate a warm, professional welcome message for {interview_state.candidate_name}.

The message should:
1. Welcome them warmly and professionally
2. Explain that this is an AI-powered Excel skills assessment
3. Outline the interview structure (introduction, assessment, conclusion)
4. Mention the duration will be approximately 20-25 minutes
5. Encourage them to explain their thinking process
6. Ask about their experience level with Excel

Keep it conversational and encouraging.
"""
        
        welcome_message = await llm_client.generate_response(welcome_prompt)
        
        # Add to conversation history
        interview_state.add_conversation("assistant", welcome_message)
        
        return welcome_message
    
    async def process_response(
        self, 
        session_id: str, 
        user_response: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Process user response and generate next interaction"""
        
        interview_state = self.active_interviews.get(session_id)
        if not interview_state:
            return "Session not found. Please restart the interview.", {}
        
        # Add user response to conversation history
        interview_state.add_conversation("user", user_response)
        
        # Process based on current phase
        if interview_state.current_phase == InterviewPhase.INTRODUCTION:
            return await self._handle_introduction_phase(interview_state, user_response)
        elif interview_state.current_phase == InterviewPhase.ASSESSMENT:
            return await self._handle_assessment_phase(interview_state, user_response)
        elif interview_state.current_phase == InterviewPhase.CONCLUSION:
            return await self._handle_conclusion_phase(interview_state, user_response)
        else:
            return "Interview completed. Thank you for your time!", {"phase": "completed"}
    
    async def _handle_introduction_phase(
        self, 
        interview_state: InterviewState, 
        response: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle introduction phase interactions"""
        
        # Extract experience level from response
        experience_level = await self._extract_experience_level(response)
        interview_state.experience_level = experience_level
        
        # Set initial difficulty based on experience
        if "beginner" in experience_level.lower() or "new" in experience_level.lower():
            interview_state.current_difficulty = QuestionDifficulty.BASIC
        elif "advanced" in experience_level.lower() or "expert" in experience_level.lower():
            interview_state.current_difficulty = QuestionDifficulty.INTERMEDIATE
        else:
            interview_state.current_difficulty = QuestionDifficulty.BASIC
        
        # Transition to assessment
        interview_state.current_phase = InterviewPhase.ASSESSMENT
        
        # Generate first question
        first_question = question_bank.get_question(interview_state.current_difficulty)
        
        if not first_question:
            return "I apologize, but there was an issue loading questions. Please try again.", {}
        
        transition_message = await self._generate_transition_message(interview_state, first_question)
        
        interview_state.add_conversation("assistant", transition_message)
        
        return transition_message, {
            "phase": "assessment",
            "question_number": 1,
            "current_difficulty": interview_state.current_difficulty.value,
            "experience_level": experience_level
        }
    
    async def _handle_assessment_phase(
        self, 
        interview_state: InterviewState, 
        response: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle assessment phase interactions"""
        
        # Get the last question asked (should be stored in conversation)
        current_question = self._get_current_question_from_conversation(interview_state)
        
        if not current_question:
            return await self._generate_next_question_flow(interview_state)
        
        # Evaluate the response
        try:
            evaluation = await evaluator.evaluate_answer(
                question=current_question["question"],
                answer=response,
                category=current_question.get("category", "General"),
                difficulty=interview_state.current_difficulty.value,
                expected_points=current_question.get("expected_points", [])
            )
            
            # Store the response
            question_response = QuestionResponse(
                question_id=current_question.get("id", "unknown"),
                question=current_question["question"],
                answer=response,
                score=evaluation.scores.overall_score,
                feedback=evaluation.feedback,
                category=current_question.get("category", "General"),
                difficulty=interview_state.current_difficulty
            )
            
            interview_state.add_response(question_response)
            
            # Provide immediate feedback
            feedback_message = evaluator.get_real_time_feedback(
                evaluation.scores.overall_score,
                current_question.get("category", "Excel")
            )
            
            # Check if interview should continue
            if len(interview_state.questions_asked) >= settings.MAX_QUESTIONS:
                interview_state.current_phase = InterviewPhase.CONCLUSION
                conclusion_message = await self._generate_conclusion_message(interview_state)
                return conclusion_message, {"phase": "conclusion"}
            
            # Adjust difficulty if needed
            if interview_state.should_increase_difficulty():
                if interview_state.current_difficulty == QuestionDifficulty.BASIC:
                    interview_state.current_difficulty = QuestionDifficulty.INTERMEDIATE
                elif interview_state.current_difficulty == QuestionDifficulty.INTERMEDIATE:
                    interview_state.current_difficulty = QuestionDifficulty.ADVANCED
            elif interview_state.should_decrease_difficulty():
                if interview_state.current_difficulty == QuestionDifficulty.ADVANCED:
                    interview_state.current_difficulty = QuestionDifficulty.INTERMEDIATE
                elif interview_state.current_difficulty == QuestionDifficulty.INTERMEDIATE:
                    interview_state.current_difficulty = QuestionDifficulty.BASIC
            
            # Generate next question
            next_response, metadata = await self._generate_next_question_flow(interview_state)
            
            # Combine feedback with next question
            combined_response = f"{feedback_message}\n\n{next_response}"
            
            return combined_response, metadata
            
        except Exception as e:
            self.logger.error(f"Error in assessment phase: {str(e)}")
            return "Thank you for your response. Let me ask you another question.", {}
    
    async def _handle_conclusion_phase(
        self, 
        interview_state: InterviewState, 
        response: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle conclusion phase interactions"""
        
        # Generate final evaluation
        try:
            interview_evaluation = await evaluator.evaluate_interview(interview_state)
            
            # Create summary message
            summary_message = await self._generate_interview_summary(interview_state, interview_evaluation)
            
            # Mark interview as completed
            interview_state.is_completed = True
            interview_state.end_time = datetime.now()
            interview_state.current_phase = InterviewPhase.COMPLETED
            
            return summary_message, {
                "phase": "completed",
                "evaluation": {
                    "overall_score": interview_evaluation.overall_scores.overall_score,
                    "skill_level": interview_evaluation.skill_level.value,
                    "key_strengths": interview_evaluation.key_strengths,
                    "improvement_areas": interview_evaluation.areas_for_improvement,
                    "recommendations": interview_evaluation.recommendations
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in conclusion phase: {str(e)}")
            return "Thank you for completing the interview. Your performance will be evaluated and a report will be generated.", {"phase": "completed"}
    
    async def _extract_experience_level(self, response: str) -> str:
        """Extract experience level from candidate response"""
        
        extraction_prompt = f"""
Analyze this response and determine the candidate's Excel experience level: "{response}"

Classify as one of:
- Beginner: Little to no Excel experience
- Intermediate: Regular Excel user with good basic skills
- Advanced: Strong Excel user with complex function knowledge
- Expert: Excel power user with VBA/advanced features

Respond with just the classification and a brief justification.
"""
        
        try:
            result = await llm_client.generate_response(extraction_prompt)
            return result.split('\n')[0].strip()  # Take first line
        except:
            return "Intermediate"  # Default fallback
    
    def _get_current_question_from_conversation(self, interview_state: InterviewState) -> Optional[Dict[str, Any]]:
        """Extract current question from conversation history"""
        
        # This is a simplified implementation
        # In a real system, you'd store question context more explicitly
        conversation = interview_state.conversation_history
        
        # Look for the last assistant message that contains a question
        for entry in reversed(conversation):
            if entry["role"] == "assistant" and "?" in entry["message"]:
                # Parse question from message (simplified)
                question_text = entry["message"].split("?")[0] + "?"
                return {
                    "id": f"q_{len(interview_state.questions_asked)}",
                    "question": question_text,
                    "category": "General Excel",
                    "expected_points": []
                }
        
        return None
    
    async def _generate_transition_message(
        self, 
        interview_state: InterviewState, 
        first_question: Dict[str, Any]
    ) -> str:
        """Generate transition message from introduction to assessment"""
        
        transition_prompt = f"""
Generate a smooth transition message from introduction to the assessment phase. 
The candidate has indicated their experience level as: {interview_state.experience_level}

The message should:
1. Acknowledge their experience level
2. Explain that we'll start with questions appropriate to their level
3. Mention that difficulty will adapt based on their responses
4. Present the first question naturally

First question: {first_question['question']}
Category: {first_question['category']}

Make it conversational and encouraging.
"""
        
        return await llm_client.generate_response(transition_prompt)
    
    async def _generate_next_question_flow(self, interview_state: InterviewState) -> Tuple[str, Dict[str, Any]]:
        """Generate the next question in the interview flow"""
        
        # Get performance summary
        current_performance = interview_state.get_current_score()
        answered_categories = [q.category for q in interview_state.questions_asked]
        
        # Get adaptive question
        next_question = question_bank.get_adaptive_question(
            current_performance=current_performance,
            current_difficulty=interview_state.current_difficulty,
            answered_categories=answered_categories
        )
        
        if not next_question:
            # Fallback to conclusion if no more questions
            interview_state.current_phase = InterviewPhase.CONCLUSION
            return await self._generate_conclusion_message(interview_state)
        
        # Generate contextual question presentation
        question_prompt = f"""
Present this Excel question in a natural, conversational way:

Question: {next_question['question']}
Category: {next_question['category']}
Difficulty: {interview_state.current_difficulty.value}

Consider:
- This is question #{len(interview_state.questions_asked) + 1}
- Current performance level: {current_performance:.1f}%
- Previous categories covered: {', '.join(answered_categories) if answered_categories else 'None yet'}

Make it engaging and clear.
"""
        
        question_message = await llm_client.generate_response(question_prompt)
        interview_state.add_conversation("assistant", question_message)
        
        return question_message, {
            "phase": "assessment",
            "question_number": len(interview_state.questions_asked) + 1,
            "current_difficulty": interview_state.current_difficulty.value,
            "category": next_question['category'],
            "current_score": current_performance
        }
    
    async def _generate_conclusion_message(self, interview_state: InterviewState) -> str:
        """Generate conclusion message"""
        
        conclusion_prompt = f"""
Generate a conclusion message for the Excel interview. 

Interview summary:
- Questions answered: {len(interview_state.questions_asked)}
- Current average score: {interview_state.get_current_score():.1f}%
- Categories covered: {', '.join(set(q.category for q in interview_state.questions_asked))}

The message should:
1. Thank them for their time
2. Mention the assessment is complete
3. Indicate that detailed feedback will be provided
4. Be encouraging and professional

Keep it brief but warm.
"""
        
        conclusion_message = await llm_client.generate_response(conclusion_prompt)
        interview_state.add_conversation("assistant", conclusion_message)
        
        return conclusion_message
    
    async def _generate_interview_summary(
        self, 
        interview_state: InterviewState, 
        evaluation: InterviewEvaluation
    ) -> str:
        """Generate final interview summary message"""
        
        summary_prompt = f"""
Generate a final summary message for the candidate based on their Excel interview performance.

Performance Summary:
- Overall Score: {evaluation.overall_scores.overall_score:.1f}/100
- Skill Level: {evaluation.skill_level.value}
- Key Strengths: {', '.join(evaluation.key_strengths[:3])}  # Top 3
- Main Areas for Improvement: {', '.join(evaluation.areas_for_improvement[:2])}  # Top 2

The message should:
1. Congratulate them on completing the assessment
2. Provide encouraging highlights of their performance
3. Mention their skill level determination
4. Give 1-2 specific areas for growth
5. End on a positive, motivating note

Be professional, encouraging, and specific. Avoid being overly critical.
"""
        
        return await llm_client.generate_response(summary_prompt)
    
    def get_interview_state(self, session_id: str) -> Optional[InterviewState]:
        """Get current interview state"""
        return self.active_interviews.get(session_id)
    
    def get_interview_progress(self, session_id: str) -> Dict[str, Any]:
        """Get interview progress information"""
        
        interview_state = self.active_interviews.get(session_id)
        if not interview_state:
            return {"error": "Session not found"}
        
        progress = {
            "session_id": session_id,
            "candidate_name": interview_state.candidate_name,
            "phase": interview_state.current_phase.value,
            "questions_answered": len(interview_state.questions_asked),
            "current_score": interview_state.get_current_score(),
            "difficulty_level": interview_state.current_difficulty.value,
            "elapsed_time": (datetime.now() - interview_state.start_time).total_seconds() / 60,  # minutes
            "is_completed": interview_state.is_completed
        }
        
        if interview_state.questions_asked:
            progress["category_performance"] = interview_state.get_category_performance()
        
        return progress
    
    def cleanup_session(self, session_id: str):
        """Clean up completed interview session"""
        if session_id in self.active_interviews:
            del self.active_interviews[session_id]
            self.logger.info(f"Cleaned up interview session: {session_id}")

# Global instance
interview_agent = ExcelInterviewAgent()