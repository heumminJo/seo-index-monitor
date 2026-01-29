import aiohttp
import asyncio
from bs4 import BeautifulSoup
from config import TIMEOUT, CONCURRENT_REQUESTS
from utils import get_random_header

async def fetch_and_analyze(session, url):
    """
    비동기로 URL을 가져와서 SEO 요소를 분석합니다.
    """
    results = {
        'url': url,
        'status_code': 0,
        'title': '',
        'description': '',
        'h1': [],
        'canonical': '',
        'robots': '',
        'issues': []
    }
    
    try:
        async with session.get(url, headers=get_random_header(), timeout=TIMEOUT, ssl=False) as response:
            results['status_code'] = response.status
            
            if response.status != 200:
                results['issues'].append(f"HTTP Status {response.status}")
                return results
            
            content = await response.read()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Title
            title_tag = soup.find('title')
            results['title'] = title_tag.text.strip() if title_tag else "Missing"
            if not title_tag:
                results['issues'].append("Missing Title tag")
            elif len(results['title']) < 10:
                results['issues'].append("Title too short")
                
            # Meta Description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag:
                results['description'] = desc_tag.get('content', '').strip()
            if not results['description']:
                results['issues'].append("Missing Meta Description")
                
            # H1 Tag
            h1_tags = soup.find_all('h1')
            results['h1'] = [h.text.strip() for h in h1_tags]
            if len(h1_tags) == 0:
                results['issues'].append("Missing H1 tag")
            elif len(h1_tags) > 1:
                results['issues'].append("Multiple H1 tags")
                
            # Canonical
            canonical_tag = soup.find('link', rel='canonical')
            if canonical_tag:
                results['canonical'] = canonical_tag.get('href', '')
            if not results['canonical']:
                results['issues'].append("Missing Canonical tag")
                
            # Robots Meta
            robots_tag = soup.find('meta', attrs={'name': 'robots'})
            if robots_tag:
                results['robots'] = robots_tag.get('content', '').lower()
                if 'noindex' in results['robots']:
                    results['issues'].append("Meta robots set to 'noindex'")

    except Exception as e:
        results['issues'].append(f"Async Crawl Error: {str(e)}")
        
    return results

async def analyze_urls_async(urls, update_callback=None):
    """
    여러 URL을 비동기로 동시에 분석합니다.
    update_callback: 처리 완료 시 호출될 콜백 함수 (중간 저장용)
    """
    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for url in urls:
            tasks.append(process_url(session, url, update_callback))
        
        return await asyncio.gather(*tasks)

async def process_url(session, url, update_callback):
    result = await fetch_and_analyze(session, url)
    if update_callback:
        update_callback(result)
    return result

if __name__ == "__main__":
    # Test code
    test_urls = ["https://www.python.org", "https://docs.python.org/3/"]
    
    async def run_test():
        res = await analyze_urls_async(test_urls, lambda x: print(f"Done: {x['url']}"))
        print(f"Total processed: {len(res)}")
        
    asyncio.run(run_test())
