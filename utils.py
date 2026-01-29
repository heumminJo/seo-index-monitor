import csv
import os
import random
from urllib.parse import urlparse
from config import USER_AGENTS

def get_random_header():
    return {'User-Agent': random.choice(USER_AGENTS)}

def normalize_url(url):
    """
    URL 비교를 위해 정규화합니다.
    - http/https 제거
    - www. 제거
    - 끝의 / 제거
    """
    if not url:
        return ""
    
    # 1. Scheme 제거
    url = url.replace('https://', '').replace('http://', '')
    # 2. www. 제거
    url = url.replace('www.', '')
    # 3. 끝의 슬래시 제거
    if url.endswith('/'):
        url = url[:-1]
        
    return url

class CsvLogger:
    def __init__(self, filename, fieldnames):
        self.filename = filename
        self.fieldnames = fieldnames
        self.initialized = False
        
        # 파일이 이미 존재하면 헤더를 쓰지 않음
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            self.initialized = True

    def log(self, data):
        try:
            with open(self.filename, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                if not self.initialized:
                    writer.writeheader()
                    self.initialized = True
                writer.writerow(data)
        except Exception as e:
            print(f"Error writing to CSV: {e}")
