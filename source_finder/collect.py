# -*- coding: utf-8 -*-
"""
collect.py - 从 yszzq.com 采集资源站页面链接
"""

import time
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

BASE_URL = "https://www.yszzq.com"
TAG_URL = f"{BASE_URL}/tags/xmlcjjk"
MAX_PAGES = 12  # 共 89 条，每页 8 条，共 12 页

KEYWORD_RE = re.compile(r'接口|地址|API|资源|资源库|资源接口|资源网', re.UNICODE)


def collect_pages():
    """爬取 yszzq.com 的 XML 采集接口标签页，提取所有相关链接"""
    all_links = []

    for page in range(1, MAX_PAGES + 1):
        url = f"{TAG_URL}/" if page == 1 else f"{TAG_URL}/index_{page}.html"
        print(f"[collect] 正在爬取第 {page}/{MAX_PAGES} 页: {url}")

        try:
            if page > 1:
                time.sleep(1.5)

            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding

            soup = BeautifulSoup(resp.text, 'lxml')

            for element in soup.find_all(string=KEYWORD_RE):
                parent = element.find_parent('a')
                if not parent or 'href' not in parent.attrs:
                    continue

                raw_href = parent['href']
                title = element.strip()

                if raw_href.startswith(('http://', 'https://')):
                    link_url = raw_href
                elif raw_href.startswith('/'):
                    link_url = f"{BASE_URL}{raw_href}"
                else:
                    link_url = f"{BASE_URL}/{raw_href}"

                if '采集接口' in title or '资源库' in title or '资源接口' in title or '采集API接口' in title:
                    all_links.append({'name': title, 'url': link_url})
                    print(f"  [OK] {title[:20]}... -> {link_url[:50]}...")

        except Exception as e:
            print(f"  [ERR] 第 {page} 页出错: {e}")

    print(f"[collect] 共采集到 {len(all_links)} 条链接")
    return all_links


if __name__ == '__main__':
    links = collect_pages()
    for link in links:
        print(f"{link['name']} | {link['url']}")
