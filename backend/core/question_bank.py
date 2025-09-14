import json
import random
from typing import List, Dict, Any, Optional
from models.interview_state import QuestionDifficulty

class ExcelQuestionBank:
    def __init__(self):
        self.questions = {
            QuestionDifficulty.BASIC: self._load_basic_questions(),
            QuestionDifficulty.INTERMEDIATE: self._load_intermediate_questions(),
            QuestionDifficulty.ADVANCED: self._load_advanced_questions()
        }
        self.used_questions = set()
    
    def _load_basic_questions(self) -> List[Dict[str, Any]]:
        """Load basic Excel questions"""
        return [
            {
                "id": "basic_001",
                "category": "Formulas & Functions",
                "question": "How would you calculate the sum of values in cells A1 to A10? What if you wanted to exclude any text values in that range?",
                "expected_points": [
                    "Use SUM(A1:A10) for basic sum",
                    "Can mention SUM function ignores text automatically",
                    "Alternative approaches like using array formulas"
                ],
                "evaluation_criteria": "Look for correct SUM syntax and understanding of function behavior"
            },
            {
                "id": "basic_002",
                "category": "Data Management",
                "question": "You have a list of customer names in column A with some duplicates. How would you identify and remove the duplicate entries?",
                "expected_points": [
                    "Data tab -> Remove Duplicates feature",
                    "Conditional formatting to highlight duplicates",
                    "Using filters or advanced filters"
                ],
                "evaluation_criteria": "Understanding of Excel's data cleaning capabilities"
            },
            {
                "id": "basic_003",
                "category": "Cell Formatting",
                "question": "Explain how you would format a column of numbers to display as currency with two decimal places. What if you wanted different currencies for different rows?",
                "expected_points": [
                    "Right-click -> Format Cells -> Currency",
                    "Custom number format codes",
                    "Using different currency symbols"
                ],
                "evaluation_criteria": "Knowledge of formatting options and flexibility"
            },
            {
                "id": "basic_004",
                "category": "Basic Functions",
                "question": "What's the difference between AVERAGE() and MEDIAN() functions? When would you use each one?",
                "expected_points": [
                    "AVERAGE calculates arithmetic mean",
                    "MEDIAN finds middle value",
                    "Understanding when each is more appropriate"
                ],
                "evaluation_criteria": "Statistical understanding and practical application"
            },
            {
                "id": "basic_005",
                "category": "Data Entry",
                "question": "How would you quickly fill a series of dates (like every Monday for the next 12 weeks) in Excel?",
                "expected_points": [
                    "Fill Series feature",
                    "AutoFill with drag",
                    "Understanding date arithmetic"
                ],
                "evaluation_criteria": "Efficiency in data entry techniques"
            }
        ]
    
    def _load_intermediate_questions(self) -> List[Dict[str, Any]]:
        """Load intermediate Excel questions"""
        return [
            {
                "id": "inter_001",
                "category": "Pivot Tables",
                "question": "Walk me through creating a pivot table from a sales data set. How would you show total sales by region and product category, and then add a filter for specific time periods?",
                "expected_points": [
                    "Insert -> Pivot Table process",
                    "Drag fields to appropriate areas",
                    "Adding filters and slicers",
                    "Grouping dates by periods"
                ],
                "evaluation_criteria": "Comprehensive understanding of pivot table creation and customization"
            },
            {
                "id": "inter_002",
                "category": "Advanced Formulas",
                "question": "You need to look up an employee's salary based on their ID, but the ID might not exist. How would you handle this scenario and return 'Not Found' if the ID doesn't exist?",
                "expected_points": [
                    "VLOOKUP with IFERROR",
                    "INDEX/MATCH combination",
                    "Error handling strategies",
                    "Mention of XLOOKUP if familiar"
                ],
                "evaluation_criteria": "Error handling and advanced lookup techniques"
            },
            {
                "id": "inter_003",
                "category": "Conditional Logic",
                "question": "Create a formula that assigns letter grades (A, B, C, D, F) based on numerical scores, where A=90+, B=80-89, C=70-79, D=60-69, F=below 60.",
                "expected_points": [
                    "Nested IF statements",
                    "IFS function (newer Excel)",
                    "LOOKUP table approach",
                    "Proper logical structure"
                ],
                "evaluation_criteria": "Complex conditional logic implementation"
            },
            {
                "id": "inter_004",
                "category": "Data Analysis",
                "question": "You have monthly sales data for 3 years. How would you identify trends, seasonality, and create a forecast for the next 6 months?",
                "expected_points": [
                    "Charts for visualization",
                    "TREND or FORECAST functions",
                    "Moving averages",
                    "Data analysis toolpack features"
                ],
                "evaluation_criteria": "Analytical thinking and forecasting knowledge"
            },
            {
                "id": "inter_005",
                "category": "Charts & Visualization",
                "question": "How would you create a dashboard showing KPI metrics with dynamic charts that update based on dropdown selections?",
                "expected_points": [
                    "Data validation for dropdowns",
                    "Dynamic named ranges or tables",
                    "Chart data source linking",
                    "Dashboard design principles"
                ],
                "evaluation_criteria": "Integration of multiple Excel features for dynamic reporting"
            }
        ]
    
    def _load_advanced_questions(self) -> List[Dict[str, Any]]:
        """Load advanced Excel questions"""
        return [
            {
                "id": "adv_001",
                "category": "VBA & Automation",
                "question": "How would you automate a monthly reporting process that involves importing data, cleaning it, creating pivot tables, and generating charts? Walk me through your VBA approach.",
                "expected_points": [
                    "VBA macro structure",
                    "Data import methods",
                    "Object manipulation",
                    "Error handling in VBA",
                    "User interface considerations"
                ],
                "evaluation_criteria": "Programming logic and automation understanding"
            },
            {
                "id": "adv_002",
                "category": "Array Formulas",
                "question": "Explain how you would use array formulas to find the top 3 sales values and their corresponding salesperson names from a large dataset without using helper columns.",
                "expected_points": [
                    "LARGE function for top values",
                    "INDEX/MATCH with array logic",
                    "Dynamic arrays (if Office 365)",
                    "CSE array formula entry"
                ],
                "evaluation_criteria": "Advanced array formula concepts and implementation"
            },
            {
                "id": "adv_003",
                "category": "Data Modeling",
                "question": "You're building a financial model with scenario analysis. How would you structure it to allow easy switching between best case, worst case, and most likely scenarios?",
                "expected_points": [
                    "Data tables for scenarios",
                    "Input cells and assumptions",
                    "INDIRECT or OFFSET functions",
                    "Model structure best practices",
                    "Sensitivity analysis"
                ],
                "evaluation_criteria": "Financial modeling expertise and structural thinking"
            },
            {
                "id": "adv_004",
                "category": "Power Query",
                "question": "How would you use Power Query to combine multiple CSV files with similar structures, clean the data, and create relationships for analysis?",
                "expected_points": [
                    "Get Data from folder",
                    "Data transformation steps",
                    "Append queries",
                    "Data types and cleaning",
                    "Loading to data model"
                ],
                "evaluation_criteria": "Modern Excel data processing capabilities"
            },
            {
                "id": "adv_005",
                "category": "Complex Analysis",
                "question": "Design a solution for tracking project budgets vs actuals with variance analysis, alerts for budget overruns, and automatic escalation reporting.",
                "expected_points": [
                    "Conditional formatting for alerts",
                    "Complex formulas for variance",
                    "Dashboard design",
                    "Automated reporting features",
                    "Integration considerations"
                ],
                "evaluation_criteria": "Business process integration and complex problem solving"
            }
        ]
    
    def get_question(
        self, 
        difficulty: QuestionDifficulty, 
        category: Optional[str] = None,
        exclude_used: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get a question based on difficulty and optionally category"""
        
        available_questions = self.questions[difficulty].copy()
        
        # Filter by category if specified
        if category:
            available_questions = [
                q for q in available_questions 
                if q["category"].lower() == category.lower()
            ]
        
        # Exclude used questions if requested
        if exclude_used:
            available_questions = [
                q for q in available_questions 
                if q["id"] not in self.used_questions
            ]
        
        if not available_questions:
            return None
        
        # Select random question
        selected_question = random.choice(available_questions)
        self.used_questions.add(selected_question["id"])
        
        return selected_question
    
    def get_adaptive_question(
        self, 
        current_performance: float, 
        current_difficulty: QuestionDifficulty,
        answered_categories: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Get next question based on adaptive logic"""
        
        # Determine next difficulty based on performance
        next_difficulty = current_difficulty
        
        if current_performance >= 80 and current_difficulty != QuestionDifficulty.ADVANCED:
            # Increase difficulty if performing well
            if current_difficulty == QuestionDifficulty.BASIC:
                next_difficulty = QuestionDifficulty.INTERMEDIATE
            else:
                next_difficulty = QuestionDifficulty.ADVANCED
        elif current_performance < 50 and current_difficulty != QuestionDifficulty.BASIC:
            # Decrease difficulty if struggling
            if current_difficulty == QuestionDifficulty.ADVANCED:
                next_difficulty = QuestionDifficulty.INTERMEDIATE
            else:
                next_difficulty = QuestionDifficulty.BASIC
        
        # Try to get a question from an unexplored category
        all_categories = set()
        for questions in self.questions.values():
            all_categories.update(q["category"] for q in questions)
        
        unexplored_categories = all_categories - set(answered_categories)
        
        if unexplored_categories:
            category = random.choice(list(unexplored_categories))
            question = self.get_question(next_difficulty, category)
            if question:
                return question
        
        # Fallback to any available question
        return self.get_question(next_difficulty)
    
    def get_categories(self, difficulty: QuestionDifficulty) -> List[str]:
        """Get all categories for a given difficulty level"""
        return list(set(q["category"] for q in self.questions[difficulty]))
    
    def reset_used_questions(self):
        """Reset the used questions tracker"""
        self.used_questions.clear()
    
    def get_question_stats(self) -> Dict[str, Any]:
        """Get statistics about the question bank"""
        stats = {
            "total_questions": sum(len(questions) for questions in self.questions.values()),
            "by_difficulty": {
                difficulty.value: len(questions) 
                for difficulty, questions in self.questions.items()
            },
            "categories": {}
        }
        
        # Category breakdown
        for difficulty, questions in self.questions.items():
            for question in questions:
                category = question["category"]
                if category not in stats["categories"]:
                    stats["categories"][category] = {
                        "total": 0,
                        "by_difficulty": {d.value: 0 for d in QuestionDifficulty}
                    }
                stats["categories"][category]["total"] += 1
                stats["categories"][category]["by_difficulty"][difficulty.value] += 1
        
        return stats

# Global instance
question_bank = ExcelQuestionBank()