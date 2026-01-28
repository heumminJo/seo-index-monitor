import requests
from bs4 import BeautifulSoup
import time
import random

def check_indexing(url, engine='google'):
    """
    특정 검색 엔진에서 해당 URL의 인덱싱 여부를 간단히 체크합니다.
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    ]
    
    headers = {'User-Agent': random.choice(user_agents)}
    
    # 검색 쿼리: site:[URL]
    if engine == 'google':
        search_url = f"https://www.google.com/search?q=site:{url}"
    elif engine == 'naver':
        search_url = f"https://search.naver.com/search.naver?query=site:{url}"
    elif engine == 'bing':
        search_url = f"https://www.bing.com/search?q=site:{url}"
    else:
        return "Unknown Engine"

    try:
        # 봇 탐지 회피를 위한 랜덤 딜레이 (개인 사용 시 주의)
        time.sleep(random.uniform(1.0, 3.0))
        
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 엔진별 인덱싱 판단 로직 (간단한 검색 결과 텍스트 확인)
        indexed = False
        if engine == 'google':
            # "검색결과가 없습니다" 또는 유사한 문구가 없으면 인덱싱된 것으로 간주
            if "did not match any documents" not in response.text and "결과가 없습니다" not in response.text:
                # 구글은 보통 결과 리스트가 있으면 인덱싱된 것
                if soup.find('div', id='search'):
                    indexed = True
        elif engine == 'naver':
            if "결과가 없습니다" not in response.text and soup.find('section', class_='sc_new'):
                indexed = True
        elif engine == 'bing':
            if "No results found" not in response.text and soup.find('ol', id='b_results'):
                indexed = True
                
        return "Indexed" if indexed else "Not Indexed"

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    test_url = "https://www.google.com"
    print(f"Google: {check_indexing(test_url, 'google')}")
    print(f"Naver: {check_indexing(test_url, 'naver')}")
    print(f"Bing: {check_indexing(test_url, 'bing')}")
