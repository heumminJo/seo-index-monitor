# SEO 인덱싱 및 분석 도구

사이트맵을 기반으로 웹 페이지의 검색 엔진 등록 상태를 확인하고 SEO 요소를 진단하는 도구입니다.

## 주요 기능
- **사이트맵 파싱**: XML 사이트맵(인덱스 사이트맵 포함)에서 URL을 자동으로 추출합니다.
- **인덱싱 체크**: Google, Naver, Bing에서 `site:` 쿼리를 사용하여 해당 URL의 등록 여부를 진단합니다.
- **SEO 상세 분석**: 미등록 사유를 파악하기 위해 HTTP 상태 코드, Title, Meta Description, H1, Canonical, Robots 설정을 크롤링합니다.
- **CSV 리포트**: 모든 분석 결과를 엑셀에서 확인 가능한 CSV 형식으로 내보냅니다.

## 설치 및 실행 방법

### 1. 가상환경 활성화 및 패키지 설치
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 도구 실행
```bash
python3 main.py
```
실행 후 안내에 따라 사이트맵 URL(예: `https://example.com/sitemap.xml`)을 입력하면 됩니다.

## 프로젝트 구조
- `main.py`: 전체 프로세스 제어 및 CSV 생성
- `sitemap_parser.py`: 사이트맵 추출 로직
- `index_checker.py`: 검색 엔진 인덱싱 확인 로직
- `seo_analyzer.py`: 개별 페이지 SEO 구성 요소 분석 로직

> [!CAUTION]
> **사용 시 주의사항**
> 검색 엔진의 `site:` 검색을 반복적으로 수행할 경우, 검색 엔진 측에서 봇으로 인식하여 일시적으로 IP를 차단할 수 있습니다. 본 도구에는 기본적인 딜레이 로직이 포함되어 있으나, 대량의 URL을 체크할 때는 주의가 필요합니다.
