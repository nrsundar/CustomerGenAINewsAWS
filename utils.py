"""
Utility functions for GenAI Content Monitor
Common helper functions and logging setup
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

def setup_logging(level: str = None, log_file: str = None):
    """Setup logging configuration"""
    
    # Get log level from environment or parameter
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Convert string level to logging level
    numeric_level = getattr(logging, level, logging.INFO)
    
    # Create logs directory if needed
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    else:
        log_file = os.getenv("LOG_FILE", "logs/genai_monitor.log")
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Setup logging with both file and console handlers
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at {level} level")
    logger.info(f"Log file: {log_file}")

def validate_url(url: str) -> bool:
    """Validate if a URL is properly formatted"""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Replace multiple whitespaces with single space
    import re
    text = re.sub(r'\s+', ' ', text)
    
    # Remove excessive newlines
    text = re.sub(r'\n+', '\n', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text

def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def get_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    except Exception:
        return "unknown"

def ensure_directory_exists(directory: str):
    """Ensure a directory exists, create if it doesn't"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def load_config_from_file(config_file: str) -> dict:
    """Load configuration from JSON file"""
    try:
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.getLogger(__name__).error(f"Error loading config file {config_file}: {e}")
        return {}

def save_config_to_file(config: dict, config_file: str):
    """Save configuration to JSON file"""
    try:
        import json
        ensure_directory_exists(os.path.dirname(config_file))
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.getLogger(__name__).error(f"Error saving config file {config_file}: {e}")

def check_internet_connection(url: str = "https://www.google.com", timeout: int = 5) -> bool:
    """Check if internet connection is available"""
    try:
        import requests
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False

def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
    """Retry a function on failure with exponential backoff"""
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = delay * (2 ** attempt)
            logging.getLogger(__name__).warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
    """Mask sensitive data for logging"""
    if not data or len(data) <= 4:
        return mask_char * len(data) if data else ""
    
    # Show first 2 and last 2 characters
    return data[:2] + mask_char * (len(data) - 4) + data[-2:]
