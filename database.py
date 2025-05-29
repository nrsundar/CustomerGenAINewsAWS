"""
Database module for GenAI Content Monitor
Handles PostgreSQL database operations for articles, companies, and tracking
"""

import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL database operations"""
    
    def __init__(self):
        self.connection = None
        self.connect()
        self.setup_tables()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=os.getenv('PGHOST'),
                database=os.getenv('PGDATABASE'),
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                port=os.getenv('PGPORT')
            )
            self.connection.autocommit = True
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def setup_tables(self):
        """Create necessary database tables"""
        try:
            with self.connection.cursor() as cursor:
                # Companies table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS companies (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) UNIQUE NOT NULL,
                        sector VARCHAR(100),
                        websites TEXT[],
                        keywords TEXT[],
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Articles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        url VARCHAR(500) UNIQUE NOT NULL,
                        content TEXT,
                        summary TEXT,
                        source_url VARCHAR(500),
                        company_id INTEGER REFERENCES companies(id),
                        is_genai_related BOOLEAN DEFAULT FALSE,
                        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Monitoring stats table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS monitoring_stats (
                        id SERIAL PRIMARY KEY,
                        run_date DATE DEFAULT CURRENT_DATE,
                        total_articles_found INTEGER DEFAULT 0,
                        genai_articles_found INTEGER DEFAULT 0,
                        websites_monitored INTEGER DEFAULT 0,
                        processing_time_seconds INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_genai ON articles(is_genai_related)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_discovered ON articles(discovered_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)")
                
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Failed to setup database tables: {e}")
            raise
    
    def add_company(self, name: str, sector: str, websites: List[str], keywords: List[str] = None) -> bool:
        """Add a new company to track"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO companies (name, sector, websites, keywords)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        sector = EXCLUDED.sector,
                        websites = EXCLUDED.websites,
                        keywords = EXCLUDED.keywords,
                        updated_at = CURRENT_TIMESTAMP
                """, (name, sector, websites or [], keywords or []))
                
                logger.info(f"Added/updated company: {name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add company {name}: {e}")
            return False
    
    def get_companies(self) -> List[Dict]:
        """Get all companies"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM companies ORDER BY name")
                companies = []
                for row in cursor.fetchall():
                    companies.append({
                        'id': row['id'],
                        'name': row['name'],
                        'sector': row['sector'],
                        'websites': row['websites'] or [],
                        'keywords': row['keywords'] or []
                    })
                return companies
                
        except Exception as e:
            logger.error(f"Failed to get companies: {e}")
            return []
    
    def get_all_websites(self) -> List[str]:
        """Get all website URLs from all companies"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT websites FROM companies WHERE websites IS NOT NULL")
                websites = []
                for row in cursor.fetchall():
                    if row[0]:  # websites array
                        websites.extend(row[0])
                return websites
                
        except Exception as e:
            logger.error(f"Failed to get websites: {e}")
            return []
    
    def is_article_seen(self, url: str) -> bool:
        """Check if an article URL has been seen before"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM articles WHERE url = %s", (url,))
                return cursor.fetchone() is not None
                
        except Exception as e:
            logger.error(f"Failed to check if article seen: {e}")
            return False
    
    def save_article(self, title: str, url: str, content: str, summary: str = None, 
                    source_url: str = None, is_genai_related: bool = False) -> bool:
        """Save a new article to the database"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO articles (title, url, content, summary, source_url, is_genai_related)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        summary = EXCLUDED.summary,
                        is_genai_related = EXCLUDED.is_genai_related,
                        processed_at = CURRENT_TIMESTAMP
                """, (title, url, content, summary, source_url, is_genai_related))
                
                logger.debug(f"Saved article: {title}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save article {url}: {e}")
            return False
    
    def get_recent_articles(self, limit: int = 50, genai_only: bool = True) -> List[Dict]:
        """Get recent articles from the database"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT a.*, c.name as company_name, c.sector as company_sector
                    FROM articles a
                    LEFT JOIN companies c ON a.company_id = c.id
                    WHERE 1=1
                """
                params = []
                
                if genai_only:
                    query += " AND a.is_genai_related = TRUE"
                
                query += " ORDER BY a.discovered_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                articles = []
                for row in cursor.fetchall():
                    articles.append({
                        'id': row['id'],
                        'title': row['title'],
                        'url': row['url'],
                        'content': row['content'],
                        'summary': row['summary'],
                        'source_url': row['source_url'],
                        'company_name': row['company_name'],
                        'company_sector': row['company_sector'],
                        'is_genai_related': row['is_genai_related'],
                        'discovered_at': row['discovered_at'].strftime('%Y-%m-%d %H:%M') if row['discovered_at'] else None
                    })
                return articles
                
        except Exception as e:
            logger.error(f"Failed to get recent articles: {e}")
            return []
    
    def save_monitoring_stats(self, total_articles: int, genai_articles: int, 
                            websites_count: int, processing_time: int) -> bool:
        """Save monitoring run statistics"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO monitoring_stats 
                    (total_articles_found, genai_articles_found, websites_monitored, processing_time_seconds)
                    VALUES (%s, %s, %s, %s)
                """, (total_articles, genai_articles, websites_count, processing_time))
                
                logger.info(f"Saved monitoring stats: {genai_articles}/{total_articles} GenAI articles")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save monitoring stats: {e}")
            return False
    
    def get_dashboard_stats(self) -> Dict:
        """Get statistics for the dashboard"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Total articles
                cursor.execute("SELECT COUNT(*) as total FROM articles")
                total_articles = cursor.fetchone()['total']
                
                # GenAI articles
                cursor.execute("SELECT COUNT(*) as genai FROM articles WHERE is_genai_related = TRUE")
                genai_articles = cursor.fetchone()['genai']
                
                # Companies being tracked
                cursor.execute("SELECT COUNT(*) as companies FROM companies")
                total_companies = cursor.fetchone()['companies']
                
                # Recent activity
                cursor.execute("""
                    SELECT COUNT(*) as recent 
                    FROM articles 
                    WHERE discovered_at >= CURRENT_DATE - INTERVAL '7 days'
                    AND is_genai_related = TRUE
                """)
                recent_activity = cursor.fetchone()['recent']
                
                # Last update
                cursor.execute("""
                    SELECT MAX(discovered_at) as last_update 
                    FROM articles 
                    WHERE is_genai_related = TRUE
                """)
                last_update_row = cursor.fetchone()
                last_update = last_update_row['last_update'].strftime('%Y-%m-%d %H:%M') if last_update_row['last_update'] else 'Never'
                
                return {
                    'total_articles': total_articles,
                    'genai_articles': genai_articles,
                    'total_companies': total_companies,
                    'recent_activity': recent_activity,
                    'last_update': last_update
                }
                
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return {
                'total_articles': 0,
                'genai_articles': 0,
                'total_companies': 0,
                'recent_activity': 0,
                'last_update': 'Error'
            }
    
    def import_companies_from_csv_data(self, companies_data: List[Dict]) -> bool:
        """Import companies from parsed CSV data"""
        try:
            with self.connection.cursor() as cursor:
                # Clear existing companies
                cursor.execute("DELETE FROM companies")
                
                # Insert new companies
                for company in companies_data:
                    self.add_company(
                        name=company['name'],
                        sector=company['sector'],
                        websites=company['websites'],
                        keywords=company['keywords']
                    )
                
                logger.info(f"Imported {len(companies_data)} companies from CSV")
                return True
                
        except Exception as e:
            logger.error(f"Failed to import companies: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")