"""
Storage module for GenAI Content Monitor
Handles persistent storage of seen articles using JSON
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class ArticleStorage:
    """JSON-based storage for tracking seen articles"""
    
    def __init__(self, storage_file: str = "articles_seen.json"):
        self.storage_file = storage_file
        self.seen_articles = self._load_seen_articles()
    
    def _load_seen_articles(self) -> Dict:
        """Load seen articles from JSON file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data.get('articles', {}))} seen articles from {self.storage_file}")
                    return data
            else:
                logger.info(f"No existing storage file found. Creating new storage: {self.storage_file}")
                return {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "articles": {}
                }
        except Exception as e:
            logger.error(f"Error loading seen articles: {e}")
            return {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "articles": {}
            }
    
    def _save_seen_articles(self):
        """Save seen articles to JSON file"""
        try:
            self.seen_articles["last_updated"] = datetime.now().isoformat()
            
            # Create directory if it doesn't exist
            Path(self.storage_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first, then rename for atomic operation
            temp_file = f"{self.storage_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.seen_articles, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            os.rename(temp_file, self.storage_file)
            
            logger.debug(f"Saved seen articles to {self.storage_file}")
            
        except Exception as e:
            logger.error(f"Error saving seen articles: {e}")
    
    def is_article_seen(self, url: str) -> bool:
        """Check if an article URL has been seen before"""
        return url in self.seen_articles.get("articles", {})
    
    def mark_article_seen(self, url: str, title: str = None):
        """Mark an article as seen"""
        if "articles" not in self.seen_articles:
            self.seen_articles["articles"] = {}
        
        self.seen_articles["articles"][url] = {
            "title": title,
            "first_seen": datetime.now().isoformat(),
            "seen_count": self.seen_articles["articles"].get(url, {}).get("seen_count", 0) + 1
        }
        
        self._save_seen_articles()
        logger.debug(f"Marked article as seen: {title} ({url})")
    
    def get_seen_articles(self) -> Dict:
        """Get all seen articles"""
        return self.seen_articles.get("articles", {})
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        articles = self.seen_articles.get("articles", {})
        return {
            "total_articles_seen": len(articles),
            "storage_file": self.storage_file,
            "created_at": self.seen_articles.get("created_at"),
            "last_updated": self.seen_articles.get("last_updated"),
            "file_size_bytes": os.path.getsize(self.storage_file) if os.path.exists(self.storage_file) else 0
        }
    
    def cleanup_old_articles(self, days_old: int = 30):
        """Remove articles older than specified days (optional cleanup)"""
        from datetime import datetime, timedelta
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            articles = self.seen_articles.get("articles", {})
            
            urls_to_remove = []
            for url, article_data in articles.items():
                try:
                    first_seen = datetime.fromisoformat(article_data.get("first_seen", ""))
                    if first_seen < cutoff_date:
                        urls_to_remove.append(url)
                except (ValueError, TypeError):
                    # Remove articles with invalid dates
                    urls_to_remove.append(url)
            
            for url in urls_to_remove:
                del articles[url]
            
            if urls_to_remove:
                self._save_seen_articles()
                logger.info(f"Cleaned up {len(urls_to_remove)} old articles")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def export_to_csv(self, output_file: str = "seen_articles.csv"):
        """Export seen articles to CSV for analysis"""
        try:
            import csv
            
            articles = self.seen_articles.get("articles", {})
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['url', 'title', 'first_seen', 'seen_count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for url, data in articles.items():
                    writer.writerow({
                        'url': url,
                        'title': data.get('title', ''),
                        'first_seen': data.get('first_seen', ''),
                        'seen_count': data.get('seen_count', 0)
                    })
            
            logger.info(f"Exported {len(articles)} articles to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
