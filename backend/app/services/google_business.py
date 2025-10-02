from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import List, Dict, Optional
from app.core.config import settings


class GoogleBusinessService:
    """Service for interacting with Google Business Profile API"""
    
    def __init__(self, access_token: str, refresh_token: str):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET
        )
        self.service = build('mybusinessbusinessinformation', 'v1', credentials=self.credentials)
        self.account_service = build('mybusinessaccountmanagement', 'v1', credentials=self.credentials)
    
    def get_accounts(self) -> List[Dict]:
        """Get all Google Business accounts"""
        try:
            accounts = self.account_service.accounts().list().execute()
            return accounts.get('accounts', [])
        except Exception as e:
            print(f"Error getting accounts: {e}")
            return []
    
    def get_locations(self, account_id: str) -> List[Dict]:
        """Get all locations for an account"""
        try:
            parent = f"accounts/{account_id}"
            locations = self.service.accounts().locations().list(parent=parent).execute()
            return locations.get('locations', [])
        except Exception as e:
            print(f"Error getting locations: {e}")
            return []
    
    def get_location(self, location_name: str) -> Optional[Dict]:
        """Get a specific location"""
        try:
            location = self.service.locations().get(name=location_name).execute()
            return location
        except Exception as e:
            print(f"Error getting location: {e}")
            return None
    
    def create_post(self, location_name: str, post_data: Dict) -> Optional[Dict]:
        """Create a local post for a location"""
        try:
            # Note: The actual API endpoint may vary
            # This is a simplified version
            parent = location_name
            post = self.service.locations().localPosts().create(
                parent=parent,
                body=post_data
            ).execute()
            return post
        except Exception as e:
            print(f"Error creating post: {e}")
            return None
    
    def get_reviews(self, location_name: str) -> List[Dict]:
        """Get reviews for a location"""
        try:
            parent = location_name
            reviews = self.service.accounts().locations().reviews().list(
                parent=parent
            ).execute()
            return reviews.get('reviews', [])
        except Exception as e:
            print(f"Error getting reviews: {e}")
            return []
    
    def reply_to_review(self, review_name: str, reply_text: str) -> Optional[Dict]:
        """Reply to a review"""
        try:
            reply = self.service.accounts().locations().reviews().updateReply(
                name=review_name,
                body={'comment': reply_text}
            ).execute()
            return reply
        except Exception as e:
            print(f"Error replying to review: {e}")
            return None
