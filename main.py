#!/usr/bin/env python3
"""
GenAI Content Monitor - Main Application
Monitors websites for GenAI-related content and sends email notifications
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

from config import Config
from scraper import WebScraper
from ai_processor import AIProcessor
from web_publisher import WebPublisher
from simple_database import SimpleDatabase
from utils import setup_logging

def main():
    """Main application entry point"""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration
        config = Config()
        logger.info("Starting GenAI Content Monitor")
        
        # Initialize components
        db = SimpleDatabase()
        scraper = WebScraper(config)
        ai_processor = AIProcessor(config)
        web_publisher = WebPublisher(config)
        
        # Track new articles found
        new_articles = []
        
        # Monitor each configured website
        for website_url in config.WEBSITES:
            logger.info(f"Monitoring website: {website_url}")
            
            try:
                # Scrape articles from website
                articles = scraper.scrape_articles(website_url)
                logger.info(f"Found {len(articles)} articles on {website_url}")
                
                # Filter for new articles only
                for article in articles:
                    if not db.is_article_seen(article['url']):
                        # Check if article is GenAI related
                        if ai_processor.is_genai_related(article['content']):
                            # Summarize the article
                            summary = ai_processor.summarize_article(article['content'])
                            article['summary'] = summary
                            new_articles.append(article)
                            
                            # Save to database
                            db.save_article(
                                title=article['title'],
                                url=article['url'],
                                content=article['content'],
                                summary=summary,
                                source_url=article.get('source_url', ''),
                                is_genai_related=True
                            )
                            logger.info(f"New GenAI article found: {article['title']}")
                        else:
                            # Save as seen even if not GenAI related to avoid reprocessing
                            db.save_article(
                                title=article['title'],
                                url=article['url'],
                                content=article['content'],
                                source_url=article.get('source_url', ''),
                                is_genai_related=False
                            )
                            
            except Exception as e:
                logger.error(f"Error processing website {website_url}: {str(e)}")
                continue
        
        # Publish articles to web page
        if new_articles:
            logger.info(f"Publishing {len(new_articles)} new articles to web page")
            web_publisher.publish_articles(new_articles)
            logger.info(f"Web page updated successfully: {web_publisher.get_web_url()}")
        else:
            logger.info("No new GenAI articles found")
            # Still publish empty page to show last update time
            web_publisher.publish_articles([])
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
