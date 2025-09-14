from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

class InterviewPhase(Enum):
    INTRODUCTION = "introduction"
    ASSESSMENT = "assessment"
    CONCLUSION = "conclusion"
    COMPLETED = "completed"

class QuestionDifficulty(Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class QuestionResponse:
    question_id: str
    question: str
    answer: str
    score: float
    feedback: str
    category: str
    difficulty: QuestionDifficulty
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class InterviewState:
    session_id: str
    candidate_name: str
    candidate_email: Optional[str]
    current_phase: InterviewPhase
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Experience and Assessment
    experience_level: Optional[str] = None
    current_difficulty: QuestionDifficulty = QuestionDifficulty.BASIC
    
    # Questions and Responses
    questions_asked: List[QuestionResponse] = field(default_factory=list)
    current_question_index: int = 0
    
    # Scoring
    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    depth_score: Optional[float] = None
    problem_solving_score: Optional[float] = None
    communication_score: Optional[float] = None
    
    # Interview Flow
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    is_completed: bool = False
    
    def add_response(self, response: QuestionResponse):
        """Add a question response to the interview state"""
        self.questions_asked.append(response)
        self.current_question_index += 1
    
    def add_conversation(self, role: str, message: str):
        """Add a conversation turn to the history"""
        self.conversation_history.append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_current_score(self) -> float:
        """Calculate current average score based on answered questions"""
        if not self.questions_asked:
            return 0.0
        
        total_score = sum(q.score for q in self.questions_asked)
        return total_score / len(self.questions_asked)
    
    def get_category_performance(self) -> Dict[str, float]:
        """Get performance breakdown by category"""
        category_scores = {}
        category_counts = {}
        
        for response in self.questions_asked:
            cat = response.category
            if cat not in category_scores:
                category_scores[cat] = 0
                category_counts[cat] = 0
            
            category_scores[cat] += response.score
            category_counts[cat] += 1
        
        return {
            cat: category_scores[cat] / category_counts[cat] 
            for cat in category_scores
        }
    
    def should_increase_difficulty(self) -> bool:
        """Determine if difficulty should be increased based on recent performance"""
        if len(self.questions_asked) < 3:
            return False
        
        # Check last 3 questions
        recent_scores = [q.score for q in self.questions_asked[-3:]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        # Increase difficulty if recent performance is good
        if self.current_difficulty == QuestionDifficulty.BASIC and avg_recent >= 75:
            return True
        elif self.current_difficulty == QuestionDifficulty.INTERMEDIATE and avg_recent >= 80:
            return True
        
        return False
    
    def should_decrease_difficulty(self) -> bool:
        """Determine if difficulty should be decreased based on poor performance"""
        if len(self.questions_asked) < 2:
            return False
        
        # Check last 2 questions
        recent_scores = [q.score for q in self.questions_asked[-2:]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        # Decrease difficulty if struggling
        if self.current_difficulty == QuestionDifficulty.ADVANCED and avg_recent < 60:
            return True
        elif self.current_difficulty == QuestionDifficulty.INTERMEDIATE and avg_recent < 50:
            return True
        
        return False