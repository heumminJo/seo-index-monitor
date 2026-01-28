import requests
from bs4 import BeautifulSoup

def analyze_seo(url):
    """
    페이지를 크롤링하여 주요 SEO 요소를 분석합니다.
    """
    results = {
        'status_code': 0,
        'title': '',
        'description': '',
        'h1': [],
        'canonical': '',
        'robots': '',
        'issues': []
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        results['status_code'] = response.status_code
        
        if response.status_code != 200:
            results['issues'].append(f"HTTP Status {response.status_code}")
            return results
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
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
        results['issues'].append(f"Crawl Error: {str(e)}")
        
    return results

if __name__ == "__main__":
    test_url = "https://www.python.org"
    print(analyze_seo(test_url))
