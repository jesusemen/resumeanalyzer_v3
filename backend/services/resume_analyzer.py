from typing import List, Dict, Any, Optional
import json
import logging
import asyncio
import os
from datetime import datetime
import uuid
import google.generativeai as genai

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY environment variable not set. Analysis features will fail.")
        else:
            genai.configure(api_key=self.api_key)
    
    def _create_chat_session(self) -> genai.GenerativeModel:
        """Create a new Gemini chat session optimized for budget"""
        # specialized system instruction for the model
        system_instruction = """You are an expert HR specialist and resume analyzer. 
        Your task is to analyze resumes against job descriptions and provide accurate, 
        concise rankings. Focus on relevance, skills match, and job requirements."""
        
        # Use the most cost-effective model
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_instruction
        )
        return model
    
    async def analyze_batch_resumes(self, job_description: str, resumes: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze multiple resumes against job description in batches for budget optimization
        """
        if not self.api_key:
             raise ValueError("GEMINI_API_KEY not configured")

        try:
            # Aggressively small batches for free tier (3 resumes per call)
            batch_size = 3
            all_results = []
            
            for i in range(0, len(resumes), batch_size):
                batch = resumes[i:i+batch_size]
                logger.info(f"Processing batch {i//batch_size + 1} with {len(batch)} resumes")
                
                # Aggressive delay between batches (12 seconds) to stay well under RPM limits
                if i > 0:
                    logger.info("Waiting 12 seconds before next batch to respect API quota...")
                    await asyncio.sleep(12)
                
                batch_results = await self._analyze_single_batch_with_retry(job_description, batch)
                all_results.extend(batch_results)
            
            # Sort all results by score and take top 7
            all_results.sort(key=lambda x: x['score'], reverse=True)
            top_7 = all_results[:7]
            
            # Add rankings
            for idx, result in enumerate(top_7):
                result['rank'] = idx + 1
            
            # Check if we have any matches (threshold: 40%)
            has_matches = any(result['score'] >= 40 for result in top_7)
            
            return {
                'candidates': top_7,
                'noMatch': not has_matches,
                'total_analyzed': len(resumes),
                'analysis_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing resumes: {e}")
            raise
    
    async def _analyze_single_batch_with_retry(self, job_description: str, batch: List[Dict[str, str]], retries: int = 4) -> List[Dict[str, Any]]:
        """Analyze a single batch with aggressive backoff retry for 429 errors"""
        for attempt in range(retries):
            try:
                model = self._create_chat_session()
                prompt = self._create_batch_prompt(job_description, batch)
                
                # Generate content (async)
                response = await model.generate_content_async(prompt)
                
                if not response.text:
                    raise ValueError("Empty response from AI")
                    
                return self._parse_batch_response(response.text, batch)
                
            except Exception as e:
                error_msg = str(e)
                # Check for quota error (429)
                if "429" in error_msg and attempt < retries - 1:
                    # Default wait time is 30s, 60s, 90s...
                    wait_time = (attempt + 1) * 30
                    
                    # Try to parse recommended wait time from error message if available
                    import re
                    match = re.search(r"retry in ([\d\.]+)s", error_msg)
                    if match:
                        wait_time = float(match.group(1)) + 5 # Add a buffer
                    
                    logger.warning(f"Quota hit (429), waiting {wait_time}s (Attempt {attempt + 1}/{retries})")
                    await asyncio.sleep(wait_time)
                    continue
                
                logger.error(f"Failed to analyze batch on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    # Final attempt failed
                    return [
                        {
                            'name': r.get('name', 'Unknown'),
                            'email': r.get('email', ''),
                            'phone': r.get('phone', ''),
                            'score': 0,
                            'reasons': [f"Analysis failed: {error_msg[:100]}"]
                        }
                        for r in batch
                    ]
        return []

    async def _analyze_single_batch(self, job_description: str, batch: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        # This is now handled by _analyze_single_batch_with_retry
        return await self._analyze_single_batch_with_retry(job_description, batch)
    
    def _create_batch_prompt(self, job_description: str, batch: List[Dict[str, str]]) -> str:
        """Create an optimized prompt for batch processing"""
        prompt = f"""
TASK: Analyze the following resumes against the job description and provide rankings.

JOB DESCRIPTION:
{job_description}

RESUMES TO ANALYZE:
"""
        
        for idx, resume in enumerate(batch):
            prompt += f"""
RESUME {idx + 1}:
Name: {resume['name']}
Email: {resume['email']}  
Phone: {resume['phone']}
Content: {resume['content'][:2000]}...  # Limit content for budget
---
"""
        
        prompt += """
INSTRUCTIONS:
1. Analyze each resume against the job description
2. Score each candidate from 0-100 based on:
   - Skills match (40%)
   - Experience relevance (30%)
   - Education/qualifications (20%)
   - Overall fit (10%)
3. Provide 3-5 specific reasons for each ranking
4. Extract contact information accurately

RESPONSE FORMAT (JSON):
[
  {
    "resume_number": 1,
    "score": 85,
    "reasons": ["Strong React experience", "5+ years relevant experience", "Previous similar role"]
  },
  {
    "resume_number": 2,
    "score": 72,
    "reasons": ["Basic skills match", "Limited experience", "Good potential"]
  }
]

Respond with valid JSON only, no additional text. Do not use markdown code blocks.
"""
        return prompt
    
    def _parse_batch_response(self, response: str, batch: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Parse the AI response and create result objects"""
        try:
            # Clean up response if it contains markdown
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.startswith('```'):
                clean_response = clean_response[3:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            
            # Locate array start/end
            json_start = clean_response.find('[')
            json_end = clean_response.rfind(']') + 1
            if json_start != -1 and json_end != -1:
                json_str = clean_response[json_start:json_end]
            else:
                json_str = clean_response

            ai_results = json.loads(json_str)
            
            results = []
            for ai_result in ai_results:
                resume_idx = ai_result.get('resume_number', 0) - 1
                if 0 <= resume_idx < len(batch):
                    resume = batch[resume_idx]
                    results.append({
                        'name': resume['name'],
                        'email': resume['email'],
                        'phone': resume['phone'],
                        'score': ai_result.get('score', 0),
                        'reasons': ai_result.get('reasons', [])
                    })
            
            return results
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error parsing AI response: {e}")
            logger.error(f"Raw response: {response}")
            # Fallback: create basic results
            return [
                {
                    'name': resume.get('name', 'Unknown'),
                    'email': resume.get('email', ''),
                    'phone': resume.get('phone', ''),
                    'score': 0,  # Default score indicating failure
                    'reasons': ['Error analyzing this resume']
                }
                for resume in batch
            ]
    
    def _extract_contact_info(self, resume_text: str) -> Dict[str, str]:
        """Extract contact information from resume text"""
        import re
        
        # Basic regex patterns for contact info
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        email_match = re.search(email_pattern, resume_text)
        phone_match = re.search(phone_pattern, resume_text)
        
        # Extract name (first line or first few words)
        lines = resume_text.split('\n')
        name = lines[0].strip() if lines else "Unknown Candidate"
        
        return {
            'name': name[:50],  # Limit name length
            'email': email_match.group() if email_match else "email@example.com",
            'phone': phone_match.group() if phone_match else "+1-555-000-0000"
        }