import csv
from sitemap_parser import get_sitemap_urls
from index_checker import check_indexing
from seo_analyzer import analyze_seo
import datetime
import os

def main():
    print("="*50)
    print("SEO Indexing & Analysis Tool")
    print("="*50)
    
    sitemap_url = input("진단할 Sitemap URL을 입력하세요: ").strip()
    if not sitemap_url:
        print("URL이 입력되지 않았습니다.")
        return
        
    print(f"\n[1/4] 사이트맵에서 URL을 추출 중입니다...")
    urls = get_sitemap_urls(sitemap_url)
    total = len(urls)
    print(f"총 {total}개의 URL을 발견했습니다.")
    
    if total == 0:
        return
        
    # 결과 저장용 리스트
    report_data = []
    
    print(f"\n[2/4] 각 URL의 인덱싱 및 SEO 상태를 분석합니다. (약간의 시간이 소요될 수 있습니다)")
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{total}] 처리 중: {url}")
        
        # 1. 인덱싱 체크
        google_idx = check_indexing(url, 'google')
        naver_idx = check_indexing(url, 'naver')
        bing_idx = check_indexing(url, 'bing')
        
        # 2. SEO 분석 (인덱싱 안 된 경우만 상세 분석하거나 전체 분석할 수 있음 - 여기서는 전체 실행)
        seo_res = analyze_seo(url)
        
        report_data.append({
            'URL': url,
            'Google': google_idx,
            'Naver': naver_idx,
            'Bing': bing_idx,
            'Status': seo_res['status_code'],
            'Title': seo_res['title'],
            'Issues': " | ".join(seo_res['issues']) if seo_res['issues'] else "None"
        })
        
    # 3. CSV 리포트 생성
    print(f"\n[3/4] 리포트 파일 생성 중...")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"seo_report_{timestamp}.csv"
    
    keys = report_data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(report_data)
        
    print(f"\n[4/4] 완료!")
    print(f"결과가 '{filename}'에 저장되었습니다.")
    print("="*50)

if __name__ == "__main__":
    main()
