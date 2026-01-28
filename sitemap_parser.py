import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_sitemap_urls(sitemap_url):
    """
    사이트맵 URL을 입력받아 모든 하위 URL 목록을 반환합니다.
    인덱스 사이트맵(다른 사이트맵을 포함하는 경우) 처리 로직이 포함되어 있습니다.
    """
    urls = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(sitemap_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml-xml')
        
        # 1. 인덱스 사이트맵인 경우 (<sitemap> 태그 확인)
        sitemaps = soup.find_all('sitemap')
        if sitemaps:
            for sitemap in sitemaps:
                loc = sitemap.find('loc')
                if loc:
                    urls.extend(get_sitemap_urls(loc.text))
        
        # 2. 일반 URL인 경우 (<url> 태그 확인)
        url_tags = soup.find_all('url')
        for url_tag in url_tags:
            loc = url_tag.find('loc')
            if loc:
                urls.append(loc.text)
                
        # 3. 만약 위 형식이 아니고 단순 XML 태그 <loc>만 있는 경우 대응
        if not sitemaps and not url_tags:
            locs = soup.find_all('loc')
            for loc in locs:
                urls.append(loc.text)
                
    except Exception as e:
        print(f"Error parsing sitemap {sitemap_url}: {e}")
        
    return list(set(urls)) # 중복 제거

if __name__ == "__main__":
    # 테스트 코드
    test_url = input("Enter Sitemap URL to test: ")
    found_urls = get_sitemap_urls(test_url)
    print(f"Found {len(found_urls)} URLs.")
    for u in found_urls[:10]:
        print(f"- {u}")
