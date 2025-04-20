import re
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

rate_limit_storage = {}
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 10  # max requests

def validate_username(username):
    
    if not username:
        logger.warning("Empty username provided")
        return False
    
    if not isinstance(username, str):
        logger.warning(f"Username not a string: {type(username)}")
        return False
    
    if len(username) < 3 or len(username) > 50:
        logger.warning(f"Username length invalid: {len(username)}")
        return False
    
    pattern = r'^[a-zA-Z0-9_\-]+$'
    if not re.match(pattern, username):
        logger.warning(f"Username format invalid: {username}")
        return False
    
    return True

def is_rate_limited(ip_address):
    
    current_time = time.time()
    
    if ip_address not in rate_limit_storage:
        rate_limit_storage[ip_address] = []
    
    rate_limit_storage[ip_address] = [
        ts for ts in rate_limit_storage[ip_address]
        if ts > current_time - RATE_LIMIT_WINDOW
    ]
    
    # Check if rate limit exceeded
    if len(rate_limit_storage[ip_address]) >= MAX_REQUESTS_PER_WINDOW:
        logger.warning(f"Rate limit exceeded for IP: {ip_address}")
        return True
    
    rate_limit_storage[ip_address].append(current_time)
    
    if current_time % 300 < 1:  
        cleanup_rate_limit_storage()
    
    return False

def cleanup_rate_limit_storage():
    global rate_limit_storage
    rate_limit_storage = {ip: timestamps for ip, timestamps in rate_limit_storage.items() if timestamps}
    logger.debug(f"Rate limit storage cleaned up. Current size: {len(rate_limit_storage)}")

def parse_html_text(html_text):
    
    if not html_text:
        return None
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', html_text).strip()
    
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    
    return text

def format_date(date_string):
    
    if not date_string:
        return None
    
    try:
        formats = [
            '%d %b %Y',  
            '%d-%m-%Y', 
            '%Y-%m-%d', 
            '%B %d, %Y', 
            '%d/%m/%Y',  
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_string.strip(), fmt)
                return dt.strftime('%Y-%m-%d') 
            except ValueError:
                continue
        
        return date_string.strip()
    
    except Exception as e:
        logger.error(f"Error formatting date '{date_string}': {str(e)}")
        return date_string
