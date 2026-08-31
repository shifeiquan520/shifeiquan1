# -*- coding: utf-8 -*-
"""
main.py - 源发现器主入口
流程：爬取 -> 提取 -> 检测 -> 去重 -> 输出 sources.json
"""

import os
import json
import sys

# 将 source_finder 目录加入路径
sys.path.insert(0, os.path.dirname(__file__))

from collect import collect_pages
from extract import extract_all
from check import check_all
from dedup import dedup_sources, to_tvbox_format

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'sources.json')


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

    # 转换为 TVBox 格式
    tvbox_sources = to_tvbox_format(sources)

    # 输出到文件
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(tvbox_sources, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] 完成！共 {len(tvbox_sources)} 个可用源")
    print(f"[FILE] 输出文件: {OUTPUT_FILE}")
    print(f"{'=' * 50}")

    # 打印前 10 个源预览
    print("\n前 10 个源预览：")
    for i, src in enumerate(tvbox_sources[:10]):
        print(f"  {i + 1}. {src['name']} | {src['api'][:50]}...")


if __name__ == '__main__':
    main()
