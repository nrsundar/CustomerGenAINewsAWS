"""
Web scraping module for GenAI Content Monitor
Handles website scraping with ethical practices and fallback mechanisms
"""

import os
import time
import logging
import requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import trafilatura

logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraper with ethical practices and multiple extraction methods"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GenAI-Content-Monitor/1.0 (Educational Purpose)'
        })
    
    def _check_robots_txt(self, url: str) -> bool:
        """Check if scraping is allowed by robots.txt"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            return rp.can_fetch(self.session.headers['User-Agent'], url)
        except Exception as e:
            logger.warning(f"Could not check robots.txt for {url}: {e}")
            return True  # Assume allowed if we can't check
    
    def _extract_with_trafilatura(self, url: str) -> Optional[str]:
        """Extract content using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                return text
        except Exception as e:
            logger.warning(f"Trafilatura extraction failed for {url}: {e}")
        return None
    
    def _extract_with_beautifulsoup(self, url: str) -> Optional[str]:
        """Extract content using BeautifulSoup as fallback"""
        try:
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content areas
            content_selectors = [
                'article', 'main', '[role="main"]', '.content', '#content',
                '.post', '.entry', '.article-content', '.blog-post'
            ]
            
            content = None
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text() for elem in elements])
                    break
            
            if not content:
                # Fallback to body text
                content = soup.get_text()
            
            # Clean up whitespace
            content = ' '.join(content.split())
            return content
            
        except Exception as e:
            logger.warning(f"BeautifulSoup extraction failed for {url}: {e}")
        return None
    
    def _extract_articles_from_page(self, url: str) -> List[Dict]:
        """Extract article information from a page"""
        articles = []
        
        try:
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common article selectors
            article_selectors = [
                'article', '.post', '.entry', '.blog-post', '.article',
                '[itemtype*="Article"]', '.content-item', '.news-item'
            ]
            
            article_elements = []
            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    article_elements = elements
                    break
            
            if not article_elements:
                # Fallback: look for links that might be articles
                article_elements = soup.find_all('a', href=True)
            
            for element in article_elements[:20]:  # Limit to first 20 to avoid overload
                try:
                    # Extract title
                    title = None
                    title_selectors = ['h1', 'h2', 'h3', '.title', '.headline']
                    for title_sel in title_selectors:
                        title_elem = element.select_one(title_sel)
                        if title_elem:
                            title = title_elem.get_text().strip()
                            break
                    
                    if not title and element.name == 'a':
                        title = element.get_text().strip()
                    
                    # Extract URL
                    article_url = None
                    if element.name == 'a':
                        article_url = element.get('href')
                    else:
                        link_elem = element.find('a', href=True)
                        if link_elem:
                            article_url = link_elem.get('href')
                    
                    if article_url:
                        article_url = urljoin(url, article_url)
                    
                    if title and article_url and len(title) > 10:
                        # Extract content from the article page
                        content = self._extract_article_content(article_url)
                        if content and len(content) > 100:  # Minimum content length
                            articles.append({
                                'title': title,
                                'url': article_url,
                                'content': content,
                                'source_url': url
                            })
                
                except Exception as e:
                    logger.warning(f"Error extracting article from element: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error extracting articles from {url}: {e}")
        
        return articles
    
    def _extract_article_content(self, url: str) -> Optional[str]:
        """Extract content from an individual article URL"""
        # First try trafilatura (most effective for article content)
        content = self._extract_with_trafilatura(url)
        if content and len(content) > 100:
            return content
        
        # Fallback to BeautifulSoup
        content = self._extract_with_beautifulsoup(url)
        return content
    
    def scrape_articles(self, url: str) -> List[Dict]:
        """Scrape articles from a website"""
        articles = []
        
        # Check robots.txt compliance
        if not self._check_robots_txt(url):
            logger.warning(f"Robots.txt disallows scraping of {url}")
            return articles
        
        logger.info(f"Scraping articles from: {url}")
        
        # Add delay to be respectful
        time.sleep(self.config.SCRAPING_DELAY)
        
        # Extract articles from the main page
        articles = self._extract_articles_from_page(url)
        
        logger.info(f"Successfully extracted {len(articles)} articles from {url}")
        return articles
