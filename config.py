# 설정 관리 파일

# 봇 탐지 회피를 위한 User-Agent 리스트
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
]

# 타임아웃 설정 (초)
TIMEOUT = 10

# 검색 엔진 설정
ENGINES = {
    'google': {
        'url': 'https://www.google.com/search?q=site:{}&start={}',
        'result_selector': '#search .g a', # 검색 결과 링크 셀렉터 (변경 가능성 있음)
    },
    'naver': {
        'url': 'https://search.naver.com/search.naver?query=site:{}&start={}', # 네이버는 start 파라미터가 다를 수 있음 (1, 11, 21...)
        'result_selector': '.sc_new a.link_tit',
    },
    'bing': {
        'url': 'https://www.bing.com/search?q=site:{}&first={}',
        'result_selector': '#b_results li.b_algo h2 a',
    }
}

# 비동기 동시 요청 제한
CONCURRENT_REQUESTS = 10
