import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock

# Add backend to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.interview_agent import ExcelInterviewAgent
from models.interview_state import InterviewState, InterviewPhase

class TestExcelInterviewAgent:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = ExcelInterviewAgent()
    
    def test_start_interview(self):
        """Test starting a new interview"""
        candidate_name = "John Doe"
        candidate_email = "john@example.com"
        
        session_id = self.agent.start_interview(candidate_name, candidate_email)
        
        assert session_id is not None
        assert session_id in self.agent.active_interviews
        
        interview_state = self.agent.active_interviews[session_id]
        assert interview_state.candidate_name == candidate_name
        assert interview_state.candidate_email == candidate_email
        assert interview_state.current_phase == InterviewPhase.INTRODUCTION
    
    def test_get_interview_progress(self):
        """Test getting interview progress"""
        session_id = self.agent.start_interview("Test User")
        progress = self.agent.get_interview_progress(session_id)
        
        assert progress['candidate_name'] == "Test User"
        assert progress['phase'] == InterviewPhase.INTRODUCTION.value
        assert progress['questions_answered'] == 0
        assert progress['is_completed'] == False
    
    def test_invalid_session(self):
        """Test handling invalid session ID"""
        progress = self.agent.get_interview_progress("invalid_session")
        assert "error" in progress
    
    def test_cleanup_session(self):
        """Test session cleanup"""
        session_id = self.agent.start_interview("Test User")
        assert session_id in self.agent.active_interviews
        
        self.agent.cleanup_session(session_id)
        assert session_id not in self.agent.active_interviews

@pytest.mark.asyncio
class TestAsyncInterviewAgent:
    
    def setup_method(self):
        """Setup async test fixtures"""
        self.agent = ExcelInterviewAgent()
    
    async def test_get_welcome_message(self):
        """Test welcome message generation"""
        session_id = self.agent.start_interview("Test User")
        
        # Mock the LLM client to avoid actual API calls
        with pytest.mock.patch('core.interview_agent.llm_client') as mock_llm:
            mock_llm.generate_response = AsyncMock(return_value="Welcome to the Excel assessment!")
            
            welcome_message = await self.agent.get_welcome_message(session_id)
            
            assert "Welcome" in welcome_message
            mock_llm.generate_response.assert_called_once()
    
    async def test_invalid_session_welcome(self):
        """Test welcome message with invalid session"""
        welcome_message = await self.agent.get_welcome_message("invalid")
        assert "couldn't find your interview session" in welcome_message

if __name__ == "__main__":
    pytest.main([__file__])