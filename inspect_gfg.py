import requests
from bs4 import BeautifulSoup

def inspect_profile(username):
    url = f'https://www.geeksforgeeks.org/user/{username}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check if there's a script tag with __NEXT_DATA__
    next_data = None
    for script in soup.find_all('script'):
        if script.get('id') == '__NEXT_DATA__':
            next_data = script
            break
    
    print(f"Script with __NEXT_DATA__: {'Found' if next_data else 'Not found'}")
    
    # Look for user profile elements
    print("\nSearching for profile data elements:")
    profile_sections = soup.select('.dashboard_profileInfo__UooCB')
    print(f"Profile sections: {len(profile_sections)}")
    
    # Find rank stats
    rank_elements = soup.select('.dashboard_rankStats__cJuUW .dashboard_stats__c5VGW')
    print(f"Rank elements: {len(rank_elements)}")
    for i, el in enumerate(rank_elements):
        number = el.select_one('.dashboard_number__GN7Cz')
        label = el.select_one('.dashboard_label__EnMMw')
        if number and label:
            print(f"  {i+1}. {label.text.strip()}: {number.text.strip()}")
    
    # Find problems solved
    problems_solved = soup.select('.dashboard_problemSolvedCount__vJH3A')
    print(f"\nProblems solved elements: {len(problems_solved)}")
    for i, el in enumerate(problems_solved):
        num = el.select_one('.dashboard_number__GN7Cz')
        label = el.select_one('.dashboard_label__EnMMw')
        if num and label:
            print(f"  {i+1}. {label.text.strip()}: {num.text.strip()}")
    
    # Find problem difficulty breakdown
    difficulty_elements = soup.select('.dashboard_problemDiff__KGuQ6 .dashboard_difficultyBlock__U_6f3')
    print(f"\nDifficulty breakdown elements: {len(difficulty_elements)}")
    for i, el in enumerate(difficulty_elements):
        diff_name = el.select_one('.dashboard_name__Sfa59')
        diff_count = el.select_one('.dashboard_count__Mm2dD')
        if diff_name and diff_count:
            print(f"  {i+1}. {diff_name.text.strip()}: {diff_count.text.strip()}")


