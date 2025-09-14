import pytest
import sys
import os
from unittest.mock import AsyncMock

# Add backend to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.evaluator import ExcelAnswerEvaluator
from models.evaluation_models import SkillLevel, ScoreBreakdown

class TestExcelAnswerEvaluator:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.evaluator = ExcelAnswerEvaluator()
    
    def test_determine_skill_level(self):
        """Test skill level determination"""
        assert self.evaluator._determine_skill_level(95) == SkillLevel.EXPERT
        assert self.evaluator._determine_skill_level(80) == SkillLevel.ADVANCED
        assert self.evaluator._determine_skill_level(65) == SkillLevel.INTERMEDIATE
        assert self.evaluator._determine_skill_level(45) == SkillLevel.BASIC
        assert self.evaluator._determine_skill_level(25) == SkillLevel.NOVICE
    
    def test_calculate_consistency_score(self):
        """Test consistency score calculation"""
        # Mock evaluations with consistent scores
        from models.evaluation_models import QuestionEvaluation, ScoreBreakdown
        
        consistent_evaluations = [
            QuestionEvaluation(
                question_id="q1",
                answer="answer1", 
                scores=ScoreBreakdown(80, 80, 80, 80, 80),
                feedback="Good",
                strengths=[],
                improvements=[],
                follow_up_suggestions=[]
            ),
            QuestionEvaluation(
                question_id="q2",
                answer="answer2",
                scores=ScoreBreakdown(82, 82, 82, 82, 82), 
                feedback="Good",
                strengths=[],
                improvements=[],
                follow_up_suggestions=[]
            )
        ]
        
        consistency = self.evaluator._calculate_consistency_score(consistent_evaluations)
        assert consistency >= 90  # High consistency
        
        # Test with inconsistent scores
        inconsistent_evaluations = [
            QuestionEvaluation(
                question_id="q1",
                answer="answer1",
                scores=ScoreBreakdown(90, 90, 90, 90, 90),
                feedback="Excellent", 
                strengths=[],
                improvements=[],
                follow_up_suggestions=[]
            ),
            QuestionEvaluation(
                question_id="q2", 
                answer="answer2",
                scores=ScoreBreakdown(40, 40, 40, 40, 40),
                feedback="Poor",
                strengths=[],
                improvements=[], 
                follow_up_suggestions=[]
            )
        ]
        
        consistency = self.evaluator._calculate_consistency_score(inconsistent_evaluations)
        assert consistency < 50  # Low consistency
    
    def test_analyze_improvement_trend(self):
        """Test improvement trend analysis"""
        from models.evaluation_models import QuestionEvaluation, ScoreBreakdown
        
        # Improving trend
        improving_evaluations = [
            QuestionEvaluation("q1", "a1", ScoreBreakdown(60, 60, 60, 60, 60), "", [], [], []),
            QuestionEvaluation("q2", "a2", ScoreBreakdown(70, 70, 70, 70, 70), "", [], [], []),
            QuestionEvaluation("q3", "a3", ScoreBreakdown(80, 80, 80, 80, 80), "", [], [], [])
        ]
        
        trend = self.evaluator._analyze_improvement_trend(improving_evaluations)
        assert trend == "improving"
        
        # Stable trend  
        stable_evaluations = [
            QuestionEvaluation("q1", "a1", ScoreBreakdown(70, 70, 70, 70, 70), "", [], [], []),
            QuestionEvaluation("q2", "a2", ScoreBreakdown(72, 72, 72, 72, 72), "", [], [], []),
            QuestionEvaluation("q3", "a3", ScoreBreakdown(71, 71, 71, 71, 71), "", [], [], [])
        ]
        
        trend = self.evaluator._analyze_improvement_trend(stable_evaluations)
        assert trend == "stable"
    
    def test_get_real_time_feedback(self):
        """Test real-time feedback generation"""
        excellent_feedback = self.evaluator.get_real_time_feedback(90, "Formulas")
        assert "Excellent" in excellent_feedback
        
        poor_feedback = self.evaluator.get_real_time_feedback(30, "Charts")
        assert "needs work" in poor_feedback.lower()
    
    def test_assess_role_readiness(self):
        """Test role readiness assessment"""
        senior_ready = self.evaluator._assess_role_readiness(90)
        assert "senior-level" in senior_ready.lower()
        
        not_ready = self.evaluator._assess_role_readiness(30)
        assert "not ready" in not_ready.lower()

@pytest.mark.asyncio 
class TestAsyncEvaluator:
    
    def setup_method(self):
        """Setup async test fixtures"""
        self.evaluator = ExcelAnswerEvaluator()
    
    async def test_evaluate_answer(self):
        """Test answer evaluation with mocked LLM"""
        with pytest.mock.patch('core.evaluator.llm_client') as mock_llm:
            mock_llm.evaluate_answer = AsyncMock(return_value={
                'technical_score': 85,
                'depth_score': 80,
                'problem_solving_score': 75,
                'communication_score': 85,
                'feedback': 'Good answer with solid understanding',
                'strengths': ['Clear explanation', 'Correct approach'],
                'improvements': ['Could add more detail'],
                'follow_up_questions': ['How would you optimize this?']
            })
            
            evaluation = await self.evaluator.evaluate_answer(
                question="How do you create a SUM formula?",
                answer="I would use =SUM(A1:A10) to add up the range",
                category="Formulas",
                difficulty="basic"
            )
            
            assert evaluation.scores.technical_score == 85
            assert "Good answer" in evaluation.feedback
            assert len(evaluation.strengths) == 2

if __name__ == "__main__":
    pytest.main([__file__])