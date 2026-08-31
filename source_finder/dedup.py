# -*- coding: utf-8 -*-
"""
dedup.py - 按域名去重
"""

from urllib.parse import urlparse


def extract_domain(api_url):
    """从 API URL 中提取域名"""
    try:
        parsed = urlparse(api_url)
        return parsed.netloc.lower()
    except Exception:
        return api_url


def dedup_sources(sources):
    """按域名去重，保留第一个出现的"""
    seen_domains = set()
    unique_sources = []

    for source in sources:
        if not source.get('alive', False):
            continue

        domain = extract_domain(source['api_url'])
        if domain not in seen_domains:
            seen_domains.add(domain)
            # 用域名作为 key
            source['key'] = domain
            unique_sources.append(source)

    print(f"[dedup] 去重前 {len(sources)} 个，去重后 {len(unique_sources)} 个")
    return unique_sources


def to_tvbox_format(sources):
    """转换为采集之王.py 需要的 TVBox 格式"""
    result = []
    for source in sources:
        result.append({
            'key': source['key'],
            'name': source['name'],
            'api': source['api_url'].rstrip('/') + '/'
        })
    return result


if __name__ == '__main__':
    test = [
        {'name': '量子A', 'api_url': 'https://cj.lziapi.com/api.php/provide/vod/', 'alive': True},
        {'name': '量子B', 'api_url': 'https://cj.lziapi.com/api.php/provide/vod/', 'alive': True},
        {'name': '非凡', 'api_url': 'https://ffzy5.tv/api.php/provide/vod/', 'alive': True},
    ]
    result = dedup_sources(test)
    for r in result:
        print(f"{r['key']} | {r['name']}")
