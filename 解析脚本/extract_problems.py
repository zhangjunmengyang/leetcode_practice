#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 LeetCode Hot 100 HTML 文件中提取题目信息并输出简洁 JSON
"""

import json
import re
from pathlib import Path


def extract_problems(html_file: str) -> list:
    """从 HTML 文件中提取题目信息"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 __NEXT_DATA__ 中的 JSON 数据
    pattern = r'<script id="__NEXT_DATA__" type="application/json">\s*(.*?)\s*</script>'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError("未找到 __NEXT_DATA__ 数据")
    
    data = json.loads(match.group(1))
    study_plan = data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['studyPlanV2Detail']
    
    problems = []
    for group in study_plan.get('planSubGroups', []):
        for q in group.get('questions', []):
            problems.append({
                "id": q.get('questionFrontendId', ''),
                "title": q.get('translatedTitle', ''),
                "difficulty": {'EASY': '简单', 'MEDIUM': '中等', 'HARD': '困难'}.get(q.get('difficulty', ''), ''),
            })
    
    return problems


def main():
    script_dir = Path(__file__).parent
    html_file = script_dir / "题单" / "leetcode75"
    output_file = script_dir / "problems.json"
    
    problems = extract_problems(str(html_file))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 成功提取 {len(problems)} 道题目，已保存到 {output_file}")


if __name__ == "__main__":
    main()
