import requests
import json
import re
from bs4 import BeautifulSoup

def extract_next_data(username):
    url = f'https://www.geeksforgeeks.org/user/{username}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Extract JSON data from Next.js script tag
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text, re.DOTALL)
        if match:
            json_data = match.group(1)
            data = json.loads(json_data)
            return data
        else:
            print("Couldn't find Next.js data in the page")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

