import re
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In-memory rate limiting storage
# Format: {ip_address: [timestamp1, timestamp2, ...]}
rate_limit_storage = {}
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 10  # max requests per window

def validate_username(username):
    """
    Validate the GeeksforGeeks username.
    
    Args:
        username (str): The username to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not username:
        logger.warning("Empty username provided")
        return False
    
    # GeeksforGeeks usernames typically follow a pattern
    # They are alphanumeric and may contain underscore, hyphen
    # Length should be reasonable
    if not isinstance(username, str):
        logger.warning(f"Username not a string: {type(username)}")
        return False
    
    if len(username) < 3 or len(username) > 50:
        logger.warning(f"Username length invalid: {len(username)}")
        return False
    
    # Check username format
    pattern = r'^[a-zA-Z0-9_\-]+$'
    if not re.match(pattern, username):
        logger.warning(f"Username format invalid: {username}")
        return False
    
    return True

def is_rate_limited(ip_address):
    """
    Check if the request from the IP address is rate limited.
    
    Args:
        ip_address (str): The IP address of the request
        
    Returns:
        bool: True if rate limited, False otherwise
    """
    current_time = time.time()
    
    # Initialize if IP not in storage
    if ip_address not in rate_limit_storage:
        rate_limit_storage[ip_address] = []
    
    # Clean up old timestamps
    rate_limit_storage[ip_address] = [
        ts for ts in rate_limit_storage[ip_address]
        if ts > current_time - RATE_LIMIT_WINDOW
    ]
    
    # Check if rate limit exceeded
    if len(rate_limit_storage[ip_address]) >= MAX_REQUESTS_PER_WINDOW:
        logger.warning(f"Rate limit exceeded for IP: {ip_address}")
        return True
    
    # Add current timestamp
    rate_limit_storage[ip_address].append(current_time)
    
    # Clean up storage periodically (remove IPs with empty lists)
    if current_time % 300 < 1:  # Run cleanup roughly every 5 minutes
        cleanup_rate_limit_storage()
    
    return False

def cleanup_rate_limit_storage():
    """Clean up the rate limit storage by removing IPs with empty timestamp lists"""
    global rate_limit_storage
    rate_limit_storage = {ip: timestamps for ip, timestamps in rate_limit_storage.items() if timestamps}
    logger.debug(f"Rate limit storage cleaned up. Current size: {len(rate_limit_storage)}")

def parse_html_text(html_text):
    """
    Parse text from HTML and clean it up.
    
    Args:
        html_text (str): The HTML text to parse
        
    Returns:
        str: Cleaned text
    """
    if not html_text:
        return None
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', html_text).strip()
    
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    
    return text

def format_date(date_string):
    """
    Format date string to a standard format.
    
    Args:
        date_string (str): Date string to format
        
    Returns:
        str: Formatted date string or None if invalid
    """
    if not date_string:
        return None
    
    try:
        # Try various date formats
        formats = [
            '%d %b %Y',  # 01 Jan 2023
            '%d-%m-%Y',  # 01-01-2023
            '%Y-%m-%d',  # 2023-01-01
            '%B %d, %Y',  # January 01, 2023
            '%d/%m/%Y',  # 01/01/2023
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_string.strip(), fmt)
                return dt.strftime('%Y-%m-%d')  # Standard ISO format
            except ValueError:
                continue
        
        # If no format matches, return the original string
        return date_string.strip()
    
    except Exception as e:
        logger.error(f"Error formatting date '{date_string}': {str(e)}")
        return date_string
