# -*- coding: utf-8 -*-
"""
main.py - 源发现器主入口
流程：爬取 -> 提取 -> 检测 -> 去重 -> sources.json -> 移动筛选 -> source1.json -> 成人筛选 -> sources18.json
"""

import os
import json
import sys
import time
import requests

# 将 source_finder 目录加入路径
sys.path.insert(0, os.path.dirname(__file__))

from collect import collect_pages
from extract import extract_all
from check import check_all
from dedup import dedup_sources, to_tvbox_format

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'sources.json')
MOBILE_FILE = os.path.join(OUTPUT_DIR, 'source1.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}
MOBILE_TIMEOUT = 8

SUFFIXES = [
    '采集综合资源接口', '采集站采集接口大全', '资源网资源采集接口',
    'API采集接口大全', '采集网采集接口', '资源采集接口',
    '采集接口地址', '采集接口',
]

RENAME_MAP = {
    'subocj.com': '速播资源',
    'api.ukuapi88.com': 'uku资源',
    'www.hongniuzy2.com': '红牛资源',
}


def clean_name(name):
    for suffix in SUFFIXES:
        if name.endswith(suffix):
            cleaned = name[:-len(suffix)]
            if cleaned:
                return cleaned
    return name


def check_mobile_accessible(source):
    """检测单个源是否移动网络可访问"""
    api_url = source.get('api', '').rstrip('/')
    check_url = f"{api_url}?ac=list&pg=1"

    try:
        start = time.time()
        resp = requests.get(check_url, headers=HEADERS, timeout=MOBILE_TIMEOUT, verify=False)
        latency = int((time.time() - start) * 1000)
        if resp.status_code != 200:
            return False
        data = resp.json()
        video_list = data.get('list', [])
        if len(video_list) > 0:
            source['latency_ms'] = latency
            return True
        return False
    except Exception:
        return False


def filter_mobile_sources(sources):
    """筛选移动网络可访问的源，按延迟排序"""
    accessible = []
    for i, source in enumerate(sources):
        name = source.get('name', '')
        print(f"  [{i+1}/{len(sources)}] {name}...", end=' ', flush=True)
        
        if check_mobile_accessible(source):
            accessible.append(source)
            print(f"OK ({source.get('latency_ms', 0)}ms)")
        else:
            print("FAIL")
        
        time.sleep(0.5)
    
    accessible.sort(key=lambda x: x.get('latency_ms', 99999))
    return accessible


def main():
    print("=" * 50)
    print("  源发现器 - 从 yszzq.com 采集可用影视源")
    print("=" * 50)

    # 1. 爬取页面链接
    print("\n[步骤 1/5] 爬取 yszzq.com 页面链接...")
    pages = collect_pages()
    if not pages:
        print("[ERR] 未采集到任何链接，退出")
        return

    # 2. 提取 API 地址
    print(f"\n[步骤 2/5] 提取 API 地址（共 {len(pages)} 个页面）...")
    sources = extract_all(pages)
    if not sources:
        print("[ERR] 未提取到任何 API 地址，退出")
        return

    # 3. 存活检测
    print(f"\n[步骤 3/5] 存活检测（共 {len(sources)} 个源）...")
    sources = check_all(sources)

    # 4. 去重
    print(f"\n[步骤 4/5] 域名去重...")
    sources = dedup_sources(sources)
    if not sources:
        print("[ERR] 去重后无可用源，退出")
        return

    # 转换为 TVBox 格式
    tvbox_sources = to_tvbox_format(sources)

    # 清理名称：去掉冗余后缀 + 手动改名
    for s in tvbox_sources:
        s['name'] = clean_name(s['name'])
        if s['key'] in RENAME_MAP:
            s['name'] = RENAME_MAP[s['key']]

    # 输出到文件
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(tvbox_sources, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] sources.json: {len(tvbox_sources)} 个可用源")
    print(f"[FILE] 输出文件: {OUTPUT_FILE}")

    # ---- 步骤 5: 筛选移动可访问源 -> source1.json ----
    print(f"\n[步骤 5/5] 筛选移动网络可访问源...")
    accessible_sources = filter_mobile_sources(tvbox_sources)
    
    with open(MOBILE_FILE, 'w', encoding='utf-8') as f:
        json.dump(accessible_sources, f, ensure_ascii=False, indent=2)
    
    print(f"\n[DONE] source1.json: {len(accessible_sources)} 个移动可访问源")
    print(f"[FILE] 输出文件: {MOBILE_FILE}")

    # ---- 生成 sources18.json（从 source1.json 筛选成人源）----
    ADULT_CATEGORIES = {
        '精品推荐', '国产精品', '日本有码', '日本无码', '网曝系列', '自拍偷拍',
        '三级伦理', '童颜巨乳', '性感人妻', '强奸乱伦', '欧美情色', '丝袜OL',
        '麻豆传媒', '明星换脸', '国产乱伦', '国产SM', '探花嫖娼', '同性恋',
        '无码专区', 'AI换脸', '制服诱惑', '欧美系列', '美女主播', '国产自拍',
        '熟女人妻', '美乳巨乳', '街拍偷拍', '丝袜美腿', '欧美风情', '网友自拍',
        '露出激情', '欧美无码', 'SM调教', 'AV解说', '国产色情', '亚洲无码',
        '亚洲有码', '巨乳美乳', '人妻熟女', '91探花', '传媒出品', '网曝门',
        '同志女同', '同志男同',
    }

    import requests as _req
    adult_sources = []
    for s in accessible_sources:
        try:
            r = _req.get(s['api'], params={'ac': 'list', 'pg': 1}, timeout=8, verify=False)
            if r.status_code == 200:
                classes = r.json().get('class', [])
                src_cats = {c.get('type_name', '') for c in classes}
                if src_cats & ADULT_CATEGORIES:
                    adult_sources.append(s)
                    print(f"  [ADULT] {s['name']} - 匹配 {len(src_cats & ADULT_CATEGORIES)} 个成人分类")
        except Exception:
            pass

    adult_file = os.path.join(OUTPUT_DIR, 'sources18.json')
    with open(adult_file, 'w', encoding='utf-8') as f:
        json.dump(adult_sources, f, ensure_ascii=False, indent=2)

    print(f"\n  sources18.json: {len(adult_sources)} 个成人源（移动可访问）")
    print(f"{'=' * 50}")

    # 打印前 10 个源预览
    print("\n前 10 个源预览：")
    for i, src in enumerate(tvbox_sources[:10]):
        print(f"  {i + 1}. {src['name']} | {src['api'][:50]}...")


if __name__ == '__main__':
    main()
