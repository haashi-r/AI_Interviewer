# AI-Powered Excel Mock Interviewer

A comprehensive AI-driven system for assessing Excel skills through conversational interviews. Built with Streamlit frontend and Python backend, powered by Google's Gemini 2.5-flash model for intelligent evaluation.

# Features

- *Intelligent Conversational Interface*: Natural interview flow with contextual questioning
- *Adaptive Difficulty*: Questions adjust based on candidate performance
- *Comprehensive Evaluation*: Multi-dimensional scoring across technical, depth, problem-solving, and  communication skills

- *Real-time Feedback*: Immediate response evaluation during the interview
- *Detailed Reports*: PDF report generation with visualizations
- *Progress Tracking*: Live interview progress monitoring
- *Extensible Question Bank*: Easily expandable question database



# Installation & Setup

# Prerequisites
- Python 3.8+
- Google API Key for Gemini 2.5 flash



# Install Dependencies
```bash
pip install -r requirements.txt
```

# Environment Configuration

# Edit .env and add your Google API key
GOOGLE_API_KEY=your_google_api_key_here
```

### Step 4: Run the Application
```bash
# Using the runner script
python run.py

# Or directly with Streamlit
streamlit run frontend/streamlit_app.py
```

#  Configuration

# Environment Variables
- `GOOGLE_API_KEY`: Your Google AI Studio API key (required)
- `STREAMLIT_SERVER_PORT`: Port for Streamlit server (default: 8501)
- `DEBUG`: Enable debug mode (default: False)

# Interview Settings (config/settings.py)
- `MAX_QUESTIONS`: Maximum questions per interview (default: 15)
- `INTERVIEW_DURATION_MINUTES`: Target interview duration (default: 25)
- `MIN_SCORE_THRESHOLD`: Minimum passing score (default: 40)

### Evaluation Weights
- Technical Accuracy: 40%
- Depth of Knowledge: 25%
- Problem Solving: 20%
- Communication: 15%

## How It Works

### Interview Flow
1. **Introduction Phase**: Candidate information and experience assessment
2. **Assessment Phase**: Adaptive questioning with real-time evaluation
3. **Conclusion Phase**: Summary and detailed feedback

### Adaptive Logic
- Questions start at basic level and adjust based on performance
- Difficulty increases when candidate scores 75%+ consistently
- Difficulty decreases when candidate struggles (< 50% average)
- Categories rotate to ensure comprehensive coverage

### Evaluation System
Each answer is evaluated across four dimensions:
- **Technical Accuracy (40%)**: Correctness of Excel knowledge
- **Depth of Knowledge (25%)**: Understanding beyond surface level
- **Problem Solving (20%)**: Logical approach and methodology
- **Communication (15%)**: Clarity of explanation

##  Usage Examples

### Starting an Interview
1. Enter candidate name and optional email
2. System generates personalized welcome message
3. Candidate responds with their Excel experience level
4. Interview begins with appropriate difficulty level

### Sample Questions by Difficulty

**Basic**: "How would you calculate the sum of values in cells A1 to A10?"

**Intermediate**: "Walk me through creating a pivot table that shows sales by region and product category."

**Advanced**: "How would you use Power Query to combine multiple CSV files and create relationships for analysis?"

##  Reports & Analytics

### PDF Report 
- Candidate information
- Overall performance scores
- Skill level assessment
- Key strengths and improvement areas
- Development recommendations

##  Customization

### Adding New Questions
1. Edit the appropriate JSON file in `data/questions/`
2. Follow the existing question structure:
```json
{
  "id": "unique_id",
  "category": "Excel Category",
  "question": "Your question here?",
  "expected_points": ["Point 1", "Point 2"],
  "evaluation_criteria": "What to evaluate"
}
```

### Modifying Evaluation Criteria
1. Update `data/evaluation_rubrics/scoring_criteria.json`
2. Adjust weights and score ranges as needed
3. Restart the application

### Customizing UI
1. Modify CSS in `frontend/streamlit_app.py`
2. Adjust layout and styling as needed
3. Add new components following Streamlit conventions

##  Deployment Options

### Local Development
```bash
streamlit run frontend/streamlit_app.py
```


### Test Coverage
- Unit tests for core evaluation logic
- Integration tests for interview flow
- Mock tests for LLM interactions

##  Security Considerations

- API keys stored in environment variables
- No persistent storage of candidate responses
- Session data cleared after completion
- Input validation for all user responses

##  API Usage

### Google Gemini Pro
- Model: `gemini-2.5-flash`
- Temperature: 0.3 (balanced creativity/consistency)
- Max tokens: 2048
- Rate limiting: Handled with retry logic

##  Roadmap

### Phase 2 Features
-  Live Excel integration with screen sharing
-  Multi-language support
-  Advanced analytics dashboard
-  Custom company rubrics
-  Bulk candidate assessment

### Phase 3 Features
-  Video analysis integration
-  Team interview scenarios
-  API for ATS integration
-  Mobile app version



##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Troubleshooting

### Common Issues

**"Google API Key not found"**
- Ensure `.env` file exists with valid `GOOGLE_API_KEY`
- Check API key permissions in Google AI Studio

**"Session not found"**
- Browser refresh clears session state
- Use "Reset Interview" button to restart

**"Error generating response"**
- Check internet connection
- Verify API key validity and quota
- Review logs for detailed error messages

### Performance Tips
- Ensure stable internet connection for LLM calls
- Close other browser tabs to free up memory
- Use Chrome or Firefox for best compatibility

##  Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Review the troubleshooting section
- Check the documentation

---

Built with using Streamlit, Google gemini-2.5-flash, and Python