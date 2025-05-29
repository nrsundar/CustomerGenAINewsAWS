"""
Configuration module for GenAI Content Monitor
Handles all application settings and environment variables
"""

import os
from typing import List
from dotenv import load_dotenv

class Config:
    """Configuration class for the application"""
    
    def __init__(self):
        load_dotenv()
        
        # Website monitoring configuration
        self.WEBSITES = self._parse_websites()
        
        # AI Model configuration
        self.SUMMARIZATION_MODEL = os.getenv("SUMMARIZATION_MODEL", "facebook/bart-large-cnn")
        self.CLASSIFICATION_MODEL = os.getenv("CLASSIFICATION_MODEL", "microsoft/DialoGPT-medium")
        self.GENAI_KEYWORDS = self._parse_keywords()
        
        # Email configuration
        self.EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
        self.EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
        self.EMAIL_SENDER = os.getenv("EMAIL_SENDER", self.EMAIL_USERNAME)
        
        # Storage configuration
        self.STORAGE_FILE = os.getenv("STORAGE_FILE", "articles_seen.json")
        
        # Scraping configuration
        self.SCRAPING_DELAY = float(os.getenv("SCRAPING_DELAY", "2.0"))
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        
        # Validate required configuration
        self._validate_config()
    
    def _parse_websites(self) -> List[str]:
        """Parse website URLs from environment variable or database"""
        websites_str = os.getenv("WEBSITES", "")
        if websites_str:
            # Use websites from environment variable
            return [url.strip() for url in websites_str.split(",") if url.strip()]
        else:
            # Try to get websites from simple database
            try:
                from simple_database import SimpleDatabase
                db = SimpleDatabase()
                company_websites = db.get_all_websites()
                if company_websites:
                    return company_websites
            except:
                pass
            
            # Your requested financial companies
            return [
                "https://www.jpmorganchase.com/news",
                "https://www.jpmorgan.com/insights",
                "https://newsroom.bankofamerica.com",
                "https://about.bankofamerica.com/en/making-an-impact",
                "https://www.capitalone.com/about/newsroom",
                "https://www.capitalone.com/tech"
            ]
    
    def _parse_keywords(self) -> List[str]:
        """Parse GenAI keywords from environment variable"""
        keywords_str = os.getenv("GENAI_KEYWORDS", "")
        if not keywords_str:
            # Default GenAI related keywords
            return [
                "generative ai", "genai", "gpt", "large language model", "llm",
                "chatgpt", "claude", "artificial intelligence", "machine learning",
                "neural network", "transformer", "diffusion", "stable diffusion",
                "midjourney", "dall-e", "text generation", "image generation",
                "natural language processing", "nlp", "deep learning"
            ]
        return [keyword.strip().lower() for keyword in keywords_str.split(",") if keyword.strip()]
    
    def _validate_config(self):
        """Validate required configuration parameters"""
        if not self.WEBSITES:
            raise ValueError("At least one website URL must be configured")
