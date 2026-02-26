import json

with open('all_problems.json', 'r', encoding='utf-8') as f:
    problems = json.load(f)

# 难度顺序映射
difficulty_order = {'简单': 0, '中等': 1, '困难': 2}

def sort_key(x):
    """排序函数：先按难度，再按 id（处理数字和 LCR xxx 格式）"""
    diff_order = difficulty_order.get(x['difficulty'], 99)
    id_str = x['id']
    
    if id_str.startswith('LCR'):
        # LCR 题目排在普通题目后面，按 LCR 后的数字排序
        lcr_num = int(id_str.split()[1])
        return (diff_order, 1, lcr_num)
    else:
        # 普通数字 id
        return (diff_order, 0, int(id_str))

# 按照难度-id 排序
problems.sort(key=sort_key)

# 保存排序后的结果
with open('all_problems_sorted.json', 'w', encoding='utf-8') as f:
    json.dump(problems, f, ensure_ascii=False, indent=2)

# 输出 Markdown 表格
print('| 序号 | ID | 题目 | 难度 |')
print('|------|-----|------|------|')
for i, p in enumerate(problems, 1):
    print(f'| {i} | {p["id"]} | {p["title"]} | {p["difficulty"]} |')