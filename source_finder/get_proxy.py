# -*- coding: utf-8 -*-
"""
get_proxy.py - 从 kuaidaili.com 获取免费中国移动 HTTP 代理
输出: output/yddl.json
"""

import os
import json
import time
import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'yddl.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

TEST_URLS = [
    'http://www.baidu.com/s?wd=ip',
    'http://www.qq.com',
    'http://www.163.com',
]
TEST_TIMEOUT = 10


def fetch_proxy_list():
    """从 kuaidaili.com 获取代理列表"""
    url = "https://www.kuaidaili.com/free/inha/"
    
    print(f"[get_proxy] 获取代理列表: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        return resp.text
    except Exception as e:
        print(f"[get_proxy] 获取失败: {e}")
        return ""


def parse_mobile_proxies(html):
    """解析HTML表格，筛选移动代理"""
    proxies = []
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table')
    if not table:
        print("[get_proxy] 未找到表格")
        return proxies
    
    rows = table.find_all('tr')
    for row in rows[1:]:  # 跳过表头
        cells = row.find_all('td')
        if len(cells) >= 4:
            ip = cells[0].get_text(strip=True)
            port = cells[1].get_text(strip=True)
            location = cells[2].get_text(strip=True)
            carrier = cells[3].get_text(strip=True)
            
            # 匹配移动代理
            if '移动' in carrier or '移动' in location:
                proxies.append({
                    'proxy': f'http://{ip}:{port}',
                    'info': f'{location} {carrier}',
                })
    
    print(f"[get_proxy] 找到 {len(proxies)} 个移动代理")
    return proxies


def test_proxy(proxy_url):
    """测试代理是否可用"""
    proxies = {'http': proxy_url, 'https': proxy_url}
    for test_url in TEST_URLS:
        try:
            start = time.time()
            resp = requests.get(test_url, proxies=proxies, timeout=TEST_TIMEOUT, verify=False)
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return True, latency
        except Exception:
            continue
    return False, 0


def save_proxy(data):
    """保存代理到 yddl.json"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[get_proxy] 已保存: {OUTPUT_FILE}")
    print(f"[get_proxy] 代理: {data.get('proxy', '无')}")
    print(f"[get_proxy] 信息: {data.get('info', '无')}")


def main():
    print("=" * 50)
    print("  移动代理获取器")
    print("=" * 50)
    
    # 1. 获取代理列表
    html = fetch_proxy_list()
    if not html:
        print("[get_proxy] 未获取到代理列表，使用空代理（直接测试）")
        save_proxy({'proxy': '', 'info': '获取失败，直接测试'})
        return
    
    # 2. 筛选移动代理
    proxies = parse_mobile_proxies(html)
    if not proxies:
        print("[get_proxy] 未找到移动代理，使用空代理（直接测试）")
        save_proxy({'proxy': '', 'info': '无移动代理，直接测试'})
        return
    
    # 3. 逐个测试
    print(f"\n[get_proxy] 开始测试 {len(proxies)} 个代理...")
    for i, p in enumerate(proxies):
        print(f"  [{i+1}/{len(proxies)}] {p['proxy']} ({p['info']})...", end=' ', flush=True)
        ok, latency = test_proxy(p['proxy'])
        if ok:
            print(f"OK ({latency}ms)")
            p['latency_ms'] = latency
            save_proxy(p)
            return
        else:
            print("FAIL")
        time.sleep(0.5)
    
    # 4. 全部失败
    print("[get_proxy] 所有代理测试失败，使用空代理（直接测试）")
    save_proxy({'proxy': '', 'info': '全部失败，直接测试'})


if __name__ == '__main__':
    main()
