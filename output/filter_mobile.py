# -*- coding: utf-8 -*-
"""
filter_mobile.py - 筛选移动网络可访问的源
"""

import json
import time
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

TIMEOUT = 8


def check_source(source):
    """检测单个源是否可访问"""
    name = source.get('name', '')
    api_url = source.get('api', '').rstrip('/')
    check_url = f"{api_url}?ac=list&pg=1"

    try:
        start = time.time()
        resp = requests.get(check_url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        latency = int((time.time() - start) * 1000)

        if resp.status_code != 200:
            return False, f'HTTP {resp.status_code}'

        data = resp.json()
        video_list = data.get('list', [])

        if not video_list:
            return False, '空列表'

        return True, f'{latency}ms | {len(video_list)}个影片'

    except requests.exceptions.Timeout:
        return False, '超时'
    except requests.exceptions.ConnectionError:
        return False, '连接失败'
    except Exception as e:
        return False, str(e)[:30]


def main():
    with open('sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)

    print(f"共 {len(sources)} 个源，开始检测移动网络可访问性...\n")

    accessible = []
    inaccessible = []

    for i, source in enumerate(sources):
        name = source.get('name', '')
        print(f"[{i+1}/{len(sources)}] {name}...", end=' ', flush=True)

        ok, msg = check_source(source)
        if ok:
            accessible.append(source)
            print(f"OK | {msg}")
        else:
            inaccessible.append(source)
            print(f"FAIL | {msg}")

        time.sleep(0.5)

    print(f"\n{'='*50}")
    print(f"检测完成:")
    print(f"  可访问: {len(accessible)} 个")
    print(f"  不可访问: {len(inaccessible)} 个")

    with open('source1.json', 'w', encoding='utf-8') as f:
        json.dump(accessible, f, ensure_ascii=False, indent=2)

    print(f"\n可访问的源已保存到 source1.json")

    if inaccessible:
        print(f"\n不可访问的源:")
        for s in inaccessible:
            print(f"  - {s['name']}")


if __name__ == '__main__':
    main()
