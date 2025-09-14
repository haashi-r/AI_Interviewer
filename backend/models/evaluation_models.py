from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class SkillLevel(Enum):
    NOVICE = "novice"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class EvaluationCriteria:
    technical_accuracy: str
    depth_of_knowledge: str
    problem_solving_approach: str
    communication_clarity: str

@dataclass
class ScoreBreakdown:
    technical_score: float
    depth_score: float
    problem_solving_score: float
    communication_score: float
    overall_score: float
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "technical": self.technical_score,
            "depth": self.depth_score,
            "problem_solving": self.problem_solving_score,
            "communication": self.communication_score,
            "overall": self.overall_score
        }

@dataclass
class QuestionEvaluation:
    question_id: str
    answer: str
    scores: ScoreBreakdown
    feedback: str
    strengths: List[str]
    improvements: List[str]
    follow_up_suggestions: List[str]

@dataclass
class InterviewEvaluation:
    overall_scores: ScoreBreakdown
    skill_level: SkillLevel
    category_performance: Dict[str, float]
    question_evaluations: List[QuestionEvaluation]
    
    # Summary
    key_strengths: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]
    
    # Detailed Analysis
    consistency_score: float
    improvement_trend: str  # "improving", "declining", "stable"
    readiness_assessment: str
    
    def get_skill_level_description(self) -> str:
        """Get description for the determined skill level"""
        descriptions = {
            SkillLevel.NOVICE: "New to Excel with basic understanding",
            SkillLevel.BASIC: "Foundational Excel skills, can handle simple tasks",
            SkillLevel.INTERMEDIATE: "Competent Excel user with good practical skills",
            SkillLevel.ADVANCED: "Strong Excel skills suitable for professional roles",
            SkillLevel.EXPERT: "Expert-level Excel proficiency with advanced capabilities"
        }
        return descriptions.get(self.skill_level, "Unknown skill level")
    
    def get_hiring_recommendation(self) -> str:
        """Get hiring recommendation based on overall performance"""
        if self.overall_scores.overall_score >= 85:
            return "Strong Hire - Excellent Excel skills"
        elif self.overall_scores.overall_score >= 70:
            return "Hire - Good Excel skills with minor development needed"
        elif self.overall_scores.overall_score >= 55:
            return "Consider - Basic skills present, requires significant training"
        else:
            return "No Hire - Insufficient Excel skills for role requirements"

@dataclass
class FeedbackTemplate:
    """Templates for generating consistent feedback"""
    
    @staticmethod
    def get_technical_feedback(score: float) -> str:
        if score >= 90:
            return "Excellent technical accuracy. Demonstrates deep understanding of Excel functions and formulas."
        elif score >= 75:
            return "Good technical knowledge with minor gaps. Shows solid understanding of core concepts."
        elif score >= 60:
            return "Basic technical understanding present. Some concepts need reinforcement."
        elif score >= 40:
            return "Limited technical accuracy. Requires significant skill development."
        else:
            return "Minimal technical understanding. Needs comprehensive Excel training."
    
    @staticmethod
    def get_depth_feedback(score: float) -> str:
        if score >= 90:
            return "Shows exceptional depth of knowledge with advanced Excel concepts."
        elif score >= 75:
            return "Good understanding of intermediate to advanced Excel features."
        elif score >= 60:
            return "Adequate depth for basic to intermediate Excel tasks."
        elif score >= 40:
            return "Surface-level understanding. Needs to develop deeper Excel knowledge."
        else:
            return "Very limited depth of Excel knowledge."
    
    @staticmethod
    def get_problem_solving_feedback(score: float) -> str:
        if score >= 90:
            return "Excellent problem-solving approach with logical, efficient solutions."
        elif score >= 75:
            return "Good analytical thinking and structured problem-solving methods."
        elif score >= 60:
            return "Basic problem-solving skills with some logical reasoning."
        elif score >= 40:
            return "Limited problem-solving approach. Needs to develop analytical thinking."
        else:
            return "Minimal problem-solving demonstration."
    
    @staticmethod
    def get_communication_feedback(score: float) -> str:
        if score >= 90:
            return "Clear, concise explanations with excellent technical communication."
        elif score >= 75:
            return "Good communication skills with mostly clear explanations."
        elif score >= 60:
            return "Adequate communication with some clarity issues."
        elif score >= 40:
            return "Communication needs improvement for better clarity."
        else:
            return "Poor communication clarity affects understanding."