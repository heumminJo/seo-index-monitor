import asyncio
import datetime
import csv
import os
from sitemap_parser import get_sitemap_urls
from index_checker import get_domain_from_url
from seo_analyzer import analyze_urls_async
from utils import CsvLogger, normalize_url
import sys

# Windows asyncio policy
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import json

HISTORY_FILE = "sitemap_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(url, history):
    if url in history:
        history.remove(url)
    history.insert(0, url) # 최신을 맨 앞으로
    # 최대 5개 유지
    history = history[:5]
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def main():
    print("="*60)
    print("SEO Indexing & Analysis Tool v2.2 (History Added)")
    print("="*60)
    
    # 히스토리 로드 및 표시
    history = load_history()
    sitemap_url = ""
    
    if history:
        print("\n[최근 사용한 사이트맵]")
        for idx, url in enumerate(history, 1):
            print(f" {idx}. {url}")
        print(" 0. 새로 입력")
        
        choice = input("\n번호를 선택하세요 (기본값: 1): ").strip()
        if not choice:
            choice = "1"
            
        if choice.isdigit() and 1 <= int(choice) <= len(history):
            sitemap_url = history[int(choice)-1]
        
    if not sitemap_url:
        sitemap_url = input("\n진단할 Sitemap URL을 입력하세요: ").strip()
        
    if not sitemap_url:
        print("URL이 입력되지 않았습니다.")
        return
        
    # 히스토리 저장
    save_history(sitemap_url, history)
        
    # 1. 사이트맵 파싱
    print(f"\n[1/4] 사이트맵 파싱 중...")
    target_urls = get_sitemap_urls(sitemap_url)
    total_urls = len(target_urls)
    print(f"발견된 URL: {total_urls}개")
    
    if total_urls == 0:
        return
        
    domain = get_domain_from_url(target_urls[0])
    
    # 2. 검색 엔진 크롤링 (Playwright 사용)
    print(f"\n[2/5] 검색 엔진 인덱싱 목록 수집 (Playwright 브라우저 사용)...")
    print(f"      * 실제 브라우저를 사용하므로 시간이 다소 걸릴 수 있습니다.")
    
    from index_checker import crawl_search_results_playwright
    
    # 네이버는 5페이지까지 (약 50개), Google/Bing은 3페이지 시도
    async def crawl_all_engines():
        naver = await crawl_search_results_playwright(f"https://{domain}", 'naver', max_pages=5)
        google = await crawl_search_results_playwright(f"https://{domain}", 'google', max_pages=3)
        bing = await crawl_search_results_playwright(f"https://{domain}", 'bing', max_pages=3)
        return naver, google, bing
    
    naver_urls, google_urls, bing_urls = asyncio.run(crawl_all_engines())
    
    print(f"\n  === 수집 결과 ===")
    print(f"  - Naver: {len(naver_urls)}개 {'✓' if naver_urls else '(수집 실패)'}")
    print(f"  - Google: {len(google_urls)}개 {'✓' if google_urls else '(캡차로 인해 수집 불가 - 수동 확인 필요)'}")
    print(f"  - Bing: {len(bing_urls)}개 {'✓' if bing_urls else '(수집 불가 - 수동 확인 필요)'}")
    
    # 비교를 위한 정규화 세트 생성
    google_norm = {normalize_url(u) for u in google_urls}
    naver_norm = {normalize_url(u) for u in naver_urls}
    bing_norm = {normalize_url(u) for u in bing_urls}
    
    # 3. CSV 저장 설정 (reports 폴더에 저장)
    REPORTS_DIR = "reports"
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(REPORTS_DIR, f"seo_report_{timestamp}.csv")
    # Bing 컬럼 추가
    fieldnames = ['URL', 'Google_Index', 'Naver_Index', 'Bing_Index', 'Status', 'Title', 'Issues']
    logger = CsvLogger(filename, fieldnames)
    
    print(f"\n[3/4] SEO 분석 및 결과 저장 중... ('{filename}')")
    
    # 결과 버퍼 (정렬용)
    results_buffer = []

    # 콜백 함수
    def on_analyze_complete(result):
        url = result['url']
        url_n = normalize_url(url)
        
        # 정확한 매칭을 위해 Set 조회 (`in` 연산자)
        is_google = "O" if url_n in google_norm else "X"
        is_naver = "O" if url_n in naver_norm else "X"
        is_bing = "O" if url_n in bing_norm else "X"
        
        row = {
            'URL': url,
            'Google_Index': is_google,
            'Naver_Index': is_naver,
            'Bing_Index': is_bing,
            'Status': result['status_code'],
            'Title': result['title'],
            'Issues': " | ".join(result['issues']) if result['issues'] else "None"
        }
        logger.log(row)
        results_buffer.append(row)
        
        # 콘솔 출력 개선 (인덱싱 상태 표시)
        idx_status = f"G:{is_google} N:{is_naver} B:{is_bing}"
        print(f"Checked: {url} [{result['status_code']}] [{idx_status}]")

    # 4. 실행
    asyncio.run(analyze_urls_async(target_urls, on_analyze_complete))
    
    # 5. 정렬된 결과 파일 생성 (상단에 요약 포함)
    print(f"\n[5/5] 인덱싱된 항목을 상단으로 정렬하여 별도 저장 중...")
    
    # 통계 계산
    total_urls = len(results_buffer)
    google_indexed = sum(1 for r in results_buffer if r['Google_Index'] == 'O')
    naver_indexed = sum(1 for r in results_buffer if r['Naver_Index'] == 'O')
    bing_indexed = sum(1 for r in results_buffer if r['Bing_Index'] == 'O')
    any_indexed = sum(1 for r in results_buffer if r['Google_Index'] == 'O' or r['Naver_Index'] == 'O' or r['Bing_Index'] == 'O')
    not_indexed = total_urls - any_indexed
    
    # 정렬
    results_buffer.sort(key=lambda r: ( 
        1 if (r['Google_Index']=='O' or r['Naver_Index']=='O' or r['Bing_Index']=='O') else 0 
    ), reverse=True)
    
    sorted_filename = os.path.join(REPORTS_DIR, f"seo_report_sorted_{timestamp}.csv")
    with open(sorted_filename, 'w', newline='', encoding='utf-8-sig') as f:
        # 요약 통계 헤더
        f.write("# ===== SEO 인덱싱 분석 리포트 =====\n")
        f.write(f"# 분석 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 대상 도메인: {domain}\n")
        f.write(f"# \n")
        f.write(f"# [요약 통계]\n")
        f.write(f"# 전체 URL 수: {total_urls}\n")
        f.write(f"# Google 인덱싱: {google_indexed}개 ({google_indexed/total_urls*100:.1f}%)\n")
        f.write(f"# Naver 인덱싱: {naver_indexed}개 ({naver_indexed/total_urls*100:.1f}%)\n")
        f.write(f"# Bing 인덱싱: {bing_indexed}개 ({bing_indexed/total_urls*100:.1f}%)\n")
        f.write(f"# 하나 이상 인덱싱: {any_indexed}개 ({any_indexed/total_urls*100:.1f}%)\n")
        f.write(f"# 미인덱싱: {not_indexed}개 ({not_indexed/total_urls*100:.1f}%)\n")
        f.write(f"# \n")
        f.write(f"# ===================================\n")
        f.write(f"# \n")
        
        # 데이터 헤더 및 내용
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_buffer)
    
    # 콘솔에도 요약 출력
    print(f"\n===== 분석 결과 요약 =====")
    print(f"전체 URL: {total_urls}개")
    print(f"Google 인덱싱: {google_indexed}개 ({google_indexed/total_urls*100:.1f}%)")
    print(f"Naver 인덱싱: {naver_indexed}개 ({naver_indexed/total_urls*100:.1f}%)")
    print(f"Bing 인덱싱: {bing_indexed}개 ({bing_indexed/total_urls*100:.1f}%)")
    print(f"미인덱싱: {not_indexed}개")
    print(f"\n모든 작업이 완료되었습니다!")
    print(f"1. 전체 로그(실시간): {filename}")
    print(f"2. 정렬된 리포트(추천): {sorted_filename}")
    print("="*60)

if __name__ == "__main__":
    main()
