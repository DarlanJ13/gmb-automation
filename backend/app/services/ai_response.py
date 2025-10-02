from openai import OpenAI
from app.core.config import settings
from typing import Optional


class AIResponseService:
    """Service for generating AI responses using OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_post_content(
        self,
        business_name: str,
        business_category: str,
        topic: Optional[str] = None,
        post_type: str = "UPDATE"
    ) -> str:
        """Generate content for a Google Business post"""
        
        if topic:
            prompt = f"""Create a {post_type.lower()} post for {business_name}, a {business_category} business, about: {topic}.
            
The post should be:
- Engaging and professional
- Between 100-300 characters
- Include a call to action
- Suitable for Google Business Profile

Generate only the post content, no additional text."""
        else:
            prompt = f"""Create a {post_type.lower()} post for {business_name}, a {business_category} business.
            
The post should be:
- Engaging and professional
- Between 100-300 characters
- Include a call to action
- Suitable for Google Business Profile
- Relevant to the business type

Generate only the post content, no additional text."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional social media manager specializing in Google Business Profile posts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating post content: {e}")
            return ""
    
    def generate_review_reply(
        self,
        business_name: str,
        reviewer_name: str,
        rating: float,
        review_comment: Optional[str],
        tone: str = "professional"
    ) -> str:
        """Generate a reply to a customer review"""
        
        sentiment = "positive" if rating >= 4 else "negative" if rating <= 2 else "neutral"
        
        prompt = f"""Generate a {tone} reply to a {sentiment} review for {business_name}.

Reviewer: {reviewer_name}
Rating: {rating}/5 stars
Review: {review_comment if review_comment else "No comment provided"}

The reply should:
- Be warm and {tone}
- Thank the customer
- Address their feedback appropriately
- Be between 50-150 words
- {"Acknowledge and apologize for any issues" if sentiment == "negative" else "Express gratitude"}

Generate only the reply text, no additional formatting."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional customer service representative responding to online reviews."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating review reply: {e}")
            return ""
    
    def analyze_review_sentiment(self, review_text: str) -> Dict[str, any]:
        """Analyze the sentiment of a review"""
        
        prompt = f"""Analyze the sentiment of this review and provide:
1. Overall sentiment (positive/negative/neutral)
2. Key topics mentioned
3. Urgency level (low/medium/high)

Review: {review_text}

Respond in JSON format."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            # Parse the response (simplified - in production, use proper JSON parsing)
            return {"analysis": response.choices[0].message.content.strip()}
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"analysis": "Unable to analyze"}
