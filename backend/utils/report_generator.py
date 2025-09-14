from fpdf import FPDF
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
import io
import base64

class InterviewReportGenerator:
    def __init__(self):
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#F18F01',
            'warning': '#C73E1D',
            'info': '#6C757D'
        }
    
    def generate_pdf_report(self, interview_data: Dict[str, Any]) -> bytes:
        """Generate a comprehensive PDF report"""
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 15)
                self.cell(0, 10, 'Excel Skills Assessment Report', 0, 1, 'C')
                self.ln(10)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
        pdf = PDF()
        pdf.add_page()
        
        # Candidate Information
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Candidate Information', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        candidate_info = interview_data.get('candidate_info', {})
        pdf.cell(0, 8, f"Name: {candidate_info.get('name', 'Not provided')}", 0, 1)
        pdf.cell(0, 8, f"Email: {candidate_info.get('email', 'Not provided')}", 0, 1)
        pdf.cell(0, 8, f"Interview Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1)
        pdf.cell(0, 8, f"Duration: {interview_data.get('duration', 'N/A')} minutes", 0, 1)
        pdf.ln(5)
        
        # Overall Score
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Overall Performance', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        scores = interview_data.get('scores', {})
        overall_score = scores.get('overall_score', 0)
        
        pdf.cell(0, 8, f"Overall Score: {overall_score:.1f}/100", 0, 1)
        pdf.cell(0, 8, f"Skill Level: {interview_data.get('skill_level', 'Not determined')}", 0, 1)
        pdf.cell(0, 8, f"Hiring Recommendation: {interview_data.get('hiring_recommendation', 'Not provided')}", 0, 1)
        pdf.ln(5)
        
        # Score Breakdown
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Score Breakdown', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        pdf.cell(0, 8, f"Technical Accuracy (40%): {scores.get('technical_score', 0):.1f}/100", 0, 1)
        pdf.cell(0, 8, f"Depth of Knowledge (25%): {scores.get('depth_score', 0):.1f}/100", 0, 1)
        pdf.cell(0, 8, f"Problem Solving (20%): {scores.get('problem_solving_score', 0):.1f}/100", 0, 1)
        pdf.cell(0, 8, f"Communication (15%): {scores.get('communication_score', 0):.1f}/100", 0, 1)
        pdf.ln(5)
        
        # Key Strengths
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Key Strengths', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        strengths = interview_data.get('key_strengths', [])
        for i, strength in enumerate(strengths, 1):
            pdf.cell(0, 8, f"{i}. {strength}", 0, 1)
        pdf.ln(5)
        
        # Areas for Improvement
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Areas for Improvement', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        improvements = interview_data.get('improvement_areas', [])
        for i, improvement in enumerate(improvements, 1):
            pdf.cell(0, 8, f"{i}. {improvement}", 0, 1)
        pdf.ln(5)
        
        # Recommendations
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Development Recommendations', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        recommendations = interview_data.get('development_recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            pdf.cell(0, 8, f"{i}. {rec}", 0, 1)
        
        return pdf.output(dest='S').encode('latin1')
    
    def generate_performance_chart(self, scores: Dict[str, float]) -> str:
        """Generate a radar chart for performance visualization"""
        
        categories = ['Technical\nAccuracy', 'Depth of\nKnowledge', 
                     'Problem\nSolving', 'Communication']
        values = [
            scores.get('technical_score', 0),
            scores.get('depth_score', 0),
            scores.get('problem_solving_score', 0),
            scores.get('communication_score', 0)
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # Close the loop
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor=self.colors['primary'] + '40',
            line=dict(color=self.colors['primary'], width=2),
            name='Performance'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    ticksuffix='',
                    dtick=20
                )
            ),
            showlegend=False,
            title="Performance Radar Chart",
            font=dict(size=12)
        )
        
        # Convert to base64 string
        img_bytes = fig.to_image(format="png", width=600, height=400)
        img_base64 = base64.b64encode(img_bytes).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def generate_category_performance_chart(self, category_scores: Dict[str, float]) -> str:
        """Generate a bar chart for category-wise performance"""
        
        categories = list(category_scores.keys())
        scores = list(category_scores.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=scores,
                marker_color=self.colors['primary'],
                text=[f'{score:.1f}%' for score in scores],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Performance by Excel Category",
            xaxis_title="Excel Categories",
            yaxis_title="Score (%)",
            yaxis=dict(range=[0, 100]),
            showlegend=False,
            font=dict(size=12)
        )
        
        # Convert to base64 string
        img_bytes = fig.to_image(format="png", width=800, height=400)
        img_base64 = base64.b64encode(img_bytes).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def generate_html_report(self, interview_data: Dict[str, Any]) -> str:
        """Generate a comprehensive HTML report"""
        
        # Generate charts
        scores = interview_data.get('scores', {})
        radar_chart = self.generate_performance_chart(scores)
        
        category_scores = interview_data.get('category_performance', {})
        category_chart = ""
        if category_scores:
            category_chart = self.generate_category_performance_chart(category_scores)
        
        # HTML template
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel Skills Assessment Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, {self.colors['primary']}, {self.colors['secondary']});
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .score-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .score-item {{
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid {self.colors['primary']};
        }}
        .score-value {{
            font-size: 2em;
            font-weight: bold;
            color: {self.colors['primary']};
        }}
        .chart-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .list-item {{
            background: #f8f9fa;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 6px;
            border-left: 3px solid {self.colors['success']};
        }}
        .improvement-item {{
            border-left-color: {self.colors['warning']};
        }}
        .recommendation-item {{
            border-left-color: {self.colors['info']};
        }}
        h1, h2, h3 {{
            color: {self.colors['primary']};
        }}
        .skill-level {{
            display: inline-block;
            padding: 8px 16px;
            background: {self.colors['success']};
            color: white;
            border-radius: 20px;
            font-weight: bold;
        }}
        .hiring-rec {{
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-weight: bold;
        }}
        .strong-hire {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .hire {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .consider {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .no-hire {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Excel Skills Assessment Report</h1>
        <p>Comprehensive Technical Interview Analysis</p>
    </div>

    <div class="card">
        <h2>Candidate Information</h2>
        <p><strong>Name:</strong> {interview_data.get('candidate_info', {}).get('name', 'Not provided')}</p>
        <p><strong>Email:</strong> {interview_data.get('candidate_info', {}).get('email', 'Not provided')}</p>
        <p><strong>Interview Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
        <p><strong>Duration:</strong> {interview_data.get('duration', 'N/A')} minutes</p>
        <p><strong>Questions Answered:</strong> {interview_data.get('total_questions', 'N/A')}</p>
    </div>

    <div class="card">
        <h2>Overall Performance Summary</h2>
        <div style="text-align: center; margin: 20px 0;">
            <div class="score-value" style="font-size: 3em;">{scores.get('overall_score', 0):.1f}/100</div>
            <p><span class="skill-level">{interview_data.get('skill_level', 'Not determined')}</span></p>
        </div>
        
        <div class="hiring-rec {self.get_recommendation_class(interview_data.get('hiring_recommendation', ''))}">
            Hiring Recommendation: {interview_data.get('hiring_recommendation', 'Not provided')}
        </div>
    </div>

    <div class="card">
        <h2>Performance Breakdown</h2>
        <div class="score-grid">
            <div class="score-item">
                <div class="score-value">{scores.get('technical_score', 0):.1f}</div>
                <div>Technical Accuracy (40%)</div>
            </div>
            <div class="score-item">
                <div class="score-value">{scores.get('depth_score', 0):.1f}</div>
                <div>Depth of Knowledge (25%)</div>
            </div>
            <div class="score-item">
                <div class="score-value">{scores.get('problem_solving_score', 0):.1f}</div>
                <div>Problem Solving (20%)</div>
            </div>
            <div class="score-item">
                <div class="score-value">{scores.get('communication_score', 0):.1f}</div>
                <div>Communication (15%)</div>
            </div>
        </div>
        
        <div class="chart-container">
            <img src="{radar_chart}" alt="Performance Radar Chart">
        </div>
    </div>

    {f'''<div class="card">
        <h2>Performance by Excel Category</h2>
        <div class="chart-container">
            <img src="{category_chart}" alt="Category Performance Chart">
        </div>
    </div>''' if category_chart else ''}

    <div class="card">
        <h2>Key Strengths</h2>
        {self.format_list_items(interview_data.get('key_strengths', []), 'list-item')}
    </div>

    <div class="card">
        <h2>Areas for Improvement</h2>
        {self.format_list_items(interview_data.get('improvement_areas', []), 'list-item improvement-item')}
    </div>

    <div class="card">
        <h2>Development Recommendations</h2>
        {self.format_list_items(interview_data.get('development_recommendations', []), 'list-item recommendation-item')}
    </div>

    <div class="card">
        <h2>Detailed Analysis</h2>
        <p><strong>Consistency Analysis:</strong> {interview_data.get('consistency_analysis', 'Not available')}</p>
        <p><strong>Role Readiness:</strong> {interview_data.get('readiness_for_role', 'Not available')}</p>
        <p><strong>Overall Impression:</strong> {interview_data.get('overall_impression', 'Not available')}</p>
    </div>

    <div class="card" style="text-align: center; color: #6c757d;">
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <p>AI-Powered Excel Mock Interviewer System</p>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def get_recommendation_class(self, recommendation: str) -> str:
        """Get CSS class for hiring recommendation"""
        if "Strong Hire" in recommendation:
            return "strong-hire"
        elif "Hire" in recommendation and "No" not in recommendation:
            return "hire"
        elif "Consider" in recommendation:
            return "consider"
        else:
            return "no-hire"
    
    def format_list_items(self, items: List[str], css_class: str) -> str:
        """Format list items as HTML"""
        if not items:
            return "<p>None identified</p>"
        
        html = ""
        for item in items:
            html += f'<div class="{css_class}">{item}</div>\n'
        return html

# Global instance
report_generator = InterviewReportGenerator()