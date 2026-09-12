# -*- coding: utf-8 -*-
"""
extract.py - 从采集到的页面中提取真实 API 地址
"""

import time
import re
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Referer': 'https://www.yszzq.com/',
}

API_PATTERNS = [
    # data-clipboard-text 属性中的 API 链接（优先）
    re.compile(r"data-clipboard-text=['\"](https?://[^'\"]+?/api\.php[^'\"]*?)['\"]"),
    # 页面中直接出现的 api.php 链接
    re.compile(r'["\'](https?://[^"\']+?/api\.php[^"\']*?)["\']'),
    # JSON 配置中的 api 字段
    re.compile(r'"api"\s*:\s*"(https?://[^"]+?/api\.php[^"]*)"'),
    # textarea/input 中的链接
    re.compile(r'value="(https?://[^"]+?/api\.php[^"]*)"'),
]


def extract_api_url(page_info):
    """从单个页面提取 api.php 地址"""
    name = page_info['name']
    url = page_info['url']

    for retry in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                time.sleep(1)
                continue

            resp.encoding = resp.apparent_encoding
            html = resp.text

            for pattern in API_PATTERNS:
                match = pattern.search(html)
                if match:
                    api_url = match.group(1).strip().lstrip('>')
                    # 标准化为提供 vod 的基础路径
                    if '/api.php/provide/vod' not in api_url:
                        base = api_url.split('/api.php')[0]
                        api_url = f"{base}/api.php/provide/vod/"
                    return {'name': name, 'api_url': api_url}

            # 备用：查找所有包含 api.php 的链接
            all_links = re.findall(r'["\']([^"\']*?api\.php[^"\']*?)["\']', html)
            for link in all_links:
                link = link.lstrip('>')
                if 'provide/vod' in link or 'at/xml' in link:
                    base = link.split('/api.php')[0]
                    api_url = f"{base}/api.php/provide/vod/"
                    return {'name': name, 'api_url': api_url}

            print(f"  [WARN] {name}: 未找到 API 链接")
            break

        except Exception as e:
            print(f"  [ERR] {name} 第 {retry + 1} 次请求失败: {e}")
            time.sleep(1)

    return None


def extract_all(pages):
    """批量提取所有页面的 API 地址"""
    results = []
    total = len(pages)

    for i, page in enumerate(pages):
        print(f"[extract] 正在提取 {i + 1}/{total}: {page['name'][:20]}...")
        result = extract_api_url(page)
        if result:
            results.append(result)
            print(f"  [OK] {result['name'][:20]} -> {result['api_url'][:50]}...")
        time.sleep(0.5)

    print(f"[extract] 共提取到 {len(results)}/{total} 个有效 API")
    return results


if __name__ == '__main__':
    # 测试：模拟 collect 输出
    test_pages = [
        {'name': '测试源', 'url': 'https://www.yszzq.com/tags/xmlcjjk'}
    ]
    results = extract_all(test_pages)
    for r in results:
        print(f"{r['name']} | {r['api_url']}")
