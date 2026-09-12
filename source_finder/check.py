# -*- coding: utf-8 -*-
"""
check.py - 存活检测 + 延迟记录
"""

import time
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

TIMEOUT = 10


def check_source(source):
    """检测单个源是否存活"""
    name = source['name']
    api_url = source['api_url'].rstrip('/')
    check_url = f"{api_url}?ac=list&pg=1"

    try:
        start = time.time()
        resp = requests.get(check_url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        latency = int((time.time() - start) * 1000)

        if resp.status_code != 200:
            return {
                'name': name,
                'api_url': api_url,
                'alive': False,
                'latency_ms': 0,
                'error': f'HTTP {resp.status_code}'
            }

        data = resp.json()
        video_list = data.get('list', [])
        categories = [c.get('type_name', '') for c in data.get('class', [])]

        if not video_list:
            return {
                'name': name,
                'api_url': api_url,
                'alive': False,
                'latency_ms': latency,
                'error': '空列表'
            }

        return {
            'name': name,
            'api_url': api_url,
            'alive': True,
            'latency_ms': latency,
            'video_count': len(video_list),
            'categories': categories,
            'error': None
        }

    except requests.exceptions.Timeout:
        return {
            'name': name,
            'api_url': api_url,
            'alive': False,
            'latency_ms': 0,
            'error': '超时'
        }
    except Exception as e:
        return {
            'name': name,
            'api_url': api_url,
            'alive': False,
            'latency_ms': 0,
            'error': str(e)[:50]
        }


def check_all(sources):
    """批量检测所有源"""
    alive_count = 0
    total = len(sources)

    for i, source in enumerate(sources):
        print(f"[check] 正在检测 {i + 1}/{total}: {source['name'][:20]}...")
        result = check_source(source)
        source.update(result)

        if result['alive']:
            alive_count += 1
            print(f"  [OK] 存活 | 延迟 {result['latency_ms']}ms | {result.get('video_count', 0)} 个影片")
        else:
            print(f"  [FAIL] 失效 | {result.get('error', '未知')}")

        time.sleep(0.3)

    print(f"[check] 存活 {alive_count}/{total} 个源")
    return sources


if __name__ == '__main__':
    test_sources = [
        {'name': '量子', 'api_url': 'https://cj.lziapi.com/api.php/provide/vod/'}
    ]
    results = check_all(test_sources)
    for r in results:
        status = '✅' if r['alive'] else '❌'
        print(f"{status} {r['name']} | {r.get('error', '')}")
