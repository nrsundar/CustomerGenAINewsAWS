"""
Company management module for GenAI Content Monitor
Handles company lists and financial sector websites
"""

import csv
import json
import logging
import os
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class CompanyManager:
    """Manages company lists and their associated websites"""
    
    def __init__(self):
        self.companies_file = "companies.json"
        self.companies = self._load_companies()
    
    def _load_companies(self) -> List[Dict]:
        """Load companies from JSON file"""
        try:
            if os.path.exists(self.companies_file):
                with open(self.companies_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} companies from {self.companies_file}")
                    return data
            else:
                # Default financial companies
                default_companies = self._get_default_financial_companies()
                self._save_companies(default_companies)
                return default_companies
        except Exception as e:
            logger.error(f"Error loading companies: {e}")
            return self._get_default_financial_companies()
    
    def _save_companies(self, companies: List[Dict]):
        """Save companies to JSON file"""
        try:
            with open(self.companies_file, 'w', encoding='utf-8') as f:
                json.dump(companies, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(companies)} companies to {self.companies_file}")
        except Exception as e:
            logger.error(f"Error saving companies: {e}")
    
    def _get_default_financial_companies(self) -> List[Dict]:
        """Get default list of top financial companies"""
        return [
            {
                "name": "JPMorgan Chase",
                "sector": "Banking",
                "websites": [
                    "https://www.jpmorganchase.com/news",
                    "https://www.jpmorgan.com/insights"
                ],
                "keywords": ["artificial intelligence", "machine learning", "digital transformation", "fintech", "automation"]
            },
            {
                "name": "Bank of America",
                "sector": "Banking", 
                "websites": [
                    "https://newsroom.bankofamerica.com",
                    "https://about.bankofamerica.com/en/making-an-impact"
                ],
                "keywords": ["AI", "digital banking", "technology", "innovation", "automation"]
            },
            {
                "name": "Goldman Sachs",
                "sector": "Investment Banking",
                "websites": [
                    "https://www.goldmansachs.com/insights",
                    "https://www.goldmansachs.com/media"
                ],
                "keywords": ["artificial intelligence", "machine learning", "algorithmic trading", "fintech", "digital assets"]
            },
            {
                "name": "Morgan Stanley",
                "sector": "Investment Banking",
                "websites": [
                    "https://www.morganstanley.com/ideas",
                    "https://www.morganstanley.com/press-releases"
                ],
                "keywords": ["AI", "technology", "digital transformation", "wealth management technology"]
            },
            {
                "name": "Wells Fargo",
                "sector": "Banking",
                "websites": [
                    "https://newsroom.wf.com",
                    "https://www.wellsfargo.com/about/corporate-responsibility"
                ],
                "keywords": ["artificial intelligence", "digital banking", "technology innovation", "customer experience"]
            },
            {
                "name": "Citigroup",
                "sector": "Banking",
                "websites": [
                    "https://www.citigroup.com/global/news",
                    "https://www.citi.com/news"
                ],
                "keywords": ["AI", "digital transformation", "fintech", "blockchain", "automation"]
            },
            {
                "name": "BlackRock",
                "sector": "Asset Management",
                "websites": [
                    "https://www.blackrock.com/corporate/insights",
                    "https://www.blackrock.com/corporate/newsroom"
                ],
                "keywords": ["artificial intelligence", "machine learning", "algorithmic investing", "technology", "ESG"]
            },
            {
                "name": "American Express",
                "sector": "Financial Services",
                "websites": [
                    "https://about.americanexpress.com/newsroom",
                    "https://www.americanexpress.com/en-us/business/trends-and-insights"
                ],
                "keywords": ["AI", "machine learning", "fraud detection", "customer experience", "fintech"]
            },
            {
                "name": "Visa",
                "sector": "Payment Technology",
                "websites": [
                    "https://usa.visa.com/about-visa/newsroom.html",
                    "https://usa.visa.com/partner-with-us/visa-technology.html"
                ],
                "keywords": ["artificial intelligence", "machine learning", "payment technology", "fraud prevention", "digital payments"]
            },
            {
                "name": "Mastercard",
                "sector": "Payment Technology", 
                "websites": [
                    "https://www.mastercard.us/en-us/news.html",
                    "https://www.mastercard.com/news/insights"
                ],
                "keywords": ["AI", "machine learning", "cybersecurity", "digital payments", "fintech innovation"]
            }
        ]
    
    def get_all_websites(self) -> List[str]:
        """Get all website URLs from all companies"""
        websites = []
        for company in self.companies:
            websites.extend(company.get('websites', []))
        return websites
    
    def get_companies(self) -> List[Dict]:
        """Get all companies"""
        return self.companies
    
    def add_company(self, name: str, sector: str, websites: List[str], keywords: List[str] = None) -> bool:
        """Add a new company"""
        try:
            new_company = {
                "name": name,
                "sector": sector,
                "websites": websites,
                "keywords": keywords or []
            }
            self.companies.append(new_company)
            self._save_companies(self.companies)
            logger.info(f"Added company: {name}")
            return True
        except Exception as e:
            logger.error(f"Error adding company {name}: {e}")
            return False
    
    def remove_company(self, name: str) -> bool:
        """Remove a company by name"""
        try:
            self.companies = [c for c in self.companies if c['name'] != name]
            self._save_companies(self.companies)
            logger.info(f"Removed company: {name}")
            return True
        except Exception as e:
            logger.error(f"Error removing company {name}: {e}")
            return False
    
    def import_from_csv(self, csv_file_path: str) -> bool:
        """Import companies from CSV file"""
        try:
            new_companies = []
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Expected columns: name, sector, websites, keywords
                    websites = [w.strip() for w in row.get('websites', '').split(',') if w.strip()]
                    keywords = [k.strip() for k in row.get('keywords', '').split(',') if k.strip()]
                    
                    if row.get('name') and websites:
                        new_company = {
                            "name": row['name'].strip(),
                            "sector": row.get('sector', 'Financial Services').strip(),
                            "websites": websites,
                            "keywords": keywords
                        }
                        new_companies.append(new_company)
            
            if new_companies:
                self.companies = new_companies
                self._save_companies(self.companies)
                logger.info(f"Imported {len(new_companies)} companies from CSV")
                return True
            else:
                logger.warning("No valid companies found in CSV file")
                return False
                
        except Exception as e:
            logger.error(f"Error importing from CSV: {e}")
            return False
    
    def export_to_csv(self, csv_file_path: str = "companies_export.csv") -> bool:
        """Export companies to CSV file"""
        try:
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'sector', 'websites', 'keywords']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for company in self.companies:
                    writer.writerow({
                        'name': company['name'],
                        'sector': company['sector'],
                        'websites': ','.join(company['websites']),
                        'keywords': ','.join(company.get('keywords', []))
                    })
            
            logger.info(f"Exported {len(self.companies)} companies to {csv_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def get_sample_csv_template(self) -> str:
        """Get a sample CSV template string"""
        return """name,sector,websites,keywords
"Apple Inc","Technology","https://www.apple.com/newsroom,https://developer.apple.com/news","AI,machine learning,iOS,innovation"
"Microsoft","Technology","https://news.microsoft.com,https://blogs.microsoft.com","artificial intelligence,Azure,cloud,AI"
"Google","Technology","https://blog.google,https://ai.googleblog.com","AI,machine learning,search,cloud"
"""