"""
Playwright 기반 검색 엔진 인덱싱 체커 v5
- Firefox 사용 (탐지율 낮음)
- headless=False 옵션 (실제 브라우저 창)
- 마우스 움직임 시뮬레이션
- 더 긴 랜덤 딜레이
"""
import asyncio
import re
import os
import random
from urllib.parse import urlparse, unquote
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from utils import normalize_url

# 디버그 폴더
DEBUG_DIR = "debug_screenshots"
PROFILE_DIR = "browser_profile"
os.makedirs(DEBUG_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)

# headless 모드 설정 (False로 하면 실제 브라우저 창이 보임)
HEADLESS_MODE = False  # 실제 브라우저 창 표시 - 캡차 직접 풀기 가능

def get_domain_from_url(url):
    parsed = urlparse(url)
    return parsed.netloc

async def human_delay(min_sec=2, max_sec=5):
    """사람처럼 랜덤한 딜레이"""
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def random_mouse_move(page):
    """마우스를 랜덤하게 움직여서 사람처럼 보이게"""
    try:
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))
    except:
        pass

async def human_scroll(page):
    """사람처럼 스크롤"""
    try:
        for _ in range(random.randint(1, 3)):
            scroll_amount = random.randint(100, 300)
            await page.mouse.wheel(0, scroll_amount)
            await asyncio.sleep(random.uniform(0.3, 0.8))
    except:
        pass

async def crawl_google_firefox(target_url, max_pages=3):
    """
    Google 검색 - Firefox 사용 (탐지율 낮음)
    """
    domain = get_domain_from_url(target_url)
    target_host = normalize_url(domain)
    indexed_urls = set()
    
    print(f"[Firefox] Google에서 site:{domain} 검색 중...")
    
    async with async_playwright() as p:
        # Firefox 사용 (Chrome보다 탐지 어려움)
        browser = await p.firefox.launch(
            headless=HEADLESS_MODE,
            firefox_user_prefs={
                "dom.webdriver.enabled": False,
                "useAutomationExtension": False,
            }
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='ko-KR',
            timezone_id='Asia/Seoul',
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        )
        
        page = await context.new_page()
        
        try:
            for page_num in range(max_pages):
                print(f"  Page {page_num + 1} 로딩 중...")
                
                if page_num == 0:
                    # 구글 메인 페이지 방문
                    await page.goto("https://www.google.com", wait_until='networkidle', timeout=30000)
                    await human_delay(2, 4)
                    await random_mouse_move(page)
                    
                    # 검색창 찾기 및 클릭
                    search_box = page.locator('textarea[name="q"], input[name="q"]').first
                    await search_box.click()
                    await human_delay(0.5, 1.5)
                    
                    # 사람처럼 천천히 타이핑
                    query = f"site:{domain}"
                    for char in query:
                        await page.keyboard.type(char, delay=random.randint(80, 200))
                        if random.random() < 0.1:  # 10% 확률로 잠시 멈춤
                            await asyncio.sleep(random.uniform(0.2, 0.5))
                    
                    await human_delay(1, 2)
                    await random_mouse_move(page)
                    
                    # 엔터 대신 검색 버튼 클릭 시도
                    try:
                        search_btn = page.locator('input[name="btnK"]').first
                        await search_btn.click()
                    except:
                        await page.keyboard.press('Enter')
                    
                    await page.wait_for_load_state('networkidle')
                else:
                    start = page_num * 10
                    await page.goto(f"https://www.google.com/search?q=site:{domain}&start={start}&hl=ko", 
                                   wait_until='networkidle', timeout=30000)
                
                await human_delay(3, 6)
                await random_mouse_move(page)
                await human_scroll(page)
                
                # 스크린샷 저장
                await page.screenshot(path=f"{DEBUG_DIR}/google_firefox_p{page_num+1}.png")
                
                content = await page.content()
                
                # 캡차 감지
                if 'recaptcha' in content.lower() or '로봇이 아닙니다' in content or 'unusual traffic' in content.lower():
                    print(f"  [!] 캡차 감지됨")
                    if not HEADLESS_MODE:
                        print(f"  [!] 브라우저 창에서 캡차를 직접 풀어주세요...")
                        await asyncio.sleep(30)  # 캡차 풀 시간 제공
                        content = await page.content()
                    else:
                        break
                
                # 링크 추출
                count = 0
                try:
                    all_links = await page.locator(f'a[href*="{domain}"]').all()
                    for link in all_links:
                        href = await link.get_attribute('href')
                        if href and href.startswith('http'):
                            if '/url?q=' in href:
                                try:
                                    href = href.split('/url?q=')[1].split('&')[0]
                                    href = unquote(href)
                                except:
                                    continue
                            
                            link_norm = normalize_url(href)
                            if target_host in link_norm and 'google' not in href:
                                indexed_urls.add(href)
                                count += 1
                except Exception as e:
                    print(f"  [!] 링크 추출 에러: {e}")
                
                print(f"  Page {page_num + 1}: {count}개 발견 (누적: {len(indexed_urls)}개)")
                
                if count == 0 and page_num > 0:
                    break
                
                await human_delay(4, 8)
                
        except Exception as e:
            print(f"  [!] Google 크롤링 에러: {e}")
        finally:
            await browser.close()
    
    return indexed_urls

