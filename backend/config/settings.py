import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Interview Configuration
    MAX_QUESTIONS = 15
    INTERVIEW_DURATION_MINUTES = 25
    MIN_SCORE_THRESHOLD = 40
    
    # LLM Configuration
    MODEL_NAME = "gemini-2.5-flash"
    TEMPERATURE = 0.3
    MAX_TOKENS = 2048
    
    # Evaluation Weights
    TECHNICAL_WEIGHT = 0.40
    DEPTH_WEIGHT = 0.25
    PROBLEM_SOLVING_WEIGHT = 0.20
    COMMUNICATION_WEIGHT = 0.15

settings = Settings()