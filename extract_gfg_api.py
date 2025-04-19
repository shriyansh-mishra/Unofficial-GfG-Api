import requests
import json
import sys

def get_profile_data(username):
    url = f'https://geeksforgeeks.org/api/user/{username}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': f'https://www.geeksforgeeks.org/user/{username}/'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching API data: {str(e)}")
        return None