async def crawl_bing_firefox(target_url, max_pages=3):
    """
    Bing 검색 - Firefox 사용
    """
    domain = get_domain_from_url(target_url)
    target_host = normalize_url(domain)
    indexed_urls = set()
    
    print(f"[Firefox] Bing에서 site:{domain} 검색 중...")
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=HEADLESS_MODE,
            firefox_user_prefs={
                "dom.webdriver.enabled": False,
            }
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='ko-KR',
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        )
        
        page = await context.new_page()
        
        try:
            for page_num in range(max_pages):
                print(f"  Page {page_num + 1} 로딩 중...")
                
                if page_num == 0:
                    await page.goto("https://www.bing.com", wait_until='networkidle', timeout=30000)
                    await human_delay(2, 4)
                    await random_mouse_move(page)
                    
                    search_box = page.locator('textarea[name="q"], input[name="q"]').first
                    await search_box.click()
                    await human_delay(0.5, 1)
                    
                    query = f"site:{domain}"
                    for char in query:
                        await page.keyboard.type(char, delay=random.randint(80, 200))
                    
                    await human_delay(1, 2)
                    await page.keyboard.press('Enter')
                    await page.wait_for_load_state('networkidle')
                else:
                    start = page_num * 10 + 1
                    await page.goto(f"https://www.bing.com/search?q=site:{domain}&first={start}", 
                                   wait_until='networkidle', timeout=30000)
                
                await human_delay(3, 5)
                await random_mouse_move(page)
                await human_scroll(page)
                
                await page.screenshot(path=f"{DEBUG_DIR}/bing_firefox_p{page_num+1}.png")
                
                content = await page.content()
                
                # 차단 감지
                if '마지막 한 단계' in content or 'captcha' in content.lower() or 'verify' in content.lower():
                    print(f"  [!] Bing 인증 요구됨")
                    if not HEADLESS_MODE:
                        print(f"  [!] 브라우저 창에서 인증을 완료해주세요...")
                        await asyncio.sleep(30)
                        content = await page.content()
                    else:
                        break
                
                count = 0
                try:
                    all_links = await page.locator(f'a[href*="{domain}"]').all()
                    for link in all_links:
                        href = await link.get_attribute('href')
                        if href and href.startswith('http'):
                            link_norm = normalize_url(href)
                            if target_host in link_norm and 'bing' not in href and 'microsoft' not in href:
                                indexed_urls.add(href)
                                count += 1
                except Exception as e:
                    print(f"  [!] 링크 추출 에러: {e}")
                
                print(f"  Page {page_num + 1}: {count}개 발견 (누적: {len(indexed_urls)}개)")
                
                if count == 0 and page_num > 0:
                    break
                
                await human_delay(3, 6)
                
        except Exception as e:
            print(f"  [!] Bing 크롤링 에러: {e}")
        finally:
            await browser.close()
    
    return indexed_urls

async def crawl_naver_playwright(target_url, max_pages=5):
    """
    네이버 검색 (기존과 동일)
    """
    domain = get_domain_from_url(target_url)
    target_host = normalize_url(domain)
    indexed_urls = set()
    
    print(f"[Playwright] Naver에서 site:{domain} 검색 중...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 900},
            locale='ko-KR',
            timezone_id='Asia/Seoul'
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        
        page = await context.new_page()
        
        try:
            for page_num in range(max_pages):
                start = page_num * 10 + 1
                search_url = f"https://search.naver.com/search.naver?where=web&query=site:{domain}&start={start}"
                
                await page.goto(search_url, wait_until='networkidle', timeout=30000)
                await human_delay(1.5, 3)
                
                await page.screenshot(path=f"{DEBUG_DIR}/naver_page{page_num+1}.png")
                
                content = await page.content()
                
                if '검색결과가 없습니다' in content or '일치하는 검색결과가 없습니다' in content:
                    print(f"  Page {page_num + 1}: 검색 결과 끝")
                    break
                
                found_links = set()
                
                try:
                    all_links = await page.locator(f'a[href*="{domain}"]').all()
                    for link in all_links:
                        href = await link.get_attribute('href')
                        if href and href.startswith('http'):
                            found_links.add(href)
                except Exception as e:
                    print(f"  [!] 셀렉터 에러: {e}")
                
                regex_links = re.findall(rf'href=["\']([^"\']*{re.escape(domain)}[^"\']*)["\']', content)
                for href in regex_links:
                    if href.startswith('http'):
                        found_links.add(href)
                
                count = 0
                for href in found_links:
                    try:
                        href = unquote(href)
                    except:
                        pass
                    
                    if not href.startswith('http'):
                        continue
                    
                    if 'naver.com' in href and domain not in href:
                        continue
                    
                    link_norm = normalize_url(href)
                    if target_host in link_norm:
                        indexed_urls.add(href)
                        count += 1
                
                print(f"  Page {page_num + 1}: {count}개 발견 (누적: {len(indexed_urls)}개)")
                
                if count == 0:
                    break
                    
                await human_delay(1, 2)
                
        except Exception as e:
            print(f"  [!] Naver 크롤링 에러: {e}")
        finally:
            await browser.close()
    
    return indexed_urls

# 통합 함수
async def crawl_search_results_playwright(target_url, engine='google', max_pages=3):
    if engine == 'naver':
        return await crawl_naver_playwright(target_url, max_pages)
    elif engine == 'google':
        return await crawl_google_firefox(target_url, max_pages)
    elif engine == 'bing':
        return await crawl_bing_firefox(target_url, max_pages)
    return set()

if __name__ == "__main__":
    async def test():
        domain = "calculkorea.com"
        
        print("\n=== Google Firefox 테스트 ===")
        google_urls = await crawl_google_firefox(f"https://{domain}", max_pages=2)
        print(f"Google 발견: {len(google_urls)}개")
        for url in list(google_urls)[:5]:
            print(f"  - {url}")
    
    asyncio.run(test())
