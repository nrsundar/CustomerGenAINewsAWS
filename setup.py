#!/usr/bin/env python3
"""
Setup script for GenAI Content Monitor
Handles initial setup, configuration, and testing
"""

import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

def create_directory_structure():
    """Create necessary directories"""
    directories = ['logs', 'data']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            # Copy example file
            with open('.env.example', 'r') as source:
                content = source.read()
            with open('.env', 'w') as target:
                target.write(content)
            print("✓ Created .env file from template")
            print("⚠️  Please edit .env file with your configuration")
            return False
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✓ .env file already exists")
        return True

def validate_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'beautifulsoup4', 'requests', 'transformers', 'torch', 
        'schedule', 'python-dotenv', 'trafilatura', 'lxml', 'html5lib'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✓ All required packages are installed")
    return True

def validate_configuration():
    """Validate configuration settings"""
    load_dotenv()
    
    required_vars = ['EMAIL_USERNAME', 'EMAIL_PASSWORD', 'EMAIL_RECIPIENT']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"❌ {var} not configured")
        else:
            print(f"✓ {var} configured")
    
    if missing_vars:
        print(f"\n⚠️  Missing required configuration: {', '.join(missing_vars)}")
        print("Please edit .env file with your settings")
        return False
    
    return True

def test_email_configuration():
    """Test email configuration"""
    try:
        from config import Config
        from email_sender import EmailSender
        
        config = Config()
        sender = EmailSender(config)
        
        print("Testing email configuration...")
        
        # Try to create SMTP connection
        import smtplib
        with smtplib.SMTP(config.EMAIL_SMTP_SERVER, config.EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
        
        print("✓ Email configuration is valid")
        
        # Ask if user wants to send test email
        response = input("Send test email? (y/N): ").lower().strip()
        if response == 'y':
            if sender.send_test_email():
                print("✓ Test email sent successfully")
            else:
                print("❌ Failed to send test email")
        
        return True
        
    except Exception as e:
        print(f"❌ Email configuration test failed: {e}")
        return False

def test_ai_models():
    """Test AI model loading"""
    try:
        from config import Config
        from ai_processor import AIProcessor
        
        config = Config()
        processor = AIProcessor(config)
        
        # Test with sample content
        test_content = "This article discusses the latest developments in ChatGPT and large language models for generative AI applications."
        
        is_genai = processor.is_genai_related(test_content)
        print(f"✓ GenAI classification test: {is_genai}")
        
        if processor.summarizer:
            summary = processor.summarize_article(test_content)
            print(f"✓ Summarization test: {summary[:50]}...")
        else:
            print("⚠️  Summarization model not loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ AI model test failed: {e}")
        return False

def test_web_scraping():
    """Test web scraping functionality"""
    try:
        from config import Config
        from scraper import WebScraper
        
        config = Config()
        scraper = WebScraper(config)
        
        # Test with a simple website
        test_url = "https://httpbin.org/html"
        print(f"Testing web scraping with: {test_url}")
        
        articles = scraper.scrape_articles(test_url)
        print(f"✓ Web scraping test completed (found {len(articles)} articles)")
        
        return True
        
    except Exception as e:
        print(f"❌ Web scraping test failed: {e}")
        return False

def run_sample_monitoring():
    """Run a sample monitoring cycle"""
    try:
        print("Running sample monitoring cycle...")
        from main import main
        main()
        print("✓ Sample monitoring completed successfully")
        return True
    except Exception as e:
        print(f"❌ Sample monitoring failed: {e}")
        return False

def main():
    """Main setup function"""
    print("GenAI Content Monitor - Setup Script")
    print("=" * 40)
    
    # Step 1: Create directories
    print("\n1. Creating directory structure...")
    create_directory_structure()
    
    # Step 2: Create .env file
    print("\n2. Setting up configuration...")
    env_exists = create_env_file()
    
    # Step 3: Check dependencies
    print("\n3. Checking dependencies...")
    deps_ok = validate_dependencies()
    
    if not deps_ok:
        print("\n❌ Setup incomplete. Please install missing dependencies.")
        return False
    
    if not env_exists:
        print("\n⚠️  Please configure .env file and run setup again.")
        return False
    
    # Step 4: Validate configuration
    print("\n4. Validating configuration...")
    config_ok = validate_configuration()
    
    if not config_ok:
        print("\n❌ Setup incomplete. Please configure required settings.")
        return False
    
    # Step 5: Test components
    print("\n5. Testing email configuration...")
    email_ok = test_email_configuration()
    
    print("\n6. Testing AI models...")
    ai_ok = test_ai_models()
    
    print("\n7. Testing web scraping...")
    scraping_ok = test_web_scraping()
    
    # Summary
    print("\n" + "=" * 40)
    print("SETUP SUMMARY")
    print("=" * 40)
    
    if all([deps_ok, config_ok, email_ok, ai_ok, scraping_ok]):
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python main.py (single check)")
        print("2. Run: python scheduler.py daily (automated)")
        print("3. Check logs/ directory for detailed output")
        
        # Offer to run sample
        response = input("\nRun sample monitoring now? (y/N): ").lower().strip()
        if response == 'y':
            run_sample_monitoring()
        
        return True
    else:
        print("⚠️  Setup completed with issues. Check failed components above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
