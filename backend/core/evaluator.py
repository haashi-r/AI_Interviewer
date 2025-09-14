import asyncio
from typing import Dict, Any, List, Optional
import logging
from models.evaluation_models import (
    ScoreBreakdown, QuestionEvaluation, InterviewEvaluation,
    SkillLevel, FeedbackTemplate
)
from models.interview_state import QuestionResponse, InterviewState
from utils.llm_client import llm_client
from config.settings import settings

class ExcelAnswerEvaluator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.feedback_template = FeedbackTemplate()
    
    async def evaluate_answer(
        self, 
        question: str, 
        answer: str, 
        category: str,
        difficulty: str,
        expected_points: List[str] = None
    ) -> QuestionEvaluation:
        """Evaluate a single answer comprehensively"""
        
        try:
            # Get LLM evaluation
            evaluation_data = await llm_client.evaluate_answer(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty
            )
            
            # Parse scores
            technical_score = evaluation_data.get('technical_score', 0)
            depth_score = evaluation_data.get('depth_score', 0)
            problem_solving_score = evaluation_data.get('problem_solving_score', 0)
            communication_score = evaluation_data.get('communication_score', 0)
            
            # Calculate weighted overall score
            overall_score = (
                technical_score * settings.TECHNICAL_WEIGHT +
                depth_score * settings.DEPTH_WEIGHT +
                problem_solving_score * settings.PROBLEM_SOLVING_WEIGHT +
                communication_score * settings.COMMUNICATION_WEIGHT
            )
            
            scores = ScoreBreakdown(
                technical_score=technical_score,
                depth_score=depth_score,
                problem_solving_score=problem_solving_score,
                communication_score=communication_score,
                overall_score=overall_score
            )
            
            # Extract feedback components
            feedback = evaluation_data.get('feedback', 'No detailed feedback available')
            strengths = evaluation_data.get('strengths', [])
            improvements = evaluation_data.get('improvements', [])
            follow_up_suggestions = evaluation_data.get('follow_up_questions', [])
            
            return QuestionEvaluation(
                question_id=f"{category}_{difficulty}_{hash(question) % 1000}",
                answer=answer,
                scores=scores,
                feedback=feedback,
                strengths=strengths,
                improvements=improvements,
                follow_up_suggestions=follow_up_suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating answer: {str(e)}")
            
            # Fallback evaluation
            return self._create_fallback_evaluation(question, answer, category)
    
    def _create_fallback_evaluation(
        self, 
        question: str, 
        answer: str, 
        category: str
    ) -> QuestionEvaluation:
        """Create a basic evaluation when LLM fails"""
        
        # Simple heuristic evaluation
        answer_length = len(answer.strip())
        technical_score = min(70, answer_length * 2)  # Basic length-based scoring
        
        scores = ScoreBreakdown(
            technical_score=technical_score,
            depth_score=technical_score * 0.9,
            problem_solving_score=technical_score * 0.8,
            communication_score=technical_score * 0.85,
            overall_score=technical_score * 0.88
        )
        
        return QuestionEvaluation(
            question_id=f"fallback_{hash(question) % 1000}",
            answer=answer,
            scores=scores,
            feedback="Evaluation completed with basic analysis due to system limitations.",
            strengths=["Provided a response"],
            improvements=["Could provide more detailed explanation"],
            follow_up_suggestions=[]
        )
    
    async def evaluate_interview(
        self, 
        interview_state: InterviewState
    ) -> InterviewEvaluation:
        """Evaluate the complete interview performance"""
        
        try:
            # Calculate overall scores
            question_evaluations = []
            
            for response in interview_state.questions_asked:
                evaluation = await self.evaluate_answer(
                    question=response.question,
                    answer=response.answer,
                    category=response.category,
                    difficulty=response.difficulty.value
                )
                question_evaluations.append(evaluation)
            
            if not question_evaluations:
                return self._create_minimal_evaluation()
            
            # Calculate aggregate scores
            overall_scores = self._calculate_aggregate_scores(question_evaluations)
            
            # Determine skill level
            skill_level = self._determine_skill_level(overall_scores.overall_score)
            
            # Calculate category performance
            category_performance = self._calculate_category_performance(question_evaluations)
            
            # Generate summary insights
            summary_data = {
                "questions": len(question_evaluations),
                "scores": overall_scores.to_dict(),
                "categories": category_performance,
                "responses": [
                    {
                        "question": eval.answer,
                        "score": eval.scores.overall_score,
                        "category": "general"  # Simplified for summary
                    }
                    for eval in question_evaluations
                ]
            }
            
            summary = await llm_client.generate_interview_summary(summary_data)
            
            # Extract insights from summary
            key_strengths = summary.get('key_strengths', ['Completed the interview'])
            areas_for_improvement = summary.get('improvement_areas', ['Continue practicing Excel skills'])
            recommendations = summary.get('development_recommendations', ['Regular Excel practice recommended'])
            
            # Calculate additional metrics
            consistency_score = self._calculate_consistency_score(question_evaluations)
            improvement_trend = self._analyze_improvement_trend(question_evaluations)
            readiness_assessment = self._assess_role_readiness(overall_scores.overall_score)
            
            return InterviewEvaluation(
                overall_scores=overall_scores,
                skill_level=skill_level,
                category_performance=category_performance,
                question_evaluations=question_evaluations,
                key_strengths=key_strengths,
                areas_for_improvement=areas_for_improvement,
                recommendations=recommendations,
                consistency_score=consistency_score,
                improvement_trend=improvement_trend,
                readiness_assessment=readiness_assessment
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating interview: {str(e)}")
            return self._create_minimal_evaluation()
    
    def _calculate_aggregate_scores(self, evaluations: List[QuestionEvaluation]) -> ScoreBreakdown:
        """Calculate aggregate scores from all question evaluations"""
        
        if not evaluations:
            return ScoreBreakdown(0, 0, 0, 0, 0)
        
        technical_total = sum(eval.scores.technical_score for eval in evaluations)
        depth_total = sum(eval.scores.depth_score for eval in evaluations)
        problem_solving_total = sum(eval.scores.problem_solving_score for eval in evaluations)
        communication_total = sum(eval.scores.communication_score for eval in evaluations)
        
        count = len(evaluations)
        
        technical_avg = technical_total / count
        depth_avg = depth_total / count
        problem_solving_avg = problem_solving_total / count
        communication_avg = communication_total / count
        
        overall_avg = (
            technical_avg * settings.TECHNICAL_WEIGHT +
            depth_avg * settings.DEPTH_WEIGHT +
            problem_solving_avg * settings.PROBLEM_SOLVING_WEIGHT +
            communication_avg * settings.COMMUNICATION_WEIGHT
        )
        
        return ScoreBreakdown(
            technical_score=technical_avg,
            depth_score=depth_avg,
            problem_solving_score=problem_solving_avg,
            communication_score=communication_avg,
            overall_score=overall_avg
        )
    
    def _determine_skill_level(self, overall_score: float) -> SkillLevel:
        """Determine skill level based on overall score"""
        
        if overall_score >= 90:
            return SkillLevel.EXPERT
        elif overall_score >= 75:
            return SkillLevel.ADVANCED
        elif overall_score >= 60:
            return SkillLevel.INTERMEDIATE
        elif overall_score >= 40:
            return SkillLevel.BASIC
        else:
            return SkillLevel.NOVICE
    
    def _calculate_category_performance(self, evaluations: List[QuestionEvaluation]) -> Dict[str, float]:
        """Calculate performance by category"""
        
        category_scores = {}
        category_counts = {}
        
        for evaluation in evaluations:
            # Extract category from question context or use generic
            category = "Excel Skills"  # Simplified for now
            
            if category not in category_scores:
                category_scores[category] = 0
                category_counts[category] = 0
            
            category_scores[category] += evaluation.scores.overall_score
            category_counts[category] += 1
        
        return {
            category: category_scores[category] / category_counts[category]
            for category in category_scores
        }
    
    def _calculate_consistency_score(self, evaluations: List[QuestionEvaluation]) -> float:
        """Calculate consistency of performance across questions"""
        
        if len(evaluations) < 2:
            return 100.0  # Perfect consistency with single question
        
        scores = [eval.scores.overall_score for eval in evaluations]
        mean_score = sum(scores) / len(scores)
        
        # Calculate standard deviation
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Convert to consistency score (lower std_dev = higher consistency)
        # Scale so that std_dev of 0 = 100, std_dev of 25+ = 0
        consistency = max(0, 100 - (std_dev * 4))
        
        return consistency
    
    def _analyze_improvement_trend(self, evaluations: List[QuestionEvaluation]) -> str:
        """Analyze if performance is improving, declining, or stable"""
        
        if len(evaluations) < 3:
            return "stable"
        
        scores = [eval.scores.overall_score for eval in evaluations]
        
        # Compare first third with last third
        first_third = scores[:len(scores)//3]
        last_third = scores[-len(scores)//3:]
        
        first_avg = sum(first_third) / len(first_third)
        last_avg = sum(last_third) / len(last_third)
        
        improvement = last_avg - first_avg
        
        if improvement > 5:
            return "improving"
        elif improvement < -5:
            return "declining"
        else:
            return "stable"
    
    def _assess_role_readiness(self, overall_score: float) -> str:
        """Assess readiness for role based on score"""
        
        if overall_score >= 85:
            return "Ready for senior-level Excel roles with minimal training"
        elif overall_score >= 70:
            return "Ready for intermediate roles, some advanced training beneficial"
        elif overall_score >= 55:
            return "Ready for entry-level roles with structured training program"
        elif overall_score >= 40:
            return "Requires significant training before role placement"
        else:
            return "Not ready for Excel-dependent roles, comprehensive training needed"
    
    def _create_minimal_evaluation(self) -> InterviewEvaluation:
        """Create a minimal evaluation when full evaluation fails"""
        
        minimal_scores = ScoreBreakdown(
            technical_score=50.0,
            depth_score=50.0,
            problem_solving_score=50.0,
            communication_score=50.0,
            overall_score=50.0
        )
        
        return InterviewEvaluation(
            overall_scores=minimal_scores,
            skill_level=SkillLevel.BASIC,
            category_performance={"Excel Skills": 50.0},
            question_evaluations=[],
            key_strengths=["Participated in the interview"],
            areas_for_improvement=["All areas need development"],
            recommendations=["Complete Excel training program"],
            consistency_score=50.0,
            improvement_trend="stable",
            readiness_assessment="Requires training before role placement"
        )
    
    def get_real_time_feedback(self, score: float, category: str) -> str:
        """Generate real-time feedback during interview"""
        
        if score >= 85:
            return f"Excellent answer! You demonstrate strong {category} skills."
        elif score >= 70:
            return f"Good response. Your {category} knowledge is solid."
        elif score >= 55:
            return f"Decent answer. Some areas in {category} could be strengthened."
        elif score >= 40:
            return f"Basic understanding shown. {category} skills need development."
        else:
            return f"This area needs work. Consider reviewing {category} concepts."
    
    def suggest_follow_up_question(self, performance: float, category: str) -> Optional[str]:
        """Suggest follow-up questions based on performance"""
        
        follow_ups = {
            "Formulas & Functions": [
                "Can you explain the difference between relative and absolute references?",
                "How would you handle errors in your formulas?",
                "What are some common Excel functions you use regularly?"
            ],
            "Data Analysis": [
                "How do you validate your analysis results?",
                "What visualization would best represent this data?",
                "How would you automate this analysis process?"
            ],
            "Pivot Tables": [
                "How would you handle missing data in a pivot table?",
                "Can you explain pivot table refresh vs. rebuild?",
                "What are some advanced pivot table features you've used?"
            ]
        }
        
        if category in follow_ups and performance > 60:
            import random
            return random.choice(follow_ups[category])
        
        return None

# Global instance
evaluator = ExcelAnswerEvaluator()