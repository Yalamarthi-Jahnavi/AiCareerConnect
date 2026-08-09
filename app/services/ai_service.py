"""
Mistral AI Service
====================
All Mistral API communication happens here.

WHY THIS FILE EXISTS:
    Centralizes ALL AI/Mistral API calls in one place. This is the ONLY
    file that talks to the Mistral API. Benefits:
    1. Easy to swap AI providers (OpenAI, Gemini) — change one file
    2. API key management in one place
    3. Prompt engineering lives here, not scattered across routes
    4. Rate limiting, retries, and error handling in one spot
"""

import json
import requests
from flask import current_app


class MistralAIService:
    """Service for communicating with the Mistral AI API."""
    
    def _get_api_key(self):
        """Get Mistral API key from app config."""
        return current_app.config.get('MISTRAL_API_KEY', '')
    
    def _get_model(self):
        """Get the Mistral model name from config."""
        return current_app.config.get('MISTRAL_MODEL', 'mistral-large-latest')
    
    def _call_mistral(self, messages, max_tokens=2000, temperature=0.7):
        """
        Make a request to the Mistral AI Chat Completions API.
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0 = deterministic, 1.0 = creative)
        
        Returns:
            str: The AI response text
        """
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError('MISTRAL_API_KEY not configured. Set it in .env file.')
        
        api_url = current_app.config.get('MISTRAL_API_URL', 'https://api.mistral.ai/v1/chat/completions')
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'model': self._get_model(),
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def analyze_resume(self, resume_text):
        """
        Analyze a resume and extract structured data.
        
        Returns:
            dict: Extracted skills, experience, education, summary
        """
        messages = [
            {
                'role': 'system',
                'content': (
                    'You are an expert career counselor and resume analyst. '
                    'Analyze the resume and return a JSON object with: '
                    '"skills" (list), "experience" (list of objects with company, role, duration), '
                    '"education" (list), "summary" (brief professional summary), '
                    '"strengths" (list), "areas_to_improve" (list). '
                    'Return ONLY valid JSON, no markdown.'
                )
            },
            {
                'role': 'user',
                'content': f'Analyze this resume:\n\n{resume_text}'
            }
        ]
        
        response = self._call_mistral(messages, max_tokens=3000, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {'raw_analysis': response}
    
    def match_jobs(self, user_profile, jobs):
        """
        Match a user profile against available jobs and rank them.
        
        Returns:
            list: Jobs ranked by match score with explanations
        """
        jobs_text = json.dumps(jobs[:20], indent=2)  # Limit to prevent token overflow
        
        messages = [
            {
                'role': 'system',
                'content': (
                    'You are an AI job matching expert. Given a candidate profile and job listings, '
                    'rank the jobs by match score (0-100). Return a JSON array of objects with: '
                    '"job_id", "match_score", "match_reasons" (list of why it matches), '
                    '"skill_gaps" (skills the candidate needs). '
                    'Return ONLY valid JSON, no markdown.'
                )
            },
            {
                'role': 'user',
                'content': (
                    f'Candidate Profile:\n{json.dumps(user_profile, indent=2)}\n\n'
                    f'Available Jobs:\n{jobs_text}'
                )
            }
        ]
        
        response = self._call_mistral(messages, max_tokens=3000, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{'raw_response': response}]
    
    def get_career_advice(self, question, user_context):
        """
        Get personalized career advice from AI.
        
        Returns:
            str: AI-generated career advice
        """
        messages = [
            {
                'role': 'system',
                'content': (
                    'You are a senior career counselor with 20 years of experience. '
                    'Provide actionable, personalized career advice. Be specific, '
                    'encouraging, and practical. Consider the user\'s current skills '
                    'and experience level.'
                )
            },
            {
                'role': 'user',
                'content': (
                    f'My background: Skills: {user_context.get("skills", "Not specified")}, '
                    f'Experience: {user_context.get("experience", 0)} years, '
                    f'Bio: {user_context.get("bio", "Not specified")}\n\n'
                    f'My question: {question}'
                )
            }
        ]
        
        return self._call_mistral(messages, max_tokens=2000, temperature=0.7)
    
    def improve_resume(self, resume_text, target_role=''):
        """
        Get AI suggestions to improve a resume.
        
        Returns:
            dict: Improvement suggestions
        """
        messages = [
            {
                'role': 'system',
                'content': (
                    'You are an expert resume writer. Analyze the resume and provide '
                    'specific, actionable improvements. Return JSON with: '
                    '"overall_score" (0-100), "improvements" (list of specific suggestions), '
                    '"missing_sections" (list), "keyword_suggestions" (list for ATS optimization), '
                    '"rewritten_summary" (improved professional summary). '
                    'Return ONLY valid JSON.'
                )
            },
            {
                'role': 'user',
                'content': (
                    f'Target Role: {target_role or "General"}\n\n'
                    f'Resume:\n{resume_text}'
                )
            }
        ]
        
        response = self._call_mistral(messages, max_tokens=3000, temperature=0.5)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {'raw_suggestions': response}
    
    def generate_interview_questions(self, job_title, job_description=''):
        """
        Generate interview prep questions for a specific role.
        
        Returns:
            dict: Categorized interview questions
        """
        messages = [
            {
                'role': 'system',
                'content': (
                    'You are an expert interviewer. Generate interview questions '
                    'categorized as: "technical" (role-specific), "behavioral" (STAR method), '
                    '"situational" (what-would-you-do), and "general". '
                    'For each question, include a "tip" for how to answer well. '
                    'Return JSON with these categories as keys, each containing a list of '
                    '{"question": "...", "tip": "..."}. Return ONLY valid JSON.'
                )
            },
            {
                'role': 'user',
                'content': (
                    f'Job Title: {job_title}\n'
                    f'Job Description: {job_description or "Not provided"}'
                )
            }
        ]
        
        response = self._call_mistral(messages, max_tokens=3000, temperature=0.6)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {'raw_questions': response}
