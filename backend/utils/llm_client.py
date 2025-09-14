from groq import Groq
import json
import logging
from typing import Dict, Any, Optional
from config.settings import settings

class LLMClient:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.logger = logging.getLogger(__name__)
    
    async def generate_response(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: float = None
    ) -> str:
        """Generate a response using Groq"""
        try:
            if temperature is None:
                temperature = settings.TEMPERATURE
            
            # Add system instruction if provided, plus general instruction to avoid HTML
            base_instruction = "Please provide responses in plain text only, without any HTML tags, markdown formatting, or special characters."
            
            messages = []
            if system_instruction:
                messages.append({
                    "role": "system", 
                    "content": f"{system_instruction}\n{base_instruction}"
                })
            else:
                messages.append({
                    "role": "system",
                    "content": base_instruction
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=messages,
                temperature=temperature,
                max_tokens=settings.MAX_TOKENS,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
    async def generate_json_response(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: float = None
    ) -> Dict[str, Any]:
        """Generate a structured JSON response"""
        try:
            json_instruction = "\n\nPlease respond with valid JSON only, no additional text."
            full_prompt = prompt + json_instruction
            
            response_text = await self.generate_response(
                full_prompt, 
                system_instruction, 
                temperature
            )
            
            # Clean the response to extract JSON
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Parse JSON
            return json.loads(response_text.strip())
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            self.logger.error(f"Raw response: {response_text}")
            
            # Fallback response
            return {
                "error": "Failed to parse response",
                "raw_response": response_text
            }
        except Exception as e:
            self.logger.error(f"Error generating JSON response: {str(e)}")
            return {"error": str(e)}
    
    async def evaluate_answer(
        self, 
        question: str, 
        answer: str, 
        category: str,
        difficulty: str
    ) -> Dict[str, Any]:
        """Evaluate a candidate's answer to an Excel question"""
        
        evaluation_prompt = f"""
You are an expert Excel interviewer evaluating a candidate's response. 

Question: {question}
Category: {category}
Difficulty: {difficulty}
Candidate's Answer: {answer}

Please evaluate this answer across four dimensions and provide scores (0-100):

1. Technical Accuracy (40% weight): How technically correct is the answer?
2. Depth of Knowledge (25% weight): Does the answer demonstrate deep understanding?
3. Problem-Solving Approach (20% weight): Is the approach logical and efficient?
4. Communication Clarity (15% weight): How clearly is the answer explained?

Provide your evaluation in the following JSON format:
{{
    "technical_score": <0-100>,
    "depth_score": <0-100>,
    "problem_solving_score": <0-100>,
    "communication_score": <0-100>,
    "overall_score": <calculated weighted average>,
    "feedback": "Detailed feedback explaining the scores",
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "follow_up_questions": ["question1", "question2"]
}}

Be fair but thorough in your evaluation. Consider the difficulty level when scoring.
"""
        
        return await self.generate_json_response(evaluation_prompt)
    
    async def generate_next_question(
        self, 
        conversation_history: str,
        current_performance: str,
        difficulty: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate the next appropriate question based on conversation context"""
        
        question_prompt = f"""
You are an expert Excel interviewer conducting a technical interview.

Conversation History:
{conversation_history}

Current Performance Summary:
{current_performance}

Generate the next appropriate Excel question with the following specifications:
- Difficulty Level: {difficulty}
- Category Focus: {category if category else "Any relevant Excel skill area"}

The question should:
1. Build naturally on the conversation
2. Test practical Excel skills
3. Be appropriate for the difficulty level
4. Allow for detailed assessment of the candidate's knowledge

Provide your response in the following JSON format:
{{
    "question": "Your Excel question here",
    "category": "excel_category",
    "expected_answer_points": ["point1", "point2", "point3"],
    "evaluation_criteria": "What to look for in a good answer",
    "difficulty_justification": "Why this question fits the {difficulty} level"
}}
"""
        
        return await self.generate_json_response(question_prompt)
    
    async def generate_interview_summary(
        self, 
        interview_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a comprehensive interview summary and report"""
        
        summary_prompt = f"""
You are an expert Excel interviewer providing a final assessment summary.

Interview Data:
{json.dumps(interview_data, indent=2)}

Generate a comprehensive interview summary that includes:

1. Overall skill level assessment (Novice/Basic/Intermediate/Advanced/Expert)
2. Key strengths demonstrated
3. Areas needing improvement
4. Specific recommendations for skill development
5. Hiring recommendation with justification
6. Performance consistency analysis

Provide your assessment in the following JSON format:
{{
    "skill_level": "Expert|Advanced|Intermediate|Basic|Novice",
    "skill_level_justification": "Explanation for the skill level assignment",
    "key_strengths": ["strength1", "strength2", "strength3"],
    "improvement_areas": ["area1", "area2", "area3"],
    "development_recommendations": ["rec1", "rec2", "rec3"],
    "hiring_recommendation": "Strong Hire|Hire|Consider|No Hire",
    "hiring_justification": "Detailed explanation for hiring recommendation",
    "consistency_analysis": "Assessment of performance consistency",
    "readiness_for_role": "Assessment of role readiness",
    "overall_impression": "Final thoughts on the candidate"
}}
"""
        
        return await self.generate_json_response(summary_prompt)

# Global instance
llm_client = LLMClient()








# import google.generativeai as genai
# import json
# import logging
# from typing import Dict, Any, Optional
# from config.settings import settings

# class LLMClient:
#     def __init__(self):
#         if not settings.GOOGLE_API_KEY:
#             raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
#         genai.configure(api_key=settings.GOOGLE_API_KEY)
#         self.model = genai.GenerativeModel(settings.MODEL_NAME)
#         self.logger = logging.getLogger(__name__)
    
#     async def generate_response(
#         self, 
#         prompt: str, 
#         system_instruction: Optional[str] = None,
#         temperature: float = None
#     ) -> str:
#         """Generate a response using Gemini Pro"""
#         try:
#             if temperature is None:
#                 temperature = settings.TEMPERATURE
            
#             # Configure generation parameters
#             generation_config = genai.types.GenerationConfig(
#                 temperature=temperature,
#                 max_output_tokens=settings.MAX_TOKENS,
#             )
            
#             # Add system instruction if provided
#             full_prompt = prompt
#             if system_instruction:
#                 full_prompt = f"{system_instruction}\n\n{prompt}"
            
#             response = self.model.generate_content(
#                 full_prompt,
#                 generation_config=generation_config
#             )
            
#             return response.text
            
#         except Exception as e:
#             self.logger.error(f"Error generating response: {str(e)}")
#             return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
#     async def generate_json_response(
#         self, 
#         prompt: str, 
#         system_instruction: Optional[str] = None,
#         temperature: float = None
#     ) -> Dict[str, Any]:
#         """Generate a structured JSON response"""
#         try:
#             json_instruction = "\n\nPlease respond with valid JSON only, no additional text."
#             full_prompt = prompt + json_instruction
            
#             response_text = await self.generate_response(
#                 full_prompt, 
#                 system_instruction, 
#                 temperature
#             )
            
#             # Clean the response to extract JSON
#             response_text = response_text.strip()
            
#             # Remove markdown code blocks if present
#             if response_text.startswith("```json"):
#                 response_text = response_text[7:]
#             if response_text.startswith("```"):
#                 response_text = response_text[3:]
#             if response_text.endswith("```"):
#                 response_text = response_text[:-3]
            
#             # Parse JSON
#             return json.loads(response_text.strip())
            
#         except json.JSONDecodeError as e:
#             self.logger.error(f"JSON parsing error: {str(e)}")
#             self.logger.error(f"Raw response: {response_text}")
            
#             # Fallback response
#             return {
#                 "error": "Failed to parse response",
#                 "raw_response": response_text
#             }
#         except Exception as e:
#             self.logger.error(f"Error generating JSON response: {str(e)}")
#             return {"error": str(e)}
    
#     async def evaluate_answer(
#         self, 
#         question: str, 
#         answer: str, 
#         category: str,
#         difficulty: str
#     ) -> Dict[str, Any]:
#         """Evaluate a candidate's answer to an Excel question"""
        
#         evaluation_prompt = f"""
# You are an expert Excel interviewer evaluating a candidate's response. 

# Question: {question}
# Category: {category}
# Difficulty: {difficulty}
# Candidate's Answer: {answer}

# Please evaluate this answer across four dimensions and provide scores (0-100):

# 1. Technical Accuracy (40% weight): How technically correct is the answer?
# 2. Depth of Knowledge (25% weight): Does the answer demonstrate deep understanding?
# 3. Problem-Solving Approach (20% weight): Is the approach logical and efficient?
# 4. Communication Clarity (15% weight): How clearly is the answer explained?

# Provide your evaluation in the following JSON format:
# {{
#     "technical_score": <0-100>,
#     "depth_score": <0-100>,
#     "problem_solving_score": <0-100>,
#     "communication_score": <0-100>,
#     "overall_score": <calculated weighted average>,
#     "feedback": "Detailed feedback explaining the scores",
#     "strengths": ["strength1", "strength2"],
#     "improvements": ["improvement1", "improvement2"],
#     "follow_up_questions": ["question1", "question2"]
# }}

# Be fair but thorough in your evaluation. Consider the difficulty level when scoring.
# """
        
#         return await self.generate_json_response(evaluation_prompt)
    
#     async def generate_next_question(
#         self, 
#         conversation_history: str,
#         current_performance: str,
#         difficulty: str,
#         category: Optional[str] = None
#     ) -> Dict[str, Any]:
#         """Generate the next appropriate question based on conversation context"""
        
#         question_prompt = f"""
# You are an expert Excel interviewer conducting a technical interview.

# Conversation History:
# {conversation_history}

# Current Performance Summary:
# {current_performance}

# Generate the next appropriate Excel question with the following specifications:
# - Difficulty Level: {difficulty}
# - Category Focus: {category if category else "Any relevant Excel skill area"}

# The question should:
# 1. Build naturally on the conversation
# 2. Test practical Excel skills
# 3. Be appropriate for the difficulty level
# 4. Allow for detailed assessment of the candidate's knowledge

# Provide your response in the following JSON format:
# {{
#     "question": "Your Excel question here",
#     "category": "excel_category",
#     "expected_answer_points": ["point1", "point2", "point3"],
#     "evaluation_criteria": "What to look for in a good answer",
#     "difficulty_justification": "Why this question fits the {difficulty} level"
# }}
# """
        
#         return await self.generate_json_response(question_prompt)
    
#     async def generate_interview_summary(
#         self, 
#         interview_data: Dict[str, Any]
#     ) -> Dict[str, Any]:
#         """Generate a comprehensive interview summary and report"""
        
#         summary_prompt = f"""
# You are an expert Excel interviewer providing a final assessment summary.

# Interview Data:
# {json.dumps(interview_data, indent=2)}

# Generate a comprehensive interview summary that includes:

# 1. Overall skill level assessment (Novice/Basic/Intermediate/Advanced/Expert)
# 2. Key strengths demonstrated
# 3. Areas needing improvement
# 4. Specific recommendations for skill development
# 5. Hiring recommendation with justification
# 6. Performance consistency analysis

# Provide your assessment in the following JSON format:
# {{
#     "skill_level": "Expert|Advanced|Intermediate|Basic|Novice",
#     "skill_level_justification": "Explanation for the skill level assignment",
#     "key_strengths": ["strength1", "strength2", "strength3"],
#     "improvement_areas": ["area1", "area2", "area3"],
#     "development_recommendations": ["rec1", "rec2", "rec3"],
#     "hiring_recommendation": "Strong Hire|Hire|Consider|No Hire",
#     "hiring_justification": "Detailed explanation for hiring recommendation",
#     "consistency_analysis": "Assessment of performance consistency",
#     "readiness_for_role": "Assessment of role readiness",
#     "overall_impression": "Final thoughts on the candidate"
# }}
# """
        
#         return await self.generate_json_response(summary_prompt)

# # Global instance
# llm_client = LLMClient()