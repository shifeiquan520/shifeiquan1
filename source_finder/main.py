# -*- coding: utf-8 -*-
"""
main.py - 源发现器主入口
流程：爬取 -> 提取 -> 检测 -> 去重 -> sources.json
      sources.json -> 筛选非成人 -> sources1.json (按延迟排序)
      sources.json -> 筛选成人 -> sources18.json
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
NON_ADULT_FILE = os.path.join(OUTPUT_DIR, 'sources1.json')
ADULT_FILE = os.path.join(OUTPUT_DIR, 'sources18.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

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


def clean_name(name):
    for suffix in SUFFIXES:
        if name.endswith(suffix):
            cleaned = name[:-len(suffix)]
            if cleaned:
                return cleaned
    return name


def is_adult_source(source):
    """检测源是否为成人源（用原始 sources，包含 categories）"""
    categories = source.get('categories', [])
    src_cats = set(categories)
    if src_cats & ADULT_CATEGORIES:
        return True
    return False


def main():
    print("=" * 50)
    print("  源发现器 - 从 yszzq.com 采集可用影视源")
    print("=" * 50)

    # 1. 爬取页面链接
    print("\n[步骤 1/4] 爬取 yszzq.com 页面链接...")
    pages = collect_pages()
    if not pages:
        print("[ERR] 未采集到任何链接，退出")
        return

    # 2. 提取 API 地址
    print(f"\n[步骤 2/4] 提取 API 地址（共 {len(pages)} 个页面）...")
    sources = extract_all(pages)
    if not sources:
        print("[ERR] 未提取到任何 API 地址，退出")
        return

    # 3. 存活检测
    print(f"\n[步骤 3/4] 存活检测（共 {len(sources)} 个源）...")
    sources = check_all(sources)

    # 4. 去重
    print(f"\n[步骤 4/4] 域名去重...")
    sources = dedup_sources(sources)
    if not sources:
        print("[ERR] 去重后无可用源，退出")
        return

    # 转换为 TVBox 格式（不含 categories）
    tvbox_sources = to_tvbox_format(sources)

    # 清理名称
    for s in tvbox_sources:
        s['name'] = clean_name(s['name'])
        if s['key'] in RENAME_MAP:
            s['name'] = RENAME_MAP[s['key']]

    # 输出 sources.json（所有源）
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(tvbox_sources, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] sources.json: {len(tvbox_sources)} 个可用源")
    print(f"[FILE] {OUTPUT_FILE}")

    # ---- 筛选非成人源 -> sources1.json（按延迟排序）----
    # 用原始 sources（含 categories）做成人检测
    non_adult = []
    for s in tvbox_sources:
        # 找到对应的原始 source（用 key 匹配）
        original = next((src for src in sources if src.get('key') == s['key']), None)
        if original and not is_adult_source(original):
            non_adult.append(s)
    non_adult.sort(key=lambda x: x.get('latency_ms', 99999))

    with open(NON_ADULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(non_adult, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] sources1.json: {len(non_adult)} 个非成人源（按延迟排序）")
    print(f"[FILE] {NON_ADULT_FILE}")

    # ---- 筛选成人源 -> sources18.json ----
    adult = []
    for s in tvbox_sources:
        original = next((src for src in sources if src.get('key') == s['key']), None)
        if original and is_adult_source(original):
            adult.append(s)

    with open(ADULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(adult, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] sources18.json: {len(adult)} 个成人源")
    print(f"[FILE] {ADULT_FILE}")

    print(f"\n{'=' * 50}")

    # 打印前 10 个源预览
    print("\n前 10 个非成人源预览：")
    for i, src in enumerate(non_adult[:10]):
        print(f"  {i + 1}. {src['name']} | {src.get('latency_ms', 0)}ms | {src['api'][:40]}...")


if __name__ == '__main__':
    main()
