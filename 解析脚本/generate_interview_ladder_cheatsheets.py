from __future__ import annotations

import json
import re
import textwrap
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_JSON = ROOT / "解析脚本" / "all_problems_sorted.json"
STUDY_PLAN_DIR = ROOT / "题单"
OUTPUT_DIR = ROOT / "面试阶梯速记"
DAY_SIZES = [52, 52, 52, 52, 51, 50]

SOURCE_NAMES = {
    "hot100": "Hot100",
    "经典150": "经典150",
    "interview75": "Interview75",
    "leetcode75": "LC75",
}

PLAN_FILES = ["hot100", "经典150", "interview75", "leetcode75"]

# LCR / 剑指 Offer 改名题，统一映射到更直观的 canonical slug，方便复用模板。
SLUG_ALIAS = {
    "shu-zu-zhong-zhong-fu-de-shu-zi-lcof": "find-repeat-number",
    "er-wei-shu-zu-zhong-de-cha-zhao-lcof": "search-sorted-matrix-from-corner",
    "ti-huan-kong-ge-lcof": "replace-spaces",
    "cong-wei-dao-tou-da-yin-lian-biao-lcof": "reverse-print-linked-list",
    "zhong-jian-er-cha-shu-lcof": "construct-binary-tree-from-preorder-and-inorder-traversal",
    "yong-liang-ge-zhan-shi-xian-dui-lie-lcof": "implement-queue-using-stacks",
    "fei-bo-na-qi-shu-lie-lcof": "fibonacci-number",
    "qing-wa-tiao-tai-jie-wen-ti-lcof": "climbing-stairs",
    "xuan-zhuan-shu-zu-de-zui-xiao-shu-zi-lcof": "find-minimum-in-rotated-sorted-array",
    "er-jin-zhi-zhong-1de-ge-shu-lcof": "number-of-1-bits",
    "shu-zhi-de-zheng-shu-ci-fang-lcof": "powx-n",
    "da-yin-cong-1dao-zui-da-de-nwei-shu-lcof": "print-numbers",
    "shan-chu-lian-biao-de-jie-dian-lcof": "delete-node-linked-list",
    "zheng-ze-biao-da-shi-pi-pei-lcof": "regular-expression-matching",
    "biao-shi-shu-zhi-de-zi-fu-chuan-lcof": "valid-number",
    "diao-zheng-shu-zu-shun-xu-shi-qi-shu-wei-yu-ou-shu-qian-mian-lcof": "reorder-array-by-parity",
    "lian-biao-zhong-dao-shu-di-kge-jie-dian-lcof": "kth-node-from-end",
    "fan-zhuan-lian-biao-lcof": "reverse-linked-list",
    "he-bing-liang-ge-pai-xu-de-lian-biao-lcof": "merge-two-sorted-lists",
    "shu-de-zi-jie-gou-lcof": "substructure-of-tree",
    "er-cha-shu-de-jing-xiang-lcof": "invert-binary-tree",
    "dui-cheng-de-er-cha-shu-lcof": "symmetric-tree",
    "shun-shi-zhen-da-yin-ju-zhen-lcof": "spiral-matrix",
    "bao-han-minhan-shu-de-zhan-lcof": "min-stack",
    "zhan-de-ya-ru-dan-chu-xu-lie-lcof": "validate-stack-sequences",
    "cong-shang-dao-xia-da-yin-er-cha-shu-lcof": "binary-tree-level-order-traversal-flat",
    "cong-shang-dao-xia-da-yin-er-cha-shu-ii-lcof": "binary-tree-level-order-traversal",
    "cong-shang-dao-xia-da-yin-er-cha-shu-iii-lcof": "binary-tree-zigzag-level-order-traversal",
    "er-cha-sou-suo-shu-de-hou-xu-bian-li-xu-lie-lcof": "verify-postorder-of-bst",
    "er-cha-shu-zhong-he-wei-mou-yi-zhi-de-lu-jing-lcof": "path-sum-ii",
    "fu-za-lian-biao-de-fu-zhi-lcof": "copy-list-with-random-pointer",
    "er-cha-sou-suo-shu-yu-shuang-xiang-lian-biao-lcof": "convert-bst-to-doubly-linked-list",
    "xu-lie-hua-er-cha-shu-lcof": "serialize-and-deserialize-binary-tree",
    "zi-fu-chuan-de-pai-lie-lcof": "string-permutation",
    "shu-zu-zhong-chu-xian-ci-shu-chao-guo-yi-ban-de-shu-zi-lcof": "majority-element",
    "zui-xiao-de-kge-shu-lcof": "smallest-k-elements",
    "shu-ju-liu-zhong-de-zhong-wei-shu-lcof": "median-finder",
    "lian-xu-zi-shu-zu-de-zui-da-he-lcof": "maximum-subarray",
    "1nzheng-shu-zhong-1chu-xian-de-ci-shu-lcof": "number-of-digit-one",
    "shu-zi-xu-lie-zhong-mou-yi-wei-de-shu-zi-lcof": "nth-digit",
    "ba-shu-zu-pai-cheng-zui-xiao-de-shu-lcof": "arrange-to-smallest-number",
    "ba-shu-zi-fan-yi-cheng-zi-fu-chuan-lcof": "translate-number-to-string",
    "li-wu-de-zui-da-jie-zhi-lcof": "max-value-of-gifts",
    "zui-chang-bu-han-zhong-fu-zi-fu-de-zi-zi-fu-chuan-lcof": "longest-substring-without-repeating-characters",
    "chou-shu-lcof": "ugly-number-ii",
    "di-yi-ge-zhi-chu-xian-yi-ci-de-zi-fu-lcof": "first-unique-character",
    "shu-zu-zhong-de-ni-xu-dui-lcof": "reverse-pairs",
    "liang-ge-lian-biao-de-di-yi-ge-gong-gong-jie-dian-lcof": "intersection-of-two-linked-lists",
    "zai-pai-xu-shu-zu-zhong-cha-zhao-shu-zi-lcof": "count-target-in-sorted-array",
    "que-shi-de-shu-zi-lcof": "missing-number-sorted",
    "er-cha-sou-suo-shu-de-di-kda-jie-dian-lcof": "kth-largest-bst",
    "er-cha-shu-de-shen-du-lcof": "maximum-depth-of-binary-tree",
    "ping-heng-er-cha-shu-lcof": "balanced-binary-tree",
    "shu-zu-zhong-shu-zi-chu-xian-de-ci-shu-lcof": "single-numbers",
    "shu-zu-zhong-shu-zi-chu-xian-de-ci-shu-ii-lcof": "single-number-ii",
    "he-wei-sde-liang-ge-shu-zi-lcof": "two-sum-ii-input-array-is-sorted",
    "he-wei-sde-lian-xu-zheng-shu-xu-lie-lcof": "find-continuous-sequence",
    "fan-zhuan-dan-ci-shun-xu-lcof": "reverse-words-in-a-string",
    "zuo-xuan-zhuan-zi-fu-chuan-lcof": "left-rotate-string",
    "hua-dong-chuang-kou-de-zui-da-zhi-lcof": "sliding-window-maximum",
    "dui-lie-de-zui-da-zhi-lcof": "max-queue",
    "nge-tou-zi-de-dian-shu-lcof": "dices-probability",
    "bu-ke-pai-zhong-de-shun-zi-lcof": "straight-in-poker",
    "yuan-quan-zhong-zui-hou-sheng-xia-de-shu-zi-lcof": "josephus-problem",
    "gu-piao-de-zui-da-li-run-lcof": "best-time-to-buy-and-sell-stock",
    "qiu-12n-lcof": "sum-nums",
    "bu-yong-jia-jian-cheng-chu-zuo-jia-fa-lcof": "add-without-operators",
    "gou-jian-cheng-ji-shu-zu-lcof": "construct-product-array",
    "ba-zi-fu-chuan-zhuan-huan-cheng-zheng-shu-lcof": "string-to-integer-atoi",
    "er-cha-sou-suo-shu-de-zui-jin-gong-gong-zu-xian-lcof": "lowest-common-ancestor-of-a-binary-search-tree",
    "er-cha-shu-de-zui-jin-gong-gong-zu-xian-lcof": "lowest-common-ancestor-of-a-binary-tree",
    "ju-zhen-zhong-de-lu-jing-lcof": "word-search",
    "ji-qi-ren-de-yun-dong-fan-wei-lcof": "moving-count",
    "jian-sheng-zi-lcof": "cutting-rope",
    "jian-sheng-zi-ii-lcof": "cutting-rope-ii",
}

CANONICAL_HINT = {
    "replace-spaces": "替换空格",
    "reverse-print-linked-list": "倒序打印链表",
    "implement-queue-using-stacks": "用两个栈实现队列",
    "reorder-array-by-parity": "奇偶重排",
    "kth-node-from-end": "链表倒数第 k 个结点",
    "substructure-of-tree": "树的子结构",
    "binary-tree-level-order-traversal-flat": "层序遍历（拍平）",
    "verify-postorder-of-bst": "验证 BST 后序序列",
    "convert-bst-to-doubly-linked-list": "BST 转循环双向链表",
    "smallest-k-elements": "最小的 k 个数",
    "count-target-in-sorted-array": "有序数组统计次数",
    "missing-number-sorted": "有序数组缺失数字",
    "kth-largest-bst": "BST 第 k 大",
    "single-numbers": "数组中两个只出现一次的数",
    "left-rotate-string": "左旋转字符串",
    "max-queue": "队列最大值",
    "dices-probability": "n 个骰子的点数概率",
    "straight-in-poker": "扑克牌顺子",
    "josephus-problem": "约瑟夫环",
    "sum-nums": "1 到 n 累加",
    "add-without-operators": "不用四则运算做加法",
    "construct-product-array": "构建乘积数组",
    "search-sorted-matrix-from-corner": "二维有序矩阵查找",
    "find-repeat-number": "数组中重复的数字",
    "print-numbers": "打印 1 到最大 n 位数",
    "moving-count": "机器人的运动范围",
    "cutting-rope": "剪绳子 I",
    "cutting-rope-ii": "剪绳子 II",
    "arrange-to-smallest-number": "把数组排成最小的数",
    "translate-number-to-string": "数字翻译成字符串",
    "max-value-of-gifts": "礼物最大价值",
    "first-unique-character": "第一个只出现一次的字符",
}


@dataclass
class Problem:
    index: int
    pid: str
    title: str
    difficulty: str
    slug: str
    tags: list[str]
    groups: list[str]
    sources: list[str]
    canonical: str


def dedent_code(code: str) -> str:
    return textwrap.dedent(code).strip("\n")


def note(family: str, memory: str, baseline: str, optimized: str, code: str) -> dict[str, str]:
    return {
        "family": family,
        "memory": memory,
        "baseline": baseline,
        "optimized": optimized,
        "code": dedent_code(code),
    }


def parse_next_data(html_path: Path) -> dict:
    text = html_path.read_text()
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', text, re.S)
    if not match:
        raise ValueError(f"__NEXT_DATA__ not found in {html_path}")
    return json.loads(match.group(1))


def load_plan_meta() -> dict[tuple[str, str], dict]:
    meta: dict[tuple[str, str], dict] = defaultdict(lambda: {"slug": "", "tags": set(), "groups": set(), "sources": set()})
    for name in PLAN_FILES:
        data = parse_next_data(STUDY_PLAN_DIR / name)
        detail = data["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["studyPlanV2Detail"]
        for subgroup in detail["planSubGroups"]:
            group_name = subgroup["name"]
            for item in subgroup["questions"]:
                key = (str(item["questionFrontendId"]), item["translatedTitle"])
                row = meta[key]
                row["slug"] = item["titleSlug"]
                row["groups"].add(group_name)
                row["sources"].add(name)
                for tag in item.get("topicTags") or []:
                    row["tags"].add(tag.get("nameTranslated") or tag.get("name") or "")
    return meta


def load_problems() -> list[Problem]:
    plan_meta = load_plan_meta()
    raw = json.loads(INPUT_JSON.read_text())
    problems: list[Problem] = []
    for idx, item in enumerate(raw, 1):
        key = (str(item["id"]), item["title"])
        meta = plan_meta.get(key, {})
        slug = meta.get("slug", "") or ""
        canonical = SLUG_ALIAS.get(slug, slug or item["title"])
        problems.append(
            Problem(
                index=idx,
                pid=str(item["id"]),
                title=item["title"],
                difficulty=item["difficulty"],
                slug=slug,
                tags=sorted(meta.get("tags", [])),
                groups=sorted(meta.get("groups", [])),
                sources=[SOURCE_NAMES.get(x, x) for x in sorted(meta.get("sources", []))],
                canonical=canonical,
            )
        )
    return problems


def compact_track(problem: Problem) -> str:
    picks: list[str] = []
    for group in problem.groups:
        if group not in picks and len(picks) < 2:
            picks.append(group)
    for tag in problem.tags:
        if tag not in picks and len(picks) < 4:
            picks.append(tag)
    return " / ".join(picks[:4]) or "综合题"


def canonical_hint(problem: Problem) -> str:
    if problem.canonical == problem.slug or problem.canonical == problem.title:
        return ""
    return CANONICAL_HINT.get(problem.canonical, "")


def fallback_note(problem: Problem) -> dict[str, str]:
    tags = set(problem.tags)
    title = problem.title
    if "二叉树" in tags or "树" in tags:
        if "广度优先搜索" in tags or "层" in title:
            return note(
                "树 BFS",
                "树题先想层序 BFS：一层一层推，天然处理层信息。",
                "队列分层遍历，按题意统计每层答案，通常 O(n)。",
                "如果还要路径/父子约束，再切 DFS 携带状态；层题优先 BFS。",
                """
                q = deque([root])
                while q:
                    for _ in range(len(q)):
                        node = q.popleft()
                        if node.left: q.append(node.left)
                        if node.right: q.append(node.right)
                """,
            )
        return note(
            "树 DFS",
            "树题默认写 DFS：函数返回值管子树，参数管路径状态。",
            "递归后序最稳：先拿左右子树结果，再更新当前节点答案。",
            "若题目强调层次、最短路、最近出口，再改 BFS。",
            """
            def dfs(node):
                if not node:
                    return base
                left = dfs(node.left)
                right = dfs(node.right)
                return merge(left, right, node)
                """,
        )
    if "链表" in tags:
        return note(
            "链表",
            "链表题先想 dummy + 双指针，改指针前先存 `nxt`。",
            "涉及删除/拼接就挂 dummy；涉及环或中点就快慢指针。",
            "若还要回文/孪生和，常见套路是找中点后反转后半段。",
            """
            dummy = ListNode(0, head)
            pre, cur = dummy, head
            while cur:
                nxt = cur.next
                # 改指针前先存 nxt
                cur = nxt
            """,
        )
    if "回溯" in tags:
        return note(
            "回溯",
            "回溯题统一模板：选一个，递归下探，回来撤销。",
            "用 `path` 记录当前答案，满足条件就收集；复杂度取决于搜索树。",
            "去重要么先排序剪枝，要么用 `used` / 集合限制同层重复。",
            """
            ans, path = [], []
            def dfs(start):
                if done(path):
                    ans.append(path[:]); return
                for i in range(start, n):
                    path.append(nums[i])
                    dfs(i + step)
                    path.pop()
            """,
        )
    if "动态规划" in tags:
        return note(
            "动态规划",
            "DP 先定状态：`dp[i]` / `dp[i][j]` 表示什么，再写转移。",
            "先写初值，再按依赖顺序转移；能滚动就滚动压空间。",
            "面试里把“状态、转移、初始化、遍历顺序”四句话说清就够。",
            """
            dp = init()
            for i in range(...):
                for j in range(...):
                    dp[i][j] = best(from_states)
            return dp[-1][-1]
            """,
        )
    if "二分查找" in tags:
        return note(
            "二分",
            "有序 + 单调就二分，先想清楚找左边界还是找答案。",
            "标准写法维护闭区间或半开区间，核心是 `mid` 后如何缩边界。",
            "若答案不在数组里，就二分答案空间并写 `check(mid)`。",
            """
            l, r = left, right
            while l < r:
                mid = (l + r) // 2
                if check(mid):
                    r = mid
                else:
                    l = mid + 1
            return l
            """,
        )
    if "滑动窗口" in tags:
        return note(
            "滑窗",
            "窗口题就维护 `[l, r]`，右扩拿元素，左缩修约束。",
            "定长窗口用进出维护答案；不定长窗口用 while 缩到满足条件。",
            "字符频次题常配合 `Counter` / 数组计数。",
            """
            l = 0
            for r, x in enumerate(nums):
                add(x)
                while bad():
                    remove(nums[l]); l += 1
                ans = update(ans, l, r)
            """,
        )
    if "哈希表" in tags:
        return note(
            "哈希",
            "查重、计数、配对、分组，优先哈希表。",
            "把 O(n^2) 暴力改成“一边遍历一边查表”，常见 O(n)。",
            "若题目有顺序要求，再和排序/双指针联动。",
            """
            cnt = {}
            for x in nums:
                cnt[x] = cnt.get(x, 0) + 1
            """,
        )
    if "堆（优先队列）" in tags:
        return note(
            "堆",
            "要动态拿最值，就上堆。",
            "小根堆拿最小，大根堆常用取负数模拟；单次操作 O(log n)。",
            "若还有门槛条件，先排序再把可选项塞堆。",
            """
            heap = []
            for x in data:
                heappush(heap, x)
            while heap:
                x = heappop(heap)
            """,
        )
    if "图" in tags or "广度优先搜索" in tags:
        return note(
            "图",
            "图题先问自己：要连通性、最短步数、还是拓扑顺序。",
            "无权最短路用 BFS；依赖关系用拓扑排序；连通块用 DFS/并查集。",
            "建图时先写清邻接表，复杂度通常 O(V+E)。",
            """
            g = defaultdict(list)
            for a, b in edges:
                g[a].append(b)
            q = deque([start])
            while q:
                x = q.popleft()
            """,
        )
    if "位运算" in tags:
        return note(
            "位运算",
            "位运算题就盯住 `& | ^ << >>` 和每一位是否独立。",
            "判奇偶、消重、统计 bit、异或分组，都是面试高频。",
            "不会推就先把样例按二进制写出来。",
            """
            ans = 0
            while n:
                ans += n & 1
                n >>= 1
            return ans
            """,
        )
    return note(
        "综合",
        "先看数据规模定方向：暴力、排序、哈希、双指针、DP、图论哪条线最顺。",
        "面试先给能过的主解，再补一句复杂度和为何不选暴力。",
        "若题意怪，先写最小可用版本，再逐步加优化。",
        """
        # 先写出最小可验证版本
        ans = init()
        for x in data:
            ans = update(ans, x)
        return ans
        """,
    )


def describe(problem: Problem) -> dict[str, str]:
    slug = problem.canonical

    if slug == "two-sum":
        return note(
            "哈希查找",
            "哈希表记已经扫过的数，边走边查补数。",
            "一次遍历 `seen[x] = idx`，命中 `target - x` 立刻返回，O(n)。",
            "排序双指针会丢原索引；这题面试主解就是哈希一次遍历。",
            """
            seen = {}
            for i, x in enumerate(nums):
                if target - x in seen:
                    return [seen[target - x], i]
                seen[x] = i
            """,
        )

    if slug in {"palindrome-number"}:
        return note(
            "数学",
            "只反转后一半数字，和前一半比较，避免溢出也更省事。",
            "负数直接 false；循环把末位搬到 `rev`，最后比较 `x == rev` 或 `x == rev // 10`。",
            "字符串法能过但不是面试优先；半反转才是更稳的数学解。",
            """
            if x < 0 or (x % 10 == 0 and x != 0):
                return False
            rev = 0
            while x > rev:
                rev = rev * 10 + x % 10
                x //= 10
            return x == rev or x == rev // 10
            """,
        )

    if slug in {"roman-to-integer"}:
        return note(
            "字符串",
            "小值在大值左边就减，否则就加。",
            "从左到右扫，若当前值小于右边值就减掉，否则加上，O(n)。",
            "也可从右往左维护最大值；但左到右写法更口语化，面试更顺。",
            """
            mp = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
            ans = 0
            for i, ch in enumerate(s):
                val = mp[ch]
                if i + 1 < len(s) and val < mp[s[i + 1]]:
                    ans -= val
                else:
                    ans += val
            return ans
            """,
        )

    if slug in {"integer-to-roman"}:
        return note(
            "贪心",
            "把特殊值也列进表里，从大到小贪心减。",
            "预置 `1000, 900, 500, ...`，每次尽量拿最大的罗马值，O(1)。",
            "这题值域固定，贪心就是标准最优写法。",
            """
            vals = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
                    (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
                    (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
            ans = []
            for v, t in vals:
                while num >= v:
                    ans.append(t)
                    num -= v
            return ''.join(ans)
            """,
        )

    if slug in {"longest-common-prefix"}:
        return note(
            "字符串",
            "拿第一个串当答案，不断缩短到所有串都匹配。",
            "横向扫描前缀，当前缀不是某个字符串前缀时就截短，O(n * m)。",
            "先按长度排序也行，但直接 shrink prefix 更直观。",
            """
            pre = strs[0]
            for s in strs[1:]:
                while not s.startswith(pre):
                    pre = pre[:-1]
            return pre
            """,
        )

    if slug in {"valid-parentheses"}:
        return note(
            "栈",
            "左括号入栈，右括号拿栈顶配对。",
            "遍历时遇左括号入栈，遇右括号检查是否和栈顶匹配，O(n)。",
            "主解已经最优；把映射表写好，代码最干净。",
            """
            mp = {')': '(', ']': '[', '}': '{'}
            st = []
            for ch in s:
                if ch not in mp:
                    st.append(ch)
                elif not st or st.pop() != mp[ch]:
                    return False
            return not st
            """,
        )

    if slug in {"merge-two-sorted-lists"}:
        return note(
            "链表",
            "双指针比大小，小的先接到结果链表后面。",
            "挂 dummy，`l1/l2` 谁小接谁，尾指针一路推进，O(m+n)。",
            "递归也能写，但面试优先迭代版，更稳更省栈。",
            """
            dummy = tail = ListNode(0)
            while l1 and l2:
                if l1.val <= l2.val:
                    tail.next, l1 = l1, l1.next
                else:
                    tail.next, l2 = l2, l2.next
                tail = tail.next
            tail.next = l1 or l2
            return dummy.next
            """,
        )

    if slug in {"remove-duplicates-from-sorted-array"}:
        return note(
            "双指针",
            "慢指针指向下一个要写的位置，快指针负责扫新值。",
            "有序数组去重就保留每段第一个，`nums[slow] = nums[fast]`，O(n)。",
            "这题要原地，别额外开 set。",
            """
            slow = 1
            for fast in range(1, len(nums)):
                if nums[fast] != nums[fast - 1]:
                    nums[slow] = nums[fast]
                    slow += 1
            return slow
            """,
        )

    if slug in {"remove-element"}:
        return note(
            "双指针",
            "慢指针收集要保留的元素，快指针扫描全数组。",
            "不是删元素，是把不等于 `val` 的元素往前覆盖，O(n)。",
            "若不关心顺序也可和尾部交换，但保序版更常规。",
            """
            slow = 0
            for x in nums:
                if x != val:
                    nums[slow] = x
                    slow += 1
            return slow
            """,
        )

    if slug in {"find-the-index-of-the-first-occurrence-in-a-string"}:
        return note(
            "字符串匹配",
            "面试先给朴素匹配，真追问再说 KMP。",
            "直接枚举起点比较 `needle`，复杂度 O((n-m+1)*m)。",
            "更优是 KMP 到 O(n+m)；但不被追问时朴素法足够清楚。",
            """
            for i in range(len(haystack) - len(needle) + 1):
                if haystack[i:i + len(needle)] == needle:
                    return i
            return -1
            """,
        )

    if slug in {"search-insert-position", "guess-number-higher-or-lower"}:
        return note(
            "二分",
            "找位置题本质就是找第一个 `>= target` 的位置。",
            "标准左边界二分，命中就收右边界，没命中最后落在插入位。",
            "能背出这一版，后面很多 lower_bound 题都通用。",
            """
            l, r = 0, len(nums)
            while l < r:
                mid = (l + r) // 2
                if nums[mid] >= target:
                    r = mid
                else:
                    l = mid + 1
            return l
            """,
        )

    if slug in {"length-of-last-word"}:
        return note(
            "字符串",
            "先跳过尾空格，再往前数最后一个单词长度。",
            "从右往左扫，先略过空格，再累计非空格字符，O(n)。",
            "`strip().split()` 能过，但从右扫更省空间。",
            """
            i = len(s) - 1
            while i >= 0 and s[i] == ' ':
                i -= 1
            ans = 0
            while i >= 0 and s[i] != ' ':
                ans += 1
                i -= 1
            return ans
            """,
        )

    if slug in {"plus-one"}:
        return note(
            "数组",
            "从后往前处理进位，遇到不是 9 的位置直接结束。",
            "倒着扫，若当前位小于 9 就加一返回；全是 9 才在前面补 1。",
            "这题关键是别把大整数转字符串，直接模拟就行。",
            """
            for i in range(len(digits) - 1, -1, -1):
                if digits[i] < 9:
                    digits[i] += 1
                    return digits
                digits[i] = 0
            return [1] + digits
            """,
        )

    if slug in {"add-binary"}:
        return note(
            "字符串",
            "从末尾往前加，和小学竖式一样，额外带一个 carry。",
            "双指针倒序 + 进位，复杂度 O(n)。",
            "也能转十进制再转回去，但没必要。",
            """
            i, j, carry = len(a) - 1, len(b) - 1, 0
            ans = []
            while i >= 0 or j >= 0 or carry:
                s = carry
                if i >= 0: s += int(a[i]); i -= 1
                if j >= 0: s += int(b[j]); j -= 1
                ans.append(str(s % 2))
                carry = s // 2
            return ''.join(reversed(ans))
            """,
        )

    if slug in {"sqrtx"}:
        return note(
            "二分",
            "找最大满足 `mid * mid <= x` 的整数。",
            "整数平方根就是右边界二分，注意乘法可能溢出时改用 `mid <= x // mid`。",
            "牛顿迭代更快，但面试讲二分最稳。",
            """
            l, r = 0, x
            while l <= r:
                mid = (l + r) // 2
                if mid <= x // max(mid, 1):
                    l = mid + 1
                else:
                    r = mid - 1
            return r
            """,
        )

    if slug in {"climbing-stairs", "fibonacci-number", "n-th-tribonacci-number"}:
        name = "斐波那契滚动 DP" if slug != "n-th-tribonacci-number" else "三状态滚动 DP"
        return note(
            "一维 DP",
            "递推只依赖前几项，就用滚动变量代替整张表。",
            "`dp[i] = dp[i-1] + dp[i-2]` 一类题，O(n) 时间，O(1) 空间。",
            f"{name} 就是主解；面试别真的开完整数组。",
            """
            a, b = 0, 1
            for _ in range(n):
                a, b = b, a + b
            return a
            """,
        )

    if slug in {"merge-sorted-array"}:
        return note(
            "双指针",
            "从后往前填，避免覆盖 `nums1` 里还没用到的值。",
            "三指针 `i, j, k` 从尾部走，谁大放谁，O(m+n)。",
            "这是最稳的原地解；别从前往后合并。",
            """
            i, j, k = m - 1, n - 1, m + n - 1
            while j >= 0:
                if i >= 0 and nums1[i] > nums2[j]:
                    nums1[k], i = nums1[i], i - 1
                else:
                    nums1[k], j = nums2[j], j - 1
                k -= 1
            """,
        )

    if slug in {"binary-tree-inorder-traversal"}:
        return note(
            "树 DFS",
            "中序遍历模板：一路压左，弹出访问，再去右边。",
            "递归和迭代都能过；面试里写迭代更能体现你掌握遍历模板。",
            "BST 相关题很多都复用这套中序骨架。",
            """
            st, cur, ans = [], root, []
            while st or cur:
                while cur:
                    st.append(cur)
                    cur = cur.left
                cur = st.pop()
                ans.append(cur.val)
                cur = cur.right
            return ans
            """,
        )

    if slug in {"same-tree"}:
        return note(
            "树 DFS",
            "两棵树同步递归：都空才相等，值不同立刻 false。",
            "比较值和结构，左右子树继续同步 DFS，O(n)。",
            "BFS 也能做，但递归最直观。",
            """
            def same(a, b):
                if not a and not b: return True
                if not a or not b or a.val != b.val: return False
                return same(a.left, b.left) and same(a.right, b.right)
            return same(p, q)
            """,
        )

    if slug in {"symmetric-tree"}:
        return note(
            "树 DFS",
            "判断镜像：左树的左对右树的右，左树的右对右树的左。",
            "写一个 `mirror(a, b)` 同步递归比较，O(n)。",
            "层序成对比较也行，但递归更像题意。",
            """
            def mirror(a, b):
                if not a and not b: return True
                if not a or not b or a.val != b.val: return False
                return mirror(a.left, b.right) and mirror(a.right, b.left)
            return mirror(root.left, root.right) if root else True
            """,
        )

    if slug in {"maximum-depth-of-binary-tree", "balanced-binary-tree"}:
        if slug == "maximum-depth-of-binary-tree":
            return note(
                "树 DFS",
                "深度题最直接：当前节点深度 = 1 + max(左深, 右深)。",
                "递归一行就能写完，O(n)。",
                "BFS 也能数层数，但 DFS 更短。",
                """
                def dfs(node):
                    if not node: return 0
                    return 1 + max(dfs(node.left), dfs(node.right))
                return dfs(root)
                """,
            )
        return note(
            "树 DFS",
            "平衡树要后序：先拿左右高度，再顺手判断差值。",
            "后序递归返回高度，失衡时直接返回 `-1` 剪枝，O(n)。",
            "别每个节点都单独算高度，否则会退化到 O(n^2)。",
            """
            def dfs(node):
                if not node: return 0
                l = dfs(node.left)
                if l == -1: return -1
                r = dfs(node.right)
                if r == -1 or abs(l - r) > 1: return -1
                return 1 + max(l, r)
            return dfs(root) != -1
            """,
        )

    if slug in {"convert-sorted-array-to-binary-search-tree"}:
        return note(
            "分治",
            "有序数组转 BST，本质就是每次拿中点当根。",
            "递归选中点建根，左半边建左子树，右半边建右子树，O(n)。",
            "中点偏左偏右都行，只要整体平衡。",
            """
            def build(l, r):
                if l > r: return None
                mid = (l + r) // 2
                root = TreeNode(nums[mid])
                root.left = build(l, mid - 1)
                root.right = build(mid + 1, r)
                return root
            return build(0, len(nums) - 1)
            """,
        )

    if slug in {"path-sum"}:
        return note(
            "树 DFS",
            "沿路减 target，到叶子时看是否刚好减到 0。",
            "DFS 传剩余和，叶子节点判断 `remain == node.val`，O(n)。",
            "BFS 也能做，但 DFS 更自然。",
            """
            def dfs(node, remain):
                if not node: return False
                if not node.left and not node.right:
                    return remain == node.val
                remain -= node.val
                return dfs(node.left, remain) or dfs(node.right, remain)
            return dfs(root, targetSum)
            """,
        )

    if slug in {"pascals-triangle"}:
        return note(
            "动态规划",
            "杨辉三角就是边界全 1，中间等于左上 + 右上。",
            "逐行构造即可，O(numRows^2)。",
            "这题不需要复杂 DP，按定义模拟就行。",
            """
            ans = []
            for i in range(numRows):
                row = [1] * (i + 1)
                for j in range(1, i):
                    row[j] = ans[i - 1][j - 1] + ans[i - 1][j]
                ans.append(row)
            return ans
            """,
        )

    if slug in {"best-time-to-buy-and-sell-stock"}:
        return note(
            "贪心",
            "一路维护历史最低价，顺手更新最大利润。",
            "遍历价格，`min_price` 表示买入最佳点，答案是 `price - min_price` 的最大值。",
            "一次交易题主解就是这个 O(n) 贪心。",
            """
            min_price = float('inf')
            ans = 0
            for p in prices:
                min_price = min(min_price, p)
                ans = max(ans, p - min_price)
            return ans
            """,
        )

    if slug in {"valid-palindrome"}:
        return note(
            "双指针",
            "两头往中间夹，跳过非字母数字，再比较小写化后的字符。",
            "双指针 O(n)，空间 O(1)。",
            "别先构造新串，原地扫更像面试。",
            """
            l, r = 0, len(s) - 1
            while l < r:
                while l < r and not s[l].isalnum(): l += 1
                while l < r and not s[r].isalnum(): r -= 1
                if s[l].lower() != s[r].lower():
                    return False
                l += 1; r -= 1
            return True
            """,
        )

    if slug in {"single-number"}:
        return note(
            "位运算",
            "相同数字异或两次会消掉，只剩那个单独的数。",
            "遍历全数组做异或，O(n) 时间 O(1) 空间。",
            "这是这题最优解，直接背。",
            """
            ans = 0
            for x in nums:
                ans ^= x
            return ans
            """,
        )

    if slug in {"linked-list-cycle", "linked-list-cycle-ii"}:
        if slug == "linked-list-cycle":
            return note(
                "快慢指针",
                "快指针一次两步，慢指针一次一步，相遇就有环。",
                "判环直接 Floyd，O(n) 时间 O(1) 空间。",
                "哈希表也能做，但不如双指针优雅。",
                """
                slow = fast = head
                while fast and fast.next:
                    slow = slow.next
                    fast = fast.next.next
                    if slow is fast:
                        return True
                return False
                """,
            )
        return note(
            "快慢指针",
            "先相遇，再让一根指针回头，两者同步走，交点就是入环点。",
            "Floyd 第二阶段是面试高频结论，O(n) / O(1)。",
            "别只会判环，入环点也要会推。",
            """
            slow = fast = head
            while fast and fast.next:
                slow = slow.next
                fast = fast.next.next
                if slow is fast:
                    break
            else:
                return None
            p = head
            while p is not slow:
                p = p.next
                slow = slow.next
            return p
            """,
        )

    if slug in {"intersection-of-two-linked-lists"}:
        return note(
            "链表",
            "A 走完接 B，B 走完接 A，长度差自动被抵消。",
            "双指针换头后要么在交点相遇，要么一起到 None，O(m+n)。",
            "这是比先算长度更简洁的面试写法。",
            """
            a, b = headA, headB
            while a is not b:
                a = a.next if a else headB
                b = b.next if b else headA
            return a
            """,
        )

    if slug in {"majority-element"}:
        return note(
            "贪心",
            "摩尔投票：同归于尽，最后剩下的一定是多数元素。",
            "维护候选人和票数，票数归零就换人，O(n) / O(1)。",
            "哈希计数能过，但摩尔投票才是更优解。",
            """
            cand, cnt = None, 0
            for x in nums:
                if cnt == 0:
                    cand = x
                cnt += 1 if x == cand else -1
            return cand
            """,
        )

    if slug in {"reverse-bits", "number-of-1-bits"}:
        if slug == "reverse-bits":
            return note(
                "位运算",
                "一位一位取出低位，再塞到答案高位方向。",
                "循环 32 次，`ans = ans * 2 + (n & 1)`，再右移原数。",
                "固定 32 位，复杂度就是 O(1)。",
                """
                ans = 0
                for _ in range(32):
                    ans = (ans << 1) | (n & 1)
                    n >>= 1
                return ans
                """,
            )
        return note(
            "位运算",
            "最低位是不是 1，用 `n & 1` 看；想更快就用 `n &= n - 1` 消最低位 1。",
            "Brian Kernighan 写法每次抹掉一个 1，复杂度和 1 的个数成正比。",
            "这是面试里最常用的 bit count 写法。",
            """
            ans = 0
            while n:
                n &= n - 1
                ans += 1
            return ans
            """,
        )

    if slug in {"happy-number"}:
        return note(
            "哈希",
            "快乐数本质是看迭代过程会不会进环。",
            "不断把数替换成“各位平方和”，用集合判重；到 1 则成功。",
            "也能用快慢指针判环，但 set 更直观。",
            """
            seen = set()
            while n != 1 and n not in seen:
                seen.add(n)
                n = sum(int(ch) ** 2 for ch in str(n))
            return n == 1
            """,
        )

    if slug in {"isomorphic-strings", "word-pattern"}:
        return note(
            "哈希",
            "双向映射才能保证一一对应，不是只记单边。",
            "维护 `a->b` 和 `b->a` 两张表，冲突就 false。",
            "映射题统一这招，别只写单向。",
            """
            a2b, b2a = {}, {}
            for a, b in zip(s, t):
                if a in a2b and a2b[a] != b: return False
                if b in b2a and b2a[b] != a: return False
                a2b[a] = b
                b2a[b] = a
            return True
            """,
        )

    if slug in {"reverse-linked-list"}:
        return note(
            "链表",
            "反转链表三件套：存 `nxt`，改 `cur.next`，整体前移。",
            "迭代最稳，O(n) / O(1)。",
            "递归也能做，但面试先写迭代。",
            """
            pre, cur = None, head
            while cur:
                nxt = cur.next
                cur.next = pre
                pre, cur = cur, nxt
            return pre
            """,
        )

    if slug in {"contains-duplicate-ii"}:
        return note(
            "哈希",
            "记录每个值上次出现的位置，看距离是否 <= k。",
            "哈希表存最近下标，遍历到当前位就检查距离，O(n)。",
            "滑窗集合也能写，但下标表更直给。",
            """
            last = {}
            for i, x in enumerate(nums):
                if x in last and i - last[x] <= k:
                    return True
                last[x] = i
            return False
            """,
        )

    if slug in {"count-complete-tree-nodes"}:
        return note(
            "树 + 二分",
            "完全二叉树要利用结构：左右高度相等说明左子树满。",
            "每层比较左右高度，满子树节点数可直接算，复杂度 O(log^2 n)。",
            "普通 DFS 也能过但没吃到“完全二叉树”信息。",
            """
            def left_h(node):
                h = 0
                while node:
                    h += 1
                    node = node.left
                return h
            if not root: return 0
            lh, rh = left_h(root.left), left_h(root.right)
            if lh == rh:
                return (1 << lh) + countNodes(root.right)
            return (1 << rh) + countNodes(root.left)
            """,
        )

    if slug in {"invert-binary-tree"}:
        return note(
            "树 DFS",
            "前序或后序都行，核心就是交换左右孩子。",
            "递归到节点就 swap(left, right)，O(n)。",
            "BFS 也能做，但 DFS 最短。",
            """
            def dfs(node):
                if not node: return None
                node.left, node.right = dfs(node.right), dfs(node.left)
                return node
            return dfs(root)
            """,
        )

    if slug in {"summary-ranges"}:
        return note(
            "数组",
            "把连续段的起点记住，一旦断开就结算一段。",
            "顺序扫数组，维护区间开头 `start` 和当前值，O(n)。",
            "这题别想复杂，纯模拟。",
            """
            ans = []
            start = nums[0]
            for i in range(1, len(nums) + 1):
                if i == len(nums) or nums[i] != nums[i - 1] + 1:
                    ans.append(str(start) if start == nums[i - 1] else f"{start}->{nums[i - 1]}")
                    if i < len(nums):
                        start = nums[i]
            return ans
            """,
        )

    if slug in {"palindrome-linked-list"}:
        return note(
            "链表",
            "找中点，反转后半，再头尾对着比。",
            "快慢指针找中点后反转链表后半段，整体 O(n) / O(1)。",
            "如果介意破坏原链表，比较完再反转回去。",
            """
            slow = fast = head
            while fast and fast.next:
                slow = slow.next
                fast = fast.next.next
            pre = None
            while slow:
                nxt = slow.next
                slow.next = pre
                pre, slow = slow, nxt
            while pre:
                if head.val != pre.val: return False
                head, pre = head.next, pre.next
            return True
            """,
        )

    if slug in {"valid-anagram"}:
        return note(
            "计数",
            "字母异位词就比较每个字符出现次数。",
            "直接 `Counter(s) == Counter(t)` 或 26 长度数组计数，O(n)。",
            "若限定小写字母，数组计数更快更省。",
            """
            cnt = [0] * 26
            for ch in s: cnt[ord(ch) - 97] += 1
            for ch in t: cnt[ord(ch) - 97] -= 1
            return all(x == 0 for x in cnt)
            """,
        )

    if slug in {"move-zeroes"}:
        return note(
            "双指针",
            "慢指针前面全是非零，快指针负责把新非零换上来。",
            "遇到非零就和慢指针位置交换，O(n)。",
            "保序且原地，面试主解。",
            """
            slow = 0
            for fast in range(len(nums)):
                if nums[fast] != 0:
                    nums[slow], nums[fast] = nums[fast], nums[slow]
                    slow += 1
            """,
        )

    if slug in {"counting-bits"}:
        return note(
            "位运算 DP",
            "`i` 的 1 个数 = `i >> 1` 的 1 个数 + 最低位是否为 1。",
            "一维 DP 顺推到 `n`，O(n)。",
            "这是比逐个调用 `bit_count()` 更有面试味的写法。",
            """
            dp = [0] * (n + 1)
            for i in range(1, n + 1):
                dp[i] = dp[i >> 1] + (i & 1)
            return dp
            """,
        )

    if slug in {"reverse-vowels-of-a-string"}:
        return note(
            "双指针",
            "左右夹逼，碰到元音才交换。",
            "双指针 + 元音集合判定，O(n)。",
            "这题关键是先转列表，字符串不能原地改。",
            """
            vowels = set('aeiouAEIOU')
            s = list(s)
            l, r = 0, len(s) - 1
            while l < r:
                while l < r and s[l] not in vowels: l += 1
                while l < r and s[r] not in vowels: r -= 1
                s[l], s[r] = s[r], s[l]
                l += 1; r -= 1
            return ''.join(s)
            """,
        )

    if slug in {"ransom-note"}:
        return note(
            "计数",
            "赎金信就是看 magazine 的字符库存够不够。",
            "计数后逐字符扣减，若出现负数就不行。",
            "26 个小写字母就直接开数组。",
            """
            cnt = [0] * 26
            for ch in magazine: cnt[ord(ch) - 97] += 1
            for ch in ransomNote:
                idx = ord(ch) - 97
                cnt[idx] -= 1
                if cnt[idx] < 0: return False
            return True
            """,
        )

    if slug in {"is-subsequence"}:
        return note(
            "双指针",
            "扫长串时顺便匹配短串，匹配成功就推进短串指针。",
            "双指针 O(n)。",
            "如果有大量查询同一个 `t`，再考虑预处理 + 二分。",
            """
            i = 0
            for ch in t:
                if i < len(s) and s[i] == ch:
                    i += 1
            return i == len(s)
            """,
        )

    if slug in {"minimum-absolute-difference-in-bst"}:
        return note(
            "BST",
            "BST 中序有序，只要比较相邻值差值。",
            "中序遍历时维护前驱节点值，顺手更新最小差，O(n)。",
            "别傻算所有点对。",
            """
            ans, prev = float('inf'), None
            def dfs(node):
                nonlocal ans, prev
                if not node: return
                dfs(node.left)
                if prev is not None:
                    ans = min(ans, node.val - prev)
                prev = node.val
                dfs(node.right)
            dfs(root)
            return ans
            """,
        )

    if slug in {"diameter-of-binary-tree"}:
        return note(
            "树 DFS",
            "求深度时顺便更新直径，直径 = 左深 + 右深。",
            "后序 DFS 返回深度，遍历每个节点时更新全局答案。",
            "这是二叉树题里最典型的“返回子树值 + 更新全局值”。",
            """
            ans = 0
            def dfs(node):
                nonlocal ans
                if not node: return 0
                l = dfs(node.left)
                r = dfs(node.right)
                ans = max(ans, l + r)
                return 1 + max(l, r)
            dfs(root)
            return ans
            """,
        )

    if slug in {"can-place-flowers"}:
        return note(
            "贪心",
            "能放就放，因为当前位置不放只会让后面更差。",
            "顺序扫花坛，当前位置和左右都为空时种下，O(n)。",
            "这题贪心是显然正确的局部最优。",
            """
            for i in range(len(flowerbed)):
                if flowerbed[i] == 0:
                    left = i == 0 or flowerbed[i - 1] == 0
                    right = i == len(flowerbed) - 1 or flowerbed[i + 1] == 0
                    if left and right:
                        flowerbed[i] = 1
                        n -= 1
            return n <= 0
            """,
        )

    if slug in {"average-of-levels-in-binary-tree", "maximum-level-sum-of-a-binary-tree"}:
        if slug == "average-of-levels-in-binary-tree":
            return note(
                "树 BFS",
                "层序遍历时顺手累加这一层的和，再除以层大小。",
                "BFS 一层一层弹，复杂度 O(n)。",
                "层题看到 average / max / right view 都是这个套路。",
                """
                ans, q = [], deque([root])
                while q:
                    level_size = len(q)
                    s = 0
                    for _ in range(level_size):
                        node = q.popleft()
                        s += node.val
                        if node.left: q.append(node.left)
                        if node.right: q.append(node.right)
                    ans.append(s / level_size)
                return ans
                """,
            )
        return note(
            "树 BFS",
            "每层累加，记录层和最大的那一层编号。",
            "层序遍历时统计每层和，比较更新答案，O(n)。",
            "DFS 也能做成 `depth -> sum`，但 BFS 更直接。",
            """
            ans, best = 1, -10**18
            level, q = 1, deque([root])
            while q:
                s = 0
                for _ in range(len(q)):
                    node = q.popleft()
                    s += node.val
                    if node.left: q.append(node.left)
                    if node.right: q.append(node.right)
                if s > best:
                    best, ans = s, level
                level += 1
            return ans
            """,
        )

    if slug in {"maximum-average-subarray-i"}:
        return note(
            "滑窗",
            "定长窗口就只做一件事：右边进一个，左边出一个。",
            "先算前 `k` 个和，再滑窗更新最大和，最后除以 `k`。",
            "定长窗口题几乎都长这样。",
            """
            s = sum(nums[:k])
            best = s
            for i in range(k, len(nums)):
                s += nums[i] - nums[i - k]
                best = max(best, s)
            return best / k
            """,
        )

    if slug in {"search-in-a-binary-search-tree"}:
        return note(
            "BST",
            "BST 搜索就按大小往左或往右走。",
            "迭代从根一路下沉，`val < node.val` 去左边，否则去右边。",
            "比 DFS 全树搜索少利用了 BST 性质就亏了。",
            """
            cur = root
            while cur and cur.val != val:
                cur = cur.left if val < cur.val else cur.right
            return cur
            """,
        )

    if slug in {"find-pivot-index"}:
        return note(
            "前缀和",
            "左边和 = 总和 - 左边和 - 当前值。",
            "先拿总和，再顺扫维护左边和，O(n)。",
            "省掉显式前缀数组，空间 O(1)。",
            """
            total = sum(nums)
            left = 0
            for i, x in enumerate(nums):
                if left == total - left - x:
                    return i
                left += x
            return -1
            """,
        )

    if slug in {"min-cost-climbing-stairs"}:
        return note(
            "一维 DP",
            "到达当前台阶的最小花费 = 当前 cost + min(前一阶, 前两阶)。",
            "滚动 DP 即可，答案是最后两阶的较小值。",
            "把“站在台阶上”和“到达楼顶”区分清楚。",
            """
            a = b = 0
            for x in cost:
                a, b = b, x + min(a, b)
            return min(a, b)
            """,
        )

    if slug in {"leaf-similar-trees"}:
        return note(
            "树 DFS",
            "把两棵树的叶子序列各自收集出来再比较。",
            "DFS 遇到叶子就 append，最后比两个列表是否相同。",
            "面试追问可说也能边生成边比较，但列表版最清楚。",
            """
            def leaves(node, out):
                if not node: return
                if not node.left and not node.right:
                    out.append(node.val); return
                leaves(node.left, out)
                leaves(node.right, out)
            a, b = [], []
            leaves(root1, a); leaves(root2, b)
            return a == b
            """,
        )

    if slug in {"number-of-recent-calls"}:
        return note(
            "队列",
            "请求时间单调递增，所以只要维护最近 3000ms 的窗口队列。",
            "新请求入队后，把 `< t-3000` 的请求从队头弹掉。",
            "这是最标准的时间窗口队列题。",
            """
            self.q.append(t)
            while self.q[0] < t - 3000:
                self.q.popleft()
            return len(self.q)
            """,
        )

    if slug in {"greatest-common-divisor-of-strings"}:
        return note(
            "字符串 + 数学",
            "若 `a+b != b+a`，就不存在公共基串；否则长度 gcd 对应的前缀就是答案。",
            "先判拼接等价，再取长度最大公因数，O(n)。",
            "比枚举所有前缀更优雅。",
            """
            if str1 + str2 != str2 + str1:
                return ""
            g = math.gcd(len(str1), len(str2))
            return str1[:g]
            """,
        )

    if slug in {"unique-number-of-occurrences"}:
        return note(
            "哈希",
            "先统计每个值出现次数，再看这些次数是否互不相同。",
            "`Counter` 后把 values 丢进 set，比大小即可。",
            "两层哈希题，模板背住。",
            """
            cnt = Counter(arr)
            return len(set(cnt.values())) == len(cnt)
            """,
        )

    if slug in {"kids-with-the-greatest-number-of-candies"}:
        return note(
            "数组",
            "先找全局最大值，再看每个孩子加完后够不够到它。",
            "两遍扫描，O(n)。",
            "纯模拟题，别绕。",
            """
            mx = max(candies)
            return [x + extraCandies >= mx for x in candies]
            """,
        )

    if slug in {"find-the-highest-altitude"}:
        return note(
            "前缀和",
            "高度变化累加就是前缀和，顺手记录最大前缀。",
            "从 0 开始累加 `gain`，更新最高海拔，O(n)。",
            "无需显式数组，滚动即可。",
            """
            cur = ans = 0
            for x in gain:
                cur += x
                ans = max(ans, cur)
            return ans
            """,
        )

    if slug in {"merge-strings-alternately"}:
        return note(
            "双指针",
            "两个串轮流取字符，剩下的直接拼尾巴。",
            "双指针交替 append，O(m+n)。",
            "就是纯模拟。",
            """
            i = j = 0
            ans = []
            while i < len(word1) or j < len(word2):
                if i < len(word1): ans.append(word1[i]); i += 1
                if j < len(word2): ans.append(word2[j]); j += 1
            return ''.join(ans)
            """,
        )

    if slug in {"find-the-difference-of-two-arrays"}:
        return note(
            "集合",
            "两边转 set，分别做差集。",
            "`set(nums1) - set(nums2)` 与反向各算一次即可。",
            "去重需求天然适合 set。",
            """
            a, b = set(nums1), set(nums2)
            return [list(a - b), list(b - a)]
            """,
        )

    if slug in {"find-repeat-number"}:
        return note(
            "哈希 / 原地",
            "先给 set 判重能过；若追求原地，再用“值放回下标位”的交换法。",
            "面试可过写 set，一次遍历命中重复就返回，O(n)/O(n)。",
            "更优是原地交换到 `nums[i] == i` 的位置，空间 O(1)。",
            """
            seen = set()
            for x in nums:
                if x in seen:
                    return x
                seen.add(x)
            """,
        )

    if slug in {"replace-spaces"}:
        return note(
            "字符串",
            "本质就是把空格替成 `%20`，面试里直接线性构造。",
            "遍历字符，空格 append `%20`，否则原样拼接，O(n)。",
            "Python 里 `s.replace(' ', '%20')` 也能一句话，但手写版更有说明力。",
            """
            ans = []
            for ch in s:
                ans.append('%20' if ch == ' ' else ch)
            return ''.join(ans)
            """,
        )

    if slug in {"reverse-print-linked-list"}:
        return note(
            "链表",
            "倒序打印链表最省事就是先顺序收集，再反转列表。",
            "遍历链表进数组，最后 `ans[::-1]`。",
            "也可用栈或递归；数组反转最直接。",
            """
            ans = []
            while head:
                ans.append(head.val)
                head = head.next
            return ans[::-1]
            """,
        )

    if slug in {"implement-queue-using-stacks"}:
        return note(
            "设计",
            "一个栈负责入，一个栈负责出；出栈空了再整体倒过去。",
            "均摊 O(1) 实现队列。",
            "这题是栈模拟队列的标准模板。",
            """
            def move():
                if not out_st:
                    while in_st:
                        out_st.append(in_st.pop())
            """,
        )

    if slug in {"find-minimum-in-rotated-sorted-array"}:
        return note(
            "二分",
            "旋转数组最小值：看 `mid` 落在哪个有序段。",
            "若 `nums[mid] > nums[r]`，最小值在右边；否则在左边含 `mid`。",
            "有重复时要多加一条 `r -= 1`；本题无重复更简单。",
            """
            l, r = 0, len(nums) - 1
            while l < r:
                mid = (l + r) // 2
                if nums[mid] > nums[r]:
                    l = mid + 1
                else:
                    r = mid
            return nums[l]
            """,
        )

    if slug in {"print-numbers"}:
        return note(
            "数学",
            "本质是输出 `1..10^n-1`。",
            "如果不考虑大数，直接遍历到 `10**n - 1` 即可。",
            "若追问大数越界，再说 DFS 按位生成字符串。",
            """
            return list(range(1, 10 ** n))
            """,
        )

    if slug in {"delete-node-linked-list"}:
        return note(
            "链表",
            "给头结点和值时，挂 dummy 后统一删除。",
            "遍历找到前驱，`pre.next = pre.next.next`。",
            "dummy 是链表删除题万能药。",
            """
            dummy = ListNode(0, head)
            pre = dummy
            while pre.next and pre.next.val != val:
                pre = pre.next
            if pre.next:
                pre.next = pre.next.next
            return dummy.next
            """,
        )

    if slug in {"reorder-array-by-parity"}:
        return note(
            "双指针",
            "奇偶分组题默认双指针：左找偶数，右找奇数，然后交换。",
            "两端夹逼原地重排，O(n)。",
            "若要稳定顺序再考虑额外数组；题里通常不要求稳定。",
            """
            l, r = 0, len(nums) - 1
            while l < r:
                while l < r and nums[l] & 1: l += 1
                while l < r and nums[r] % 2 == 0: r -= 1
                nums[l], nums[r] = nums[r], nums[l]
            return nums
            """,
        )

    if slug in {"kth-node-from-end"}:
        return note(
            "双指针",
            "快指针先走 k 步，再和慢指针一起走。",
            "快到尾时，慢指针正好在倒数第 k 个节点。",
            "链表倒数第 k / 删除倒数第 n 都是这一套。",
            """
            fast = slow = head
            for _ in range(k):
                fast = fast.next
            while fast:
                slow = slow.next
                fast = fast.next
            return slow
            """,
        )

    if slug in {"spiral-matrix"}:
        return note(
            "矩阵",
            "维护上右下左四条边，走完一圈就收缩边界。",
            "模拟即可，注意每次收边界后都要判空。",
            "这是螺旋类矩阵题通用模板。",
            """
            top, bottom = 0, m - 1
            left, right = 0, n - 1
            while top <= bottom and left <= right:
                ...
            """,
        )

    if slug in {"min-stack"}:
        return note(
            "设计",
            "普通栈外再配一个最小栈，保证栈顶就是当前最小值。",
            "push 时同步压最小值，pop 时一起弹，所有操作 O(1)。",
            "这是最小栈标准解。",
            """
            self.st.append(x)
            if not self.min_st or x <= self.min_st[-1]:
                self.min_st.append(x)
            """,
        )

    if slug in {"binary-tree-level-order-traversal-flat", "binary-tree-level-order-traversal", "binary-tree-zigzag-level-order-traversal"}:
        if slug == "binary-tree-level-order-traversal-flat":
            return note(
                "树 BFS",
                "层序遍历拍平版：队列从上到下弹，值直接按顺序收。",
                "普通 BFS，节点值按出队顺序记录即可。",
                "要按层分组就把一层长度先记下来。",
                """
                ans, q = [], deque([root])
                while q:
                    node = q.popleft()
                    ans.append(node.val)
                    if node.left: q.append(node.left)
                    if node.right: q.append(node.right)
                return ans
                """,
            )
        if slug == "binary-tree-level-order-traversal":
            return note(
                "树 BFS",
                "每次先记住当前层节点数，循环弹出这一层。",
                "队列分层，按层收集数组，O(n)。",
                "二叉树层题统一模板。",
                """
                ans, q = [], deque([root])
                while q:
                    level = []
                    for _ in range(len(q)):
                        node = q.popleft()
                        level.append(node.val)
                        if node.left: q.append(node.left)
                        if node.right: q.append(node.right)
                    ans.append(level)
                return ans
                """,
            )
        return note(
            "树 BFS",
            "还是层序，只是奇偶层决定是否反转。",
            "按层 BFS，偶数层正着放，奇数层倒着放。",
            "也可用 `deque` 左右插入避免最后 reverse。",
            """
            ans, q, rev = [], deque([root]), False
            while q:
                level = deque()
                for _ in range(len(q)):
                    node = q.popleft()
                    (level.appendleft if rev else level.append)(node.val)
                    if node.left: q.append(node.left)
                    if node.right: q.append(node.right)
                ans.append(list(level))
                rev = not rev
            return ans
            """,
        )

    if slug in {"smallest-k-elements"}:
        return note(
            "堆",
            "最小的 k 个数，面试先写小根堆或排序，追问再说快选。",
            "Python 直接 `heapq.nsmallest(k, arr)` 或建小根堆弹 k 次。",
            "更优平均 O(n) 是快选，但堆法更稳更短。",
            """
            heapq.heapify(arr)
            return [heapq.heappop(arr) for _ in range(k)]
            """,
        )

    if slug in {"maximum-subarray"}:
        return note(
            "DP / 贪心",
            "Kadane：当前和一旦拖后腿，就从当前位置重新开始。",
            "`cur = max(x, cur + x)`，全程维护最大值，O(n)。",
            "这是最大子数组和的标准最优写法。",
            """
            cur = ans = nums[0]
            for x in nums[1:]:
                cur = max(x, cur + x)
                ans = max(ans, cur)
            return ans
            """,
        )

    if slug in {"first-unique-character"}:
        return note(
            "计数",
            "先统计频次，再按原顺序找第一个频次为 1 的字符。",
            "两遍遍历，O(n)。",
            "哈希即可，不必上复杂结构。",
            """
            cnt = Counter(s)
            for ch in s:
                if cnt[ch] == 1:
                    return ch
            return ' '
            """,
        )

    if slug in {"count-target-in-sorted-array", "missing-number-sorted"}:
        if slug == "count-target-in-sorted-array":
            return note(
                "二分",
                "有序数组统计次数 = 右边界 - 左边界。",
                "分别二分找第一个 `>= target` 和第一个 `> target` 的位置。",
                "别线性扫，浪费有序性。",
                """
                def lower(x):
                    l, r = 0, len(nums)
                    while l < r:
                        mid = (l + r) // 2
                        if nums[mid] >= x: r = mid
                        else: l = mid + 1
                    return l
                return lower(target + 1) - lower(target)
                """,
            )
        return note(
            "二分",
            "缺失数字题看 `nums[mid]` 和 `mid` 是否对得上。",
            "左侧正常区间满足 `nums[mid] == mid`，失配点往右边界缩。",
            "因为数组有序且无重复，二分很自然。",
            """
            l, r = 0, len(nums)
            while l < r:
                mid = (l + r) // 2
                if nums[mid] == mid:
                    l = mid + 1
                else:
                    r = mid
            return l
            """,
        )

    if slug in {"kth-largest-bst"}:
        return note(
            "BST",
            "BST 的倒序中序就是从大到小。",
            "右-中-左遍历，数到第 k 个就返回。",
            "中序有序是 BST 题的核心利用点。",
            """
            ans = k
            def dfs(node):
                nonlocal ans, out
                if not node or ans == 0: return
                dfs(node.right)
                ans -= 1
                if ans == 0:
                    out = node.val
                    return
                dfs(node.left)
            out = None
            dfs(root)
            return out
            """,
        )

    if slug in {"two-sum-ii-input-array-is-sorted"}:
        return note(
            "双指针",
            "有序数组两数和，左右夹逼就行。",
            "和小了左指针右移，和大了右指针左移，O(n)。",
            "比哈希更省空间，面试优先双指针。",
            """
            l, r = 0, len(numbers) - 1
            while l < r:
                s = numbers[l] + numbers[r]
                if s == target: return [l + 1, r + 1]
                if s < target: l += 1
                else: r -= 1
            """,
        )

    if slug in {"find-continuous-sequence"}:
        return note(
            "滑窗",
            "连续正整数求和最适合双指针窗口。",
            "窗口和小了扩右边，大了缩左边，等于 target 就记答案。",
            "因为序列全是正数，窗口和有单调性。",
            """
            l = r = 1
            s, ans = 0, []
            while l <= target // 2:
                if s < target:
                    s += r; r += 1
                elif s > target:
                    s -= l; l += 1
                else:
                    ans.append(list(range(l, r)))
                    s -= l; l += 1
            return ans
            """,
        )

    if slug in {"reverse-words-in-a-string", "left-rotate-string"}:
        if slug == "left-rotate-string":
            return note(
                "字符串",
                "左旋就是前 n 个搬到末尾。",
                "切片拼接最短：`s[n:] + s[:n]`。",
                "如果面试强调原地，再说三次反转。",
                """
                return s[n:] + s[:n]
                """,
            )
        return note(
            "字符串",
            "先切词去掉多余空格，再整体反转词序。",
            "Python 里 `split()` 天然去重空格，最后 `' '.join(reversed(...))`。",
            "若不能用库函数，再手写双指针清空格。",
            """
            return ' '.join(reversed(s.split()))
            """,
        )

    if slug in {"straight-in-poker"}:
        return note(
            "排序 + 贪心",
            "大小王当万能牌，关键看最大最小差值和重复牌。",
            "排序后跳过 0，若有重复非零直接 false，否则看 `max - min < 5`。",
            "这是扑克牌顺子的固定判法。",
            """
            nums.sort()
            joker = nums.count(0)
            for i in range(joker + 1, len(nums)):
                if nums[i] == nums[i - 1]:
                    return False
            return nums[-1] - nums[joker] < 5
            """,
        )

    if slug in {"josephus-problem"}:
        return note(
            "数学",
            "约瑟夫环递推：当前答案由上一轮答案平移得到。",
            "从 `ans = 0` 开始递推 `ans = (ans + m) % i`。",
            "比链表模拟高效太多，O(n)。",
            """
            ans = 0
            for i in range(2, n + 1):
                ans = (ans + m) % i
            return ans
            """,
        )

    if slug in {"add-without-operators"}:
        return note(
            "位运算",
            "异或算无进位和，与后左移算进位；不断迭代直到没进位。",
            "位加法模板题，注意 Python 要处理 32 位截断。",
            "面试里把“异或 = 加法不进位，&<<1 = 进位”说出来就很加分。",
            """
            mask = 0xffffffff
            while b:
                a, b = (a ^ b) & mask, ((a & b) << 1) & mask
            return a if a <= 0x7fffffff else ~(a ^ mask)
            """,
        )

    if slug in {"lowest-common-ancestor-of-a-binary-search-tree", "lowest-common-ancestor-of-a-binary-tree"}:
        if slug == "lowest-common-ancestor-of-a-binary-search-tree":
            return note(
                "BST",
                "BST 最近公共祖先看区间：两个点都小去左，都大去右，夹住当前节点就是答案。",
                "利用 BST 有序性一路下探，O(h)。",
                "比普通二叉树 LCA 简单很多。",
                """
                cur = root
                while cur:
                    if p.val < cur.val and q.val < cur.val:
                        cur = cur.left
                    elif p.val > cur.val and q.val > cur.val:
                        cur = cur.right
                    else:
                        return cur
                """,
            )
        return note(
            "树 DFS",
            "普通二叉树 LCA：左右子树各找到一个时，当前节点就是祖先。",
            "后序递归，若左右都非空返回当前节点，否则返回非空那边。",
            "LCA 是树后序模板题。",
            """
            def dfs(node):
                if not node or node in (p, q): return node
                l = dfs(node.left)
                r = dfs(node.right)
                if l and r: return node
                return l or r
            return dfs(root)
            """,
        )

    if slug in {"add-two-numbers"}:
        return note(
            "链表",
            "链表加法照着竖式做，带一个进位就够了。",
            "同步遍历两条链表，当前位和 = 两节点值 + carry。",
            "dummy + carry 是这类题固定模板。",
            """
            dummy = tail = ListNode(0)
            carry = 0
            while l1 or l2 or carry:
                s = carry
                if l1: s, l1 = s + l1.val, l1.next
                if l2: s, l2 = s + l2.val, l2.next
                tail.next = ListNode(s % 10)
                tail = tail.next
                carry = s // 10
            return dummy.next
            """,
        )

    if slug in {"longest-substring-without-repeating-characters"}:
        return note(
            "滑窗",
            "窗口内不能重复；右边扩张，重复了就缩左边直到合法。",
            "哈希表记录字符最近位置或窗口计数，O(n)。",
            "这是滑窗入门母题，必须肌肉记忆。",
            """
            last = {}
            l = ans = 0
            for r, ch in enumerate(s):
                if ch in last and last[ch] >= l:
                    l = last[ch] + 1
                last[ch] = r
                ans = max(ans, r - l + 1)
            return ans
            """,
        )

    if slug in {"longest-palindromic-substring"}:
        return note(
            "双指针",
            "回文串先想中心扩展：每个点和每个缝都当中心。",
            "枚举 `2n-1` 个中心，向两边扩，O(n^2)。",
            "更优是 Manacher，但面试大多数场景中心扩展就够。",
            """
            def expand(l, r):
                while l >= 0 and r < len(s) and s[l] == s[r]:
                    l -= 1; r += 1
                return l + 1, r - 1
            best = (0, 0)
            for i in range(len(s)):
                for a, b in (expand(i, i), expand(i, i + 1)):
                    if b - a > best[1] - best[0]:
                        best = (a, b)
            return s[best[0]:best[1] + 1]
            """,
        )

    if slug in {"zigzag-conversion"}:
        return note(
            "模拟",
            "按行收字符，方向在向下和向上斜走之间切换。",
            "维护当前行和方向，逐字符放进对应行字符串。",
            "别真的构造二维矩阵，按行收集最简洁。",
            """
            rows = [''] * numRows
            i, step = 0, 1
            for ch in s:
                rows[i] += ch
                if i == 0: step = 1
                if i == numRows - 1: step = -1
                i += step
            return ''.join(rows)
            """,
        )

    if slug in {
        "remove-duplicates-from-sorted-array-ii",
        "factorial-trailing-zeroes",
        "rotate-array",
        "product-of-array-except-self",
        "validate-stack-sequences",
        "arrange-to-smallest-number",
        "max-queue",
        "text-justification",
        "candy",
        "merge-k-sorted-lists",
        "reverse-nodes-in-k-group",
        "sliding-window-maximum",
        "house-robber",
        "binary-tree-right-side-view",
        "serialize-and-deserialize-binary-tree",
    }:
        if slug == "remove-duplicates-from-sorted-array-ii":
            return note(
                "双指针",
                "允许最多保留两个重复值，就让慢指针前面始终是合法数组。",
                "从第 3 个位置开始写，只要 `nums[fast] != nums[slow-2]` 就能保留，O(n)。",
                "比计数重写更简洁，是这题主解。",
                """
                if len(nums) <= 2:
                    return len(nums)
                slow = 2
                for fast in range(2, len(nums)):
                    if nums[fast] != nums[slow - 2]:
                        nums[slow] = nums[fast]
                        slow += 1
                return slow
                """,
            )
        if slug == "factorial-trailing-zeroes":
            return note(
                "数学",
                "尾零只看 5 的个数，因为 2 一定比 5 多。",
                "统计 `n//5 + n//25 + ...` 即可，O(log n)。",
                "这是阶乘尾零标准结论题。",
                """
                ans = 0
                while n:
                    n //= 5
                    ans += n
                return ans
                """,
            )
        if slug == "rotate-array":
            return note(
                "数组",
                "轮转数组最经典是三次反转：整体反，再反前 k，再反后半。",
                "原地 O(n) 时间 O(1) 空间。",
                "额外数组能过，但三次反转是更优主解。",
                """
                k %= len(nums)
                nums.reverse()
                nums[:k] = reversed(nums[:k])
                nums[k:] = reversed(nums[k:])
                """,
            )
        if slug == "product-of-array-except-self":
            return note(
                "前后缀",
                "答案 = 左侧乘积 * 右侧乘积，不用除法。",
                "第一遍写前缀积，第二遍用滚动后缀积乘回去，O(n) / O(1) 额外空间。",
                "这是前后缀模板题，必须会。",
                """
                ans = [1] * len(nums)
                for i in range(1, len(nums)):
                    ans[i] = ans[i - 1] * nums[i - 1]
                suf = 1
                for i in range(len(nums) - 1, -1, -1):
                    ans[i] *= suf
                    suf *= nums[i]
                return ans
                """,
            )
        if slug == "validate-stack-sequences":
            return note(
                "栈",
                "按 pushed 顺序入栈，只要栈顶能匹配 popped 就不断弹。",
                "完整模拟一遍，最后栈空说明合法，O(n)。",
                "这是入栈出栈序列模板题。",
                """
                st = []
                j = 0
                for x in pushed:
                    st.append(x)
                    while st and j < len(popped) and st[-1] == popped[j]:
                        st.pop()
                        j += 1
                return not st
                """,
            )
        if slug == "arrange-to-smallest-number":
            return note(
                "排序",
                "拼接最小值题看比较器：`a+b < b+a` 就让 `a` 在前。",
                "把数字转字符串，自定义排序后直接拼接。",
                "这是“最小数/最大数”类题固定套路。",
                """
                strs = list(map(str, nums))
                strs.sort(key=cmp_to_key(lambda a, b: -1 if a + b < b + a else 1 if a + b > b + a else 0))
                return ''.join(strs)
                """,
            )
        if slug == "max-queue":
            return note(
                "单调队列",
                "普通队列管进出，单调队列管当前最大值。",
                "入队时把尾部更小元素弹掉；出队时若弹出的正好是最大值，单调队列头也一起弹。",
                "这是队列最大值标准设计题。",
                """
                def push_back(x):
                    q.append(x)
                    while max_q and max_q[-1] < x:
                        max_q.pop()
                    max_q.append(x)
                """,
            )
        if slug == "text-justification":
            return note(
                "模拟",
                "先尽量往一行里装单词，再把额外空格平均撒到单词缝里。",
                "最后一行和单词数为 1 的行都左对齐，其余行均匀分配空格。",
                "这题是规则模拟，别怕长，按“分组后格式化”拆开写。",
                """
                line = []
                width = 0
                for word in words:
                    if width + len(line) + len(word) > maxWidth:
                        ans.append(format_line(line, width, maxWidth))
                        line, width = [], 0
                    line.append(word)
                    width += len(word)
                """,
            )
        if slug == "candy":
            return note(
                "贪心",
                "左右相邻约束分别处理：先从左往右保证左规则，再从右往左补右规则。",
                "每个孩子至少 1 颗，两遍扫描后取较大值相加。",
                "这是双向贪心经典题。",
                """
                left = [1] * len(ratings)
                for i in range(1, len(ratings)):
                    if ratings[i] > ratings[i - 1]:
                        left[i] = left[i - 1] + 1
                ans = right = 1
                for i in range(len(ratings) - 2, -1, -1):
                    right = right + 1 if ratings[i] > ratings[i + 1] else 1
                    ans += max(left[i], right)
                return ans
                """,
            )
        if slug == "merge-k-sorted-lists":
            return note(
                "堆 / 分治",
                "K 路有序链表合并，优先队列始终拿当前最小头节点。",
                "把每条链表头丢进小根堆，弹最小再推进该链表下一个，O(N log k)。",
                "也可分治两两合并；面试里堆法更直观。",
                """
                heap = []
                for i, node in enumerate(lists):
                    if node:
                        heappush(heap, (node.val, i, node))
                dummy = tail = ListNode(0)
                while heap:
                    _, i, node = heappop(heap)
                    tail.next = node
                    tail = tail.next
                    if node.next:
                        heappush(heap, (node.next.val, i, node.next))
                return dummy.next
                """,
            )
        if slug == "reverse-nodes-in-k-group":
            return note(
                "链表",
                "每次先看后面够不够 k 个，够就整段反转，不够原样返回。",
                "用 `pre` 指向每段前驱，`tail` 找到段尾，反转后接回去。",
                "这是链表分段反转模板题。",
                """
                dummy = ListNode(0, head)
                pre = dummy
                while True:
                    tail = pre
                    for _ in range(k):
                        tail = tail.next
                        if not tail:
                            return dummy.next
                    nxt = tail.next
                    head, tail = reverse(pre.next, tail)
                    pre.next = head
                    tail.next = nxt
                    pre = tail
                """,
            )
        if slug == "sliding-window-maximum":
            return note(
                "单调队列",
                "窗口最大值就维护一个单调递减队列，队头永远是最大值下标。",
                "新元素进来前弹掉队尾更小值；若队头过期就弹头，O(n)。",
                "这是单调队列母题。",
                """
                dq = deque()
                ans = []
                for i, x in enumerate(nums):
                    while dq and nums[dq[-1]] <= x:
                        dq.pop()
                    dq.append(i)
                    if dq[0] <= i - k:
                        dq.popleft()
                    if i >= k - 1:
                        ans.append(nums[dq[0]])
                return ans
                """,
            )
        if slug == "house-robber":
            return note(
                "一维 DP",
                "打家劫舍就是每间房两种选择：偷它或不偷它。",
                "`dp[i] = max(dp[i-1], dp[i-2] + nums[i])`，可滚动压缩到 O(1)。",
                "这是线性 DP 母题。",
                """
                take = skip = 0
                for x in nums:
                    take, skip = skip + x, max(skip, take)
                return max(take, skip)
                """,
            )
        if slug == "binary-tree-right-side-view":
            return note(
                "树 BFS",
                "每层最后弹出来的那个节点，就是右视图可见节点。",
                "层序遍历，记录每层最后一个值，O(n)。",
                "DFS 也能做成“先右后左 + 记录首次到达深度”。",
                """
                ans = []
                q = deque([root])
                while q:
                    size = len(q)
                    for i in range(size):
                        node = q.popleft()
                        if node.left: q.append(node.left)
                        if node.right: q.append(node.right)
                        if i == size - 1:
                            ans.append(node.val)
                return ans
                """,
            )
        return note(
            "树序列化",
            "序列化二叉树最稳是层序或前序 + 空指针标记，反序列化按同样规则还原。",
            "面试里层序写法最直观：空节点写 `null`，反序列化时队列按父节点接左右孩子。",
            "关键是空节点也要进序列，不然结构还原不出来。",
            """
            # serialize: BFS append value / 'null'
            # deserialize: queue parents, 依次接左右孩子
            """,
        )

    if slug in {"container-with-most-water"}:
        return note(
            "双指针",
            "面积由短板决定，所以每次只移动更短的那一边。",
            "左右夹逼，计算面积并更新答案，O(n)。",
            "这是双指针贪心经典题。",
            """
            l, r, ans = 0, len(height) - 1, 0
            while l < r:
                ans = max(ans, min(height[l], height[r]) * (r - l))
                if height[l] < height[r]:
                    l += 1
                else:
                    r -= 1
            return ans
            """,
        )

    if slug in {"3sum"}:
        return note(
            "排序 + 双指针",
            "三数之和先排序，固定一个数，剩下两个数做两数之和。",
            "排序后枚举 `i`，内部 `l/r` 夹逼，同时处理去重，O(n^2)。",
            "三数题核心是排序 + 去重细节。",
            """
            nums.sort()
            ans = []
            for i in range(len(nums) - 2):
                if i and nums[i] == nums[i - 1]:
                    continue
                l, r = i + 1, len(nums) - 1
                while l < r:
                    s = nums[i] + nums[l] + nums[r]
                    ...
            """,
        )

    if slug in {"letter-combinations-of-a-phone-number", "generate-parentheses", "combination-sum", "permutations", "combinations", "subsets", "word-search", "palindrome-partitioning", "combination-sum-iii", "n-queens", "n-queens-ii", "string-permutation"}:
        family = "回溯"
        memory = "回溯统一模板：做选择，递归，撤销选择。"
        baseline = "用 `path` 表示当前状态，满足条件就收集；注意去重和剪枝。"
        optimized = "去重通常靠排序后跳过同层重复；搜索空间大时尽早剪枝。"
        code = """
        ans, path = [], []
        def dfs(start):
            if done(path):
                ans.append(path[:]); return
            for i in range(start, n):
                path.append(choices[i])
                dfs(i + step)
                path.pop()
        """
        if slug == "word-search":
            return note(
                family,
                "单词搜索就是 DFS + 回溯：从每个起点出发，走一步就标记已访问。",
                "递归匹配 `word[k]`，四连通扩展，失败就撤销访问标记。",
                "常用原地改字符代替 visited 数组，空间更省。",
                """
                def dfs(i, j, k):
                    if board[i][j] != word[k]: return False
                    if k == len(word) - 1: return True
                    ch, board[i][j] = board[i][j], '#'
                    for ni, nj in dirs:
                        if ok and dfs(ni, nj, k + 1): return True
                    board[i][j] = ch
                    return False
                """,
            )
        if slug.startswith("n-queens"):
            return note(
                family,
                "N 皇后本质是按行放皇后，列、主对角、副对角都不能冲突。",
                "回溯按行尝试列位置，三个集合判冲突。",
                "位运算版更快，但集合版面试足够。",
                """
                cols, diag1, diag2 = set(), set(), set()
                def dfs(r):
                    if r == n:
                        ans.append(...)
                        return
                    for c in range(n):
                        if c in cols or r - c in diag1 or r + c in diag2:
                            continue
                        ...
                """,
            )
        return note(family, memory, baseline, optimized, code)

    if slug in {"remove-nth-node-from-end-of-list", "swap-nodes-in-pairs", "rotate-list", "partition-list", "reverse-linked-list-ii", "delete-middle-node-of-a-linked-list", "maximum-twin-sum-of-a-linked-list", "odd-even-linked-list", "copy-list-with-random-pointer", "sort-list"}:
        if slug == "remove-nth-node-from-end-of-list":
            return note(
                "链表",
                "先让快指针走 n 步，再一起走，慢指针停在待删节点前一个。",
                "dummy + 快慢指针，统一删除头结点场景。",
                "链表倒数第 n / 删除第 n 的母题。",
                """
                dummy = ListNode(0, head)
                fast = slow = dummy
                for _ in range(n + 1):
                    fast = fast.next
                while fast:
                    fast = fast.next
                    slow = slow.next
                slow.next = slow.next.next
                return dummy.next
                """,
            )
        if slug == "swap-nodes-in-pairs":
            return note(
                "链表",
                "每次抓两个节点做局部反转，再接回前后链。",
                "dummy 保住头，循环里改 3 根指针。",
                "画清楚四个点：pre, a, b, nxt。",
                """
                dummy = ListNode(0, head)
                pre = dummy
                while pre.next and pre.next.next:
                    a = pre.next
                    b = a.next
                    pre.next, a.next, b.next = b, b.next, a
                    pre = a
                return dummy.next
                """,
            )
        if slug == "rotate-list":
            return note(
                "链表",
                "先算长度并成环，再在新尾处断开。",
                "新头 = 第 `n-k%n` 个节点之后那个点。",
                "这是旋转链表标准做法。",
                """
                n, cur = 1, head
                while cur.next:
                    cur = cur.next; n += 1
                cur.next = head
                k = n - k % n
                while k:
                    cur = cur.next
                    k -= 1
                new_head = cur.next
                cur.next = None
                return new_head
                """,
            )
        if slug == "reverse-linked-list-ii":
            return note(
                "链表",
                "局部反转先走到 left 前一位，再把后面的节点头插进区间前端。",
                "头插法一次次把 `cur.next` 摘出来插到 `pre` 后面。",
                "这题是区间反转模板。",
                """
                dummy = ListNode(0, head)
                pre = dummy
                for _ in range(left - 1): pre = pre.next
                cur = pre.next
                for _ in range(right - left):
                    nxt = cur.next
                    cur.next = nxt.next
                    nxt.next = pre.next
                    pre.next = nxt
                return dummy.next
                """,
            )
        if slug == "copy-list-with-random-pointer":
            return note(
                "链表",
                "哈希表先建老节点到新节点映射，再补 next/random。",
                "两遍遍历最清楚，O(n) 时间 O(n) 空间。",
                "更优 O(1) 空间是穿插复制，但哈希版更适合面试先答主解。",
                """
                mp = {}
                cur = head
                while cur:
                    mp[cur] = Node(cur.val)
                    cur = cur.next
                cur = head
                while cur:
                    mp[cur].next = mp.get(cur.next)
                    mp[cur].random = mp.get(cur.random)
                    cur = cur.next
                return mp.get(head)
                """,
            )
        if slug == "sort-list":
            return note(
                "链表 + 归并",
                "链表排序优先归并：找中点拆开，递归排左右，再合并。",
                "链表无法随机访问，不适合快排；归并 O(n log n) 最稳。",
                "中点用快慢指针找。",
                """
                def sort(head):
                    if not head or not head.next: return head
                    slow = fast = head
                    pre = None
                    while fast and fast.next:
                        pre, slow, fast = slow, slow.next, fast.next.next
                    pre.next = None
                    return merge(sort(head), sort(slow))
                """,
            )
        if slug == "delete-middle-node-of-a-linked-list":
            return note(
                "链表",
                "快慢指针找中点，记录慢指针前驱并删掉它。",
                "快一次走两步，慢一次走一步，最终慢在中点。",
                "只有一个节点时直接返回 None。",
                """
                if not head.next: return None
                slow = fast = head
                pre = None
                while fast and fast.next:
                    pre = slow
                    slow = slow.next
                    fast = fast.next.next
                pre.next = slow.next
                return head
                """,
            )
        if slug == "maximum-twin-sum-of-a-linked-list":
            return note(
                "链表",
                "找中点，反转后半，前后一起扫求最大和。",
                "链表回文题的变形，O(n) / O(1)。",
                "会回文链表，这题就顺手做出来。",
                """
                slow = fast = head
                while fast and fast.next:
                    slow = slow.next
                    fast = fast.next.next
                pre = None
                while slow:
                    nxt = slow.next
                    slow.next = pre
                    pre, slow = slow, nxt
                ans = 0
                while pre:
                    ans = max(ans, head.val + pre.val)
                    head, pre = head.next, pre.next
                return ans
                """,
            )
        if slug == "odd-even-linked-list":
            return note(
                "链表",
                "奇链表和偶链表分别串起来，最后把奇尾接偶头。",
                "维护 odd / even 两条链，按位置分组，O(n)。",
                "这是链表重排模板题。",
                """
                odd, even = head, head.next
                even_head = even
                while even and even.next:
                    odd.next = even.next
                    odd = odd.next
                    even.next = odd.next
                    even = even.next
                odd.next = even_head
                return head
                """,
            )

    if slug in {"next-permutation"}:
        return note(
            "数组",
            "从右往左找第一个下降点，再找右侧刚好比它大的数交换，最后把尾部升序化。",
            "标准步骤：找拐点 -> 找替换 -> 交换 -> 反转后缀。",
            "这是排列题必须会的模板。",
            """
            i = len(nums) - 2
            while i >= 0 and nums[i] >= nums[i + 1]:
                i -= 1
            if i >= 0:
                j = len(nums) - 1
                while nums[j] <= nums[i]:
                    j -= 1
                nums[i], nums[j] = nums[j], nums[i]
            nums[i + 1:] = reversed(nums[i + 1:])
            """,
        )

    if slug in {"search-in-rotated-sorted-array", "find-first-and-last-position-of-element-in-sorted-array", "search-a-2d-matrix", "search-a-2d-matrix-ii", "search-sorted-matrix-from-corner", "find-peak-element", "koko-eating-bananas", "successful-pairs-of-spells-and-potions", "median-of-two-sorted-arrays"}:
        if slug == "search-in-rotated-sorted-array":
            return note(
                "二分",
                "旋转数组二分先判哪半边有序，再看 target 落不落在这半边。",
                "每轮至少有一边有序，按有序段缩区间，O(log n)。",
                "这是旋转数组搜索标准模板。",
                """
                l, r = 0, len(nums) - 1
                while l <= r:
                    mid = (l + r) // 2
                    if nums[mid] == target: return mid
                    if nums[l] <= nums[mid]:
                        if nums[l] <= target < nums[mid]:
                            r = mid - 1
                        else:
                            l = mid + 1
                    else:
                        ...
                return -1
                """,
            )
        if slug == "find-first-and-last-position-of-element-in-sorted-array":
            return note(
                "二分",
                "两次 lower_bound：找第一个 `>= target` 和第一个 `> target`。",
                "左右边界分开二分，复杂度 O(log n)。",
                "这是边界二分经典题。",
                """
                def lower(x):
                    l, r = 0, len(nums)
                    while l < r:
                        mid = (l + r) // 2
                        if nums[mid] >= x: r = mid
                        else: l = mid + 1
                    return l
                l = lower(target)
                r = lower(target + 1) - 1
                return [l, r] if l < len(nums) and nums[l] == target else [-1, -1]
                """,
            )
        if slug == "search-a-2d-matrix":
            return note(
                "二分",
                "整张矩阵按行拍平成一个有序数组来二分。",
                "下标换算 `mid -> row, col`，O(log(mn))。",
                "因为每行首元素大于上一行尾元素，所以能整体看成有序。",
                """
                m, n = len(matrix), len(matrix[0])
                l, r = 0, m * n
                while l < r:
                    mid = (l + r) // 2
                    x = matrix[mid // n][mid % n]
                    if x >= target: r = mid
                    else: l = mid + 1
                return l < m * n and matrix[l // n][l % n] == target
                """,
            )
        if slug in {"search-a-2d-matrix-ii", "search-sorted-matrix-from-corner"}:
            return note(
                "二分 / 矩阵",
                "从右上角出发：大了往左，小了往下，一步排掉一行或一列。",
                "利用行列双有序，复杂度 O(m+n)。",
                "这是二维有序矩阵查找标准走法。",
                """
                i, j = 0, len(matrix[0]) - 1
                while i < len(matrix) and j >= 0:
                    if matrix[i][j] == target: return True
                    if matrix[i][j] > target: j -= 1
                    else: i += 1
                return False
                """,
            )
        if slug == "find-peak-element":
            return note(
                "二分",
                "看 `mid` 和右边谁大：往更高那边走一定能找到峰值。",
                "若 `nums[mid] > nums[mid+1]`，峰值在左侧含 mid，否则在右侧。",
                "不需要真的找最大值，单调性已经够用。",
                """
                l, r = 0, len(nums) - 1
                while l < r:
                    mid = (l + r) // 2
                    if nums[mid] > nums[mid + 1]:
                        r = mid
                    else:
                        l = mid + 1
                return l
                """,
            )
        if slug == "koko-eating-bananas":
            return note(
                "二分答案",
                "速度越快越容易吃完，答案满足单调性，直接二分速度。",
                "写 `check(k)` 统计总小时数是否 <= h，然后二分最小速度。",
                "这类“最小满足条件”题都往二分答案想。",
                """
                def check(k):
                    return sum((x + k - 1) // k for x in piles) <= h
                l, r = 1, max(piles)
                while l < r:
                    mid = (l + r) // 2
                    if check(mid): r = mid
                    else: l = mid + 1
                return l
                """,
            )
        if slug == "successful-pairs-of-spells-and-potions":
            return note(
                "排序 + 二分",
                "药水排序后，对每个咒语二分第一个满足乘积 >= success 的位置。",
                "排序一次，再对每个 spell 做 lower_bound，O((n+m)log m)。",
                "比双重循环省太多。",
                """
                potions.sort()
                ans = []
                for x in spells:
                    need = (success + x - 1) // x
                    i = bisect_left(potions, need)
                    ans.append(len(potions) - i)
                return ans
                """,
            )
        return note(
            "二分",
            "两个有序数组找中位数，核心是二分分割点让左右两边元素个数平衡。",
            "在较短数组上二分 `i`，推出另一个数组分割点 `j`，满足左边最大 <= 右边最小。",
            "这是困难题里非常经典的分割二分。",
            """
            # 在较短数组上二分 cut
            # 保证 left_max <= right_min
            """,
        )

    if slug in {"valid-sudoku"}:
        return note(
            "哈希",
            "行、列、九宫格分别判重。",
            "三个集合数组同步维护，一旦重复直接 false。",
            "这是数独校验模板。",
            """
            rows = [set() for _ in range(9)]
            cols = [set() for _ in range(9)]
            boxes = [set() for _ in range(9)]
            """,
        )

    if slug in {"jump-game-ii", "jump-game"}:
        if slug == "jump-game":
            return note(
                "贪心",
                "维护当前能到的最远位置，只要没断就能继续。",
                "遍历时更新 `far = max(far, i + nums[i])`，若 `i > far` 说明断了。",
                "这题贪心比 DP 更优。",
                """
                far = 0
                for i, x in enumerate(nums):
                    if i > far: return False
                    far = max(far, i + x)
                return True
                """,
            )
        return note(
            "贪心",
            "按层 BFS 思想：当前步数能覆盖的区间扫完时，必须再跳一步。",
            "遍历到当前边界就加一步，并把边界更新为这一层能到的最远点。",
            "这是比 DP 更优的 O(n) 解。",
            """
            ans = end = far = 0
            for i in range(len(nums) - 1):
                far = max(far, i + nums[i])
                if i == end:
                    ans += 1
                    end = far
            return ans
            """,
        )

    if slug in {"group-anagrams"}:
        return note(
            "哈希",
            "异位词分组关键是找统一 key：排序后字符串或 26 维计数。",
            "哈希表按 key 聚合列表，O(n * k log k)。",
            "追求更优就用字符计数 tuple 当 key，避免排序。",
            """
            groups = defaultdict(list)
            for s in strs:
                key = tuple(sorted(s))
                groups[key].append(s)
            return list(groups.values())
            """,
        )

    if slug in {"powx-n"}:
        return note(
            "快速幂",
            "指数每次折半，当前位是 1 就把底数乘进答案。",
            "二进制快速幂，O(log n)。",
            "负指数先转成正指数，再最后取倒数。",
            """
            if n < 0:
                x, n = 1 / x, -n
            ans = 1
            while n:
                if n & 1:
                    ans *= x
                x *= x
                n >>= 1
            return ans
            """,
        )

    if slug in {"merge-intervals", "insert-interval", "non-overlapping-intervals", "minimum-number-of-arrows-to-burst-balloons"}:
        if slug == "merge-intervals":
            return note(
                "区间",
                "区间题先按起点排序，再顺着合并。",
                "若当前区间起点 <= 上一个区间终点，就能合并。",
                "排序 + 扫描是区间母题。",
                """
                intervals.sort()
                ans = [intervals[0]]
                for s, e in intervals[1:]:
                    if s <= ans[-1][1]:
                        ans[-1][1] = max(ans[-1][1], e)
                    else:
                        ans.append([s, e])
                return ans
                """,
            )
        if slug == "insert-interval":
            return note(
                "区间",
                "先收左边完全不重叠的，再合并中间重叠段，最后接右边。",
                "因为原数组已按起点排序，所以线性扫描就够了。",
                "插入区间本质还是区间合并。",
                """
                ans = []
                i = 0
                while i < n and intervals[i][1] < new[0]:
                    ans.append(intervals[i]); i += 1
                while i < n and intervals[i][0] <= new[1]:
                    new[0] = min(new[0], intervals[i][0])
                    new[1] = max(new[1], intervals[i][1])
                    i += 1
                ans.append(new)
                return ans + intervals[i:]
                """,
            )
        if slug == "non-overlapping-intervals":
            return note(
                "贪心",
                "想保留最多区间，就优先留下结束最早的。",
                "按结束点排序，当前区间若和上一个保留区间重叠就删除它。",
                "这是区间调度经典贪心。",
                """
                intervals.sort(key=lambda x: x[1])
                end = intervals[0][1]
                keep = 1
                for s, e in intervals[1:]:
                    if s >= end:
                        keep += 1
                        end = e
                return len(intervals) - keep
                """,
            )
        return note(
            "贪心",
            "射气球要尽量复用同一支箭，所以优先按右端点排序。",
            "当前气球起点若大于上一箭位置，就必须新开一箭。",
            "区间最少点覆盖的经典模型。",
            """
            points.sort(key=lambda x: x[1])
            ans = 1
            end = points[0][1]
            for s, e in points[1:]:
                if s > end:
                    ans += 1
                    end = e
            return ans
            """,
        )

    if slug in {"unique-paths", "unique-paths-ii", "minimum-path-sum", "triangle", "max-value-of-gifts"}:
        if slug == "unique-paths":
            return note(
                "二维 DP",
                "走格子题先写 `dp[i][j] = 上 + 左`。",
                "初始化首行首列为 1，其他位置由上左转移，O(mn)。",
                "能压缩成一维数组。",
                """
                dp = [1] * n
                for _ in range(1, m):
                    for j in range(1, n):
                        dp[j] += dp[j - 1]
                return dp[-1]
                """,
            )
        if slug == "unique-paths-ii":
            return note(
                "二维 DP",
                "带障碍的走格子：障碍位置直接置 0。",
                "状态仍是上 + 左，只是遇障碍不能到达。",
                "首行首列初始化注意被障碍截断。",
                """
                dp = [0] * n
                dp[0] = 1
                for i in range(m):
                    for j in range(n):
                        if obstacleGrid[i][j]:
                            dp[j] = 0
                        elif j > 0:
                            dp[j] += dp[j - 1]
                return dp[-1]
                """,
            )
        if slug in {"minimum-path-sum", "max-value-of-gifts"}:
            return note(
                "二维 DP",
                "网格路径题：当前位置最优值只来自上边或左边。",
                "最小路径和写 `min`，礼物最大值写 `max`。",
                "本质是一类题，状态定义一致。",
                """
                dp = [[0] * n for _ in range(m)]
                for i in range(m):
                    for j in range(n):
                        dp[i][j] = grid[i][j] + best_from_up_left
                return dp[-1][-1]
                """,
            )
        return note(
            "二维 DP",
            "三角形从底往上推最省事：当前位置 += 下层相邻两个里的较优值。",
            "自底向上原地 DP，O(n^2) 时间 O(1) 额外空间。",
            "比从顶到底写边界更顺。",
            """
            dp = triangle[-1][:]
            for i in range(len(triangle) - 2, -1, -1):
                for j in range(i + 1):
                    dp[j] = triangle[i][j] + min(dp[j], dp[j + 1])
            return dp[0]
            """,
        )

    if slug in {"simplify-path"}:
        return note(
            "栈",
            "路径化简就是目录栈：正常目录入栈，`.` 忽略，`..` 出栈。",
            "按 `/` 切开后模拟即可。",
            "路径题本质是栈模拟。",
            """
            st = []
            for part in path.split('/'):
                if part in ('', '.'):
                    continue
                if part == '..':
                    if st: st.pop()
                else:
                    st.append(part)
            return '/' + '/'.join(st)
            """,
        )

    if slug in {"edit-distance", "interleaving-string", "longest-common-subsequence"}:
        if slug == "edit-distance":
            return note(
                "二维 DP",
                "编辑距离三操作：增删改，对应三个来源状态。",
                "`dp[i][j]` 表示前缀最小编辑次数，转移看左、上、左上。",
                "这是字符串 DP 经典题。",
                """
                dp = [[0] * (n + 1) for _ in range(m + 1)]
                for i in range(m + 1): dp[i][0] = i
                for j in range(n + 1): dp[0][j] = j
                for i in range(1, m + 1):
                    for j in range(1, n + 1):
                        ...
                """,
            )
        if slug == "interleaving-string":
            return note(
                "二维 DP",
                "交错字符串看前缀：`s3[:i+j]` 能否由 `s1[:i]` 和 `s2[:j]` 组成。",
                "状态只依赖上边和左边，O(mn)。",
                "先判长度是否相等再 DP。",
                """
                if len(s1) + len(s2) != len(s3): return False
                dp = [[False] * (len(s2) + 1) for _ in range(len(s1) + 1)]
                dp[0][0] = True
                ...
                return dp[-1][-1]
                """,
            )
        return note(
            "二维 DP",
            "LCS：字符相同就继承左上 + 1，不同就取上或左最大。",
            "经典二维 DP，O(mn)。",
            "面试常问状态定义和转移。",
            """
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if a[i - 1] == b[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1] + 1
                    else:
                        dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
            return dp[m][n]
            """,
        )

    if slug in {"set-matrix-zeroes", "rotate-image", "game-of-life"}:
        if slug == "rotate-image":
            return note(
                "矩阵",
                "顺时针旋转 90 度 = 先转置，再每行反转。",
                "原地两步做完，O(n^2)。",
                "这是矩阵旋转标准解。",
                """
                n = len(matrix)
                for i in range(n):
                    for j in range(i + 1, n):
                        matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
                for row in matrix:
                    row.reverse()
                """,
            )
        if slug == "set-matrix-zeroes":
            return note(
                "矩阵",
                "用首行首列当标记位，避免额外 O(mn) 空间。",
                "第一遍打标，第二遍清零，最后处理首行首列。",
                "面试常追问 O(1) 额外空间版本。",
                """
                row0 = any(matrix[0][j] == 0 for j in range(n))
                col0 = any(matrix[i][0] == 0 for i in range(m))
                ...
                """,
            )
        return note(
            "矩阵",
            "生命游戏要同时读旧值写新值，所以用状态编码原地过渡。",
            "比如 `0->1` 记成 2，`1->0` 记成 -1，最后再统一归一。",
            "这样能做到 O(1) 额外空间。",
            """
            for i in range(m):
                for j in range(n):
                    live = count_neighbors(i, j)
                    if board[i][j] == 1 and (live < 2 or live > 3):
                        board[i][j] = -1
                    if board[i][j] == 0 and live == 3:
                        board[i][j] = 2
            """,
        )

    if slug in {"sort-colors"}:
        return note(
            "双指针",
            "荷兰国旗：小于 pivot 放左边，大于 pivot 放右边，等于留中间。",
            "三个指针 `l, i, r` 原地分三段，O(n)。",
            "面试必须会的三色分类模板。",
            """
            l, i, r = 0, 0, len(nums) - 1
            while i <= r:
                if nums[i] == 0:
                    nums[l], nums[i] = nums[i], nums[l]
                    l += 1; i += 1
                elif nums[i] == 2:
                    nums[r], nums[i] = nums[i], nums[r]
                    r -= 1
                else:
                    i += 1
            """,
        )

    if slug in {"validate-binary-search-tree", "binary-search-tree-iterator", "kth-smallest-element-in-a-bst", "delete-node-in-a-bst", "verify-postorder-of-bst", "convert-bst-to-doubly-linked-list"}:
        if slug == "validate-binary-search-tree":
            return note(
                "BST",
                "验证 BST 最稳是上下界递归：每个节点必须落在合法区间里。",
                "DFS 传 `low/high`，当前值必须满足 `low < val < high`。",
                "比只比较父子更严谨。",
                """
                def dfs(node, low, high):
                    if not node: return True
                    if not (low < node.val < high): return False
                    return dfs(node.left, low, node.val) and dfs(node.right, node.val, high)
                return dfs(root, -inf, inf)
                """,
            )
        if slug == "binary-search-tree-iterator":
            return note(
                "设计",
                "BST 迭代器本质是受控中序，把左链先全部压栈。",
                "`next()` 弹栈顶，再把其右子树的左链压进去。",
                "均摊 O(1)。",
                """
                def push_left(node):
                    while node:
                        st.append(node)
                        node = node.left
                """,
            )
        if slug == "kth-smallest-element-in-a-bst":
            return note(
                "BST",
                "BST 中序有序，数到第 k 个就是答案。",
                "迭代中序遍历时递减 `k`，为 0 就返回。",
                "比先存完整数组更省空间。",
                """
                st = []
                cur = root
                while st or cur:
                    while cur:
                        st.append(cur); cur = cur.left
                    cur = st.pop()
                    k -= 1
                    if k == 0: return cur.val
                    cur = cur.right
                """,
            )
        if slug == "delete-node-in-a-bst":
            return note(
                "BST",
                "BST 删除分三种：0 个孩子直接删，1 个孩子顶替，2 个孩子找后继替换。",
                "删除后继续保持 BST 性质。",
                "面试里把三种情况说明白就够。",
                """
                if key < root.val:
                    root.left = deleteNode(root.left, key)
                elif key > root.val:
                    root.right = deleteNode(root.right, key)
                else:
                    ...
                return root
                """,
            )
        if slug == "verify-postorder-of-bst":
            return note(
                "分治",
                "后序最后一个是根，左边都小于根，右边都大于根，再递归验证左右段。",
                "递归分段能过，平均 O(n log n)。",
                "面试可补充单调栈倒序写法更优。",
                """
                def dfs(l, r):
                    if l >= r: return True
                    root = postorder[r]
                    m = l
                    while postorder[m] < root: m += 1
                    for i in range(m, r):
                        if postorder[i] < root: return False
                    return dfs(l, m - 1) and dfs(m, r - 1)
                """,
            )
        return note(
            "BST",
            "BST 转双向链表就做中序，把前驱和当前节点双向连起来。",
            "中序保证有序，最后首尾相连。",
            "这是树转链表常见模板。",
            """
            pre = head = None
            def dfs(node):
                nonlocal pre, head
                if not node: return
                dfs(node.left)
                ...
                dfs(node.right)
            """,
        )

    if slug in {"construct-binary-tree-from-preorder-and-inorder-traversal", "construct-binary-tree-from-inorder-and-postorder-traversal"}:
        if slug == "construct-binary-tree-from-preorder-and-inorder-traversal":
            return note(
                "分治",
                "前序第一个是根，在中序里找到它，就能切出左右子树范围。",
                "哈希表记录中序下标，递归建左右子树，O(n)。",
                "构树题核心是“一个遍历给根，另一个遍历给区间”。",
                """
                pos = {x: i for i, x in enumerate(inorder)}
                def build(pl, pr, il, ir):
                    if pl > pr: return None
                    root = TreeNode(preorder[pl])
                    k = pos[preorder[pl]]
                    left = k - il
                    root.left = build(pl + 1, pl + left, il, k - 1)
                    root.right = build(pl + left + 1, pr, k + 1, ir)
                    return root
                """,
            )
        return note(
            "分治",
            "后序最后一个是根，在中序里找到它，左右区间就切开了。",
            "哈希表 + 递归，O(n)。",
            "和前序/中序构树同一模板，换一下根的位置即可。",
            """
            pos = {x: i for i, x in enumerate(inorder)}
            def build(il, ir, pl, pr):
                if il > ir: return None
                root = TreeNode(postorder[pr])
                k = pos[postorder[pr]]
                left = k - il
                root.left = build(il, k - 1, pl, pl + left - 1)
                root.right = build(k + 1, ir, pl + left, pr - 1)
                return root
            """,
        )

    if slug in {"flatten-binary-tree-to-linked-list"}:
        return note(
            "树 DFS",
            "后序更顺：先把左右子树拉平，再把左链挂到右边。",
            "递归返回后，将左子树插到右子树前，再找到尾巴接原右子树。",
            "也可反向前序用 `prev` 指针一路串。",
            """
            def dfs(node):
                if not node: return
                dfs(node.left); dfs(node.right)
                left, right = node.left, node.right
                node.left = None
                node.right = left
                cur = node
                while cur.right:
                    cur = cur.right
                cur.right = right
            """,
        )

    if slug in {"best-time-to-buy-and-sell-stock-ii", "best-time-to-buy-and-sell-stock-with-transaction-fee", "best-time-to-buy-and-sell-stock-iii", "best-time-to-buy-and-sell-stock-iv"}:
        if slug == "best-time-to-buy-and-sell-stock-ii":
            return note(
                "贪心",
                "能赚就赚，把所有上升段利润加起来。",
                "相邻两天只要今天比昨天高，就把差值计入答案。",
                "无限次交易题直接贪心。",
                """
                ans = 0
                for i in range(1, len(prices)):
                    ans += max(0, prices[i] - prices[i - 1])
                return ans
                """,
            )
        if slug == "best-time-to-buy-and-sell-stock-with-transaction-fee":
            return note(
                "状态 DP",
                "持股 / 不持股两状态滚动，手续费放在买或卖时扣都行。",
                "`hold` 表示当前持股最大收益，`cash` 表示不持股最大收益。",
                "股票 DP 先背状态转移。",
                """
                hold, cash = -prices[0], 0
                for p in prices[1:]:
                    hold = max(hold, cash - p)
                    cash = max(cash, hold + p - fee)
                return cash
                """,
            )
        if slug == "best-time-to-buy-and-sell-stock-iii":
            return note(
                "状态 DP",
                "最多两次交易，直接开 4 个状态：买1、卖1、买2、卖2。",
                "逐价格更新四个状态，O(n) / O(1)。",
                "比二维 DP 更容易现场手写。",
                """
                buy1 = buy2 = -10**18
                sell1 = sell2 = 0
                for p in prices:
                    buy1 = max(buy1, -p)
                    sell1 = max(sell1, buy1 + p)
                    buy2 = max(buy2, sell1 - p)
                    sell2 = max(sell2, buy2 + p)
                return sell2
                """,
            )
        return note(
            "状态 DP",
            "最多 k 次交易就把“买/卖”状态拉成 `2k` 个状态滚动更新。",
            "若 `k >= n/2` 退化成无限次交易贪心。",
            "股票 IV 核心是状态机 DP。",
            """
            if k >= len(prices) // 2:
                ...
            buy = [-10**18] * (k + 1)
            sell = [0] * (k + 1)
            """,
        )

    if slug in {"longest-consecutive-sequence"}:
        return note(
            "哈希",
            "只从连续序列的起点开始往后数，避免重复统计。",
            "把元素放进 set，若 `x-1` 不在集合里，才从 `x` 开始扩，O(n)。",
            "这是哈希优化暴力的经典题。",
            """
            st = set(nums)
            ans = 0
            for x in st:
                if x - 1 not in st:
                    y = x
                    while y in st:
                        y += 1
                    ans = max(ans, y - x)
            return ans
            """,
        )

    if slug in {"sum-root-to-leaf-numbers"}:
        return note(
            "树 DFS",
            "路径上的数字前缀一路乘 10 再加当前位。",
            "DFS 传当前值，到叶子时累加到答案。",
            "这类路径聚合题都用参数带状态。",
            """
            def dfs(node, cur):
                if not node: return 0
                cur = cur * 10 + node.val
                if not node.left and not node.right:
                    return cur
                return dfs(node.left, cur) + dfs(node.right, cur)
            return dfs(root, 0)
            """,
        )

    if slug in {"surrounded-regions"}:
        return note(
            "图",
            "边界上的 O 不能被围住，所以先从边界 O 出发标记安全区。",
            "DFS/BFS 把安全 O 标成特殊字符，最后未标记的 O 变 X。",
            "这题本质是边界泛洪。",
            """
            for border_o in border_cells:
                bfs_mark(border_o)
            for i in range(m):
                for j in range(n):
                    ...
            """,
        )

    if slug in {"clone-graph"}:
        return note(
            "图",
            "克隆图一定要有 `原节点 -> 新节点` 映射，防止重复建和死循环。",
            "DFS/BFS 都能做，遇到新节点先建副本再递归邻居。",
            "图复制题模板。",
            """
            mp = {}
            def dfs(node):
                if node in mp: return mp[node]
                copy = Node(node.val)
                mp[node] = copy
                for nei in node.neighbors:
                    copy.neighbors.append(dfs(nei))
                return copy
            """,
        )

    if slug in {"gas-station"}:
        return note(
            "贪心",
            "总油量不够直接无解；够的话，从某点失败就说明这段起点都不可能。",
            "累计油量一旦为负，下一站重开起点。",
            "这是经典贪心证明题。",
            """
            if sum(gas) < sum(cost): return -1
            start = cur = 0
            for i in range(len(gas)):
                cur += gas[i] - cost[i]
                if cur < 0:
                    start = i + 1
                    cur = 0
            return start
            """,
        )

    if slug in {"single-number-ii"}:
        return note(
            "位运算",
            "每一位单独统计，出现 3 次的位最终 `% 3` 会被消掉。",
            "按 32 位统计 1 的个数，对 3 取模后重建答案。",
            "比哈希省空间，也更像面试。",
            """
            ans = 0
            for b in range(32):
                s = sum((x >> b) & 1 for x in nums)
                if s % 3:
                    ans |= 1 << b
            return ans if ans < 1 << 31 else ans - (1 << 32)
            """,
        )

    if slug in {"word-break"}:
        return note(
            "DP",
            "`dp[i]` 表示前 i 个字符能否被字典拼出来。",
            "枚举切分点 `j`，若 `dp[j]` 为真且 `s[j:i]` 在字典里，则 `dp[i]=True`。",
            "哈希集合存单词，避免线性查找。",
            """
            wordSet = set(wordDict)
            dp = [False] * (len(s) + 1)
            dp[0] = True
            for i in range(1, len(s) + 1):
                for j in range(i):
                    if dp[j] and s[j:i] in wordSet:
                        dp[i] = True
                        break
            return dp[-1]
            """,
        )

    if slug in {"lru-cache"}:
        return note(
            "设计",
            "LRU = 哈希表定位节点 + 双向链表维护最近使用顺序。",
            "`get/put` 都要把节点挪到头部，超容量删尾节点。",
            "Python 面试可直接说 `OrderedDict`，但手写版更扎实。",
            """
            # key -> node
            # 双向链表: head <-> ... <-> tail
            # 访问节点后 move_to_head(node)
            """,
        )

    if slug in {"evaluate-reverse-polish-notation"}:
        return note(
            "栈",
            "逆波兰表达式遇数字入栈，遇操作符就弹两个数计算后再压回。",
            "栈模拟即可，O(n)。",
            "注意减法和除法的操作数顺序。",
            """
            st = []
            for tok in tokens:
                if tok not in '+-*/':
                    st.append(int(tok))
                else:
                    b = st.pop(); a = st.pop()
                    st.append(calc(a, b, tok))
            return st[-1]
            """,
        )

    if slug in {"maximum-product-subarray"}:
        return note(
            "DP",
            "乘积题要同时维护最大值和最小值，因为负数会翻转身份。",
            "遍历时更新 `mx` / `mn`，答案取全局最大。",
            "这是和最大子数组和不同的关键点。",
            """
            mx = mn = ans = nums[0]
            for x in nums[1:]:
                cand = (x, mx * x, mn * x)
                mx, mn = max(cand), min(cand)
                ans = max(ans, mx)
            return ans
            """,
        )

    if slug in {"trailing-zeroes"}:
        return note(
            "数学",
            "尾零来自因子 10，而 10 = 2 * 5，瓶颈是 5 的个数。",
            "统计 `n/5 + n/25 + n/125 + ...`。",
            "这是阶乘零的标准公式。",
            """
            ans = 0
            while n:
                n //= 5
                ans += n
            return ans
            """,
        )

    if slug in {"number-of-islands", "rotting-oranges", "nearest-exit-from-entrance-in-maze", "keys-and-rooms", "number-of-provinces", "snakes-and-ladders", "word-ladder", "minimum-genetic-mutation", "reorder-routes-to-make-all-paths-lead-to-the-city-zero", "course-schedule", "course-schedule-ii"}:
        if slug == "number-of-islands":
            return note(
                "图",
                "见到连通块数量，默认 DFS/BFS 淹掉一整块。",
                "遍历网格，碰到陆地就答案加一并 flood fill，O(mn)。",
                "图中连通块统计母题。",
                """
                def dfs(i, j):
                    if out or grid[i][j] != '1': return
                    grid[i][j] = '0'
                    for ni, nj in dirs: dfs(ni, nj)
                """,
            )
        if slug == "rotting-oranges":
            return note(
                "BFS",
                "多源 BFS：所有烂橘子一起入队，按层扩散。",
                "每层代表一分钟，统计剩余新鲜橘子是否清零。",
                "这类“最短扩散时间”都想到多源 BFS。",
                """
                q = deque(all_rotten)
                minute = 0
                while q and fresh:
                    for _ in range(len(q)):
                        ...
                    minute += 1
                """,
            )
        if slug == "nearest-exit-from-entrance-in-maze":
            return note(
                "BFS",
                "无权最短步数直接 BFS，第一次走到边界出口就是答案。",
                "入口先标记访问，队列里存坐标和步数。",
                "迷宫最短路模板。",
                """
                q = deque([(sx, sy, 0)])
                maze[sx][sy] = '+'
                while q:
                    x, y, d = q.popleft()
                    ...
                """,
            )
        if slug == "keys-and-rooms":
            return note(
                "图",
                "房间和钥匙就是图的可达性问题。",
                "DFS/BFS 从 0 号房间出发，看能否访问所有节点。",
                "连通性题模板。",
                """
                seen = {0}
                q = deque([0])
                while q:
                    x = q.popleft()
                    for y in rooms[x]:
                        if y not in seen:
                            seen.add(y); q.append(y)
                return len(seen) == len(rooms)
                """,
            )
        if slug == "number-of-provinces":
            return note(
                "图",
                "省份数量就是无向图连通块个数。",
                "DFS/BFS/并查集都行；面试里 DFS 最好写。",
                "本质和岛屿数量一样。",
                """
                seen = set()
                def dfs(i):
                    for j, c in enumerate(isConnected[i]):
                        if c and j not in seen:
                            seen.add(j)
                            dfs(j)
                """,
            )
        if slug == "snakes-and-ladders":
            return note(
                "BFS",
                "棋盘游戏最少步数就是图最短路。",
                "每个格子向后 1..6 个位置连边，遇蛇梯先跳转，再 BFS。",
                "关键是编号和矩阵坐标互转。",
                """
                q = deque([(1, 0)])
                seen = {1}
                while q:
                    pos, step = q.popleft()
                    for nxt in range(pos + 1, min(pos + 6, n * n) + 1):
                        ...
                """,
            )
        if slug == "word-ladder":
            return note(
                "BFS",
                "无权最短变换步数直接 BFS，最好用通配符表加速邻居查找。",
                "每次改一个字符形成邻接关系，层数就是答案。",
                "更优可提双向 BFS。",
                """
                wild = defaultdict(list)
                for w in wordList:
                    for i in range(len(w)):
                        wild[w[:i] + '*' + w[i+1:]].append(w)
                """,
            )
        if slug == "minimum-genetic-mutation":
            return note(
                "BFS",
                "基因变化本质是单词接龙缩小版：每次改一位，最少几步。",
                "BFS 扩展所有合法下一状态，bank 用 set 加速。",
                "题小直接 BFS 就够。",
                """
                bank = set(bank)
                q = deque([(startGene, 0)])
                seen = {startGene}
                while q:
                    gene, d = q.popleft()
                    ...
                """,
            )
        if slug == "reorder-routes-to-make-all-paths-lead-to-the-city-zero":
            return note(
                "图",
                "无向遍历整棵树，但在边上记住原方向；遇到“背离 0”的边就要改向。",
                "建双向图，原正向边打 1，反向边打 0，DFS/BFS 累加需要翻转的边。",
                "这是树遍历 + 方向标记题。",
                """
                g = defaultdict(list)
                for a, b in connections:
                    g[a].append((b, 1))
                    g[b].append((a, 0))
                """,
            )
        if slug == "course-schedule":
            return note(
                "拓扑排序",
                "课程依赖就是有向图判环；能拓扑完就能学完。",
                "统计入度，入度 0 入队，弹出时削减后继入度。",
                "拓扑排序判 DAG 模板。",
                """
                g = defaultdict(list)
                indeg = [0] * numCourses
                for a, b in prerequisites:
                    g[b].append(a)
                    indeg[a] += 1
                """,
            )
        return note(
            "拓扑排序",
            "课程表 II 就是在拓扑排序时把弹出顺序记下来。",
            "若最终排序长度 < 课程数，说明有环。",
            "判环 + 输出顺序一锅端。",
            """
            ans = []
            q = deque(i for i, d in enumerate(indeg) if d == 0)
            while q:
                x = q.popleft()
                ans.append(x)
                ...
            return ans if len(ans) == numCourses else []
            """,
        )

    if slug in {"implement-trie-prefix-tree", "design-add-and-search-words-data-structure", "search-suggestions-system", "word-search-ii"}:
        if slug == "implement-trie-prefix-tree":
            return note(
                "字典树",
                "Trie 每个节点存孩子和单词结束标记。",
                "插入就按字符往下建，查询就一路走。",
                "字典树模板题。",
                """
                class TrieNode:
                    def __init__(self):
                        self.next = {}
                        self.end = False
                """,
            )
        if slug == "design-add-and-search-words-data-structure":
            return note(
                "字典树",
                "带 `.` 通配符时，查询阶段需要 DFS 尝试所有孩子。",
                "插入仍是普通 Trie；搜索遇到 `.` 就分叉递归。",
                "这是 Trie + DFS 组合题。",
                """
                def search(word):
                    def dfs(node, i):
                        if i == len(word): return node.end
                        ch = word[i]
                        ...
                    return dfs(root, 0)
                """,
            )
        if slug == "search-suggestions-system":
            return note(
                "排序 / 字典树",
                "面试先给排序 + 双指针 / 二分，字典树是加分项。",
                "产品名排序后，对每个前缀二分出左边界，往后拿前 3 个匹配项。",
                "比硬写 Trie 更短。",
                """
                products.sort()
                ans = []
                pre = ''
                l = 0
                for ch in searchWord:
                    pre += ch
                    l = bisect_left(products, pre, l)
                    ans.append([p for p in products[l:l+3] if p.startswith(pre)])
                return ans
                """,
            )
        return note(
            "Trie + 回溯",
            "单词搜索 II 用 Trie 压掉大量无效前缀，再在板子上 DFS。",
            "DFS 走到 Trie 没有该字符就立刻剪枝。",
            "比对每个单词单独搜高效太多。",
            """
            trie = build(words)
            def dfs(i, j, node):
                ch = board[i][j]
                if ch not in node.next: return
                nxt = node.next[ch]
                ...
            """,
        )

    if slug in {"minimum-size-subarray-sum", "find-all-anagrams-in-a-string", "max-consecutive-ones-iii", "maximum-number-of-vowels-in-a-substring-of-given-length", "longest-subarray-of-1s-after-deleting-one-element", "minimum-window-substring", "substring-with-concatenation-of-all-words", "subarray-sum-equals-k"}:
        if slug == "minimum-size-subarray-sum":
            return note(
                "滑窗",
                "全是正数时，窗口和有单调性：够大就尽量缩。",
                "右扩累加，和 >= target 时 while 缩左边更新最短长度，O(n)。",
                "正数数组最小长度题的标准解。",
                """
                l = s = 0
                ans = inf
                for r, x in enumerate(nums):
                    s += x
                    while s >= target:
                        ans = min(ans, r - l + 1)
                        s -= nums[l]; l += 1
                return 0 if ans == inf else ans
                """,
            )
        if slug == "find-all-anagrams-in-a-string":
            return note(
                "滑窗",
                "固定窗口大小 = `len(p)`，窗口字符计数和目标计数相等就记答案。",
                "定长窗口维护 26 维计数，O(n)。",
                "定长异位词窗口模板。",
                """
                need = Counter(p)
                win = Counter()
                ans = []
                for i, ch in enumerate(s):
                    win[ch] += 1
                    if i >= len(p):
                        old = s[i - len(p)]
                        win[old] -= 1
                        if win[old] == 0: del win[old]
                    if win == need:
                        ans.append(i - len(p) + 1)
                return ans
                """,
            )
        if slug == "max-consecutive-ones-iii":
            return note(
                "滑窗",
                "窗口内最多允许 k 个 0；超过了就缩左边。",
                "典型“至多 k 个坏点”的窗口题，O(n)。",
                "背住这个模板，很多题通用。",
                """
                l = zeros = ans = 0
                for r, x in enumerate(nums):
                    zeros += x == 0
                    while zeros > k:
                        zeros -= nums[l] == 0
                        l += 1
                    ans = max(ans, r - l + 1)
                return ans
                """,
            )
        if slug == "maximum-number-of-vowels-in-a-substring-of-given-length":
            return note(
                "滑窗",
                "定长窗口数元音，进一个减一个。",
                "元音集合 + 固定窗口，O(n)。",
                "定长子串统计题标准模板。",
                """
                vowels = set('aeiou')
                cur = sum(ch in vowels for ch in s[:k])
                ans = cur
                for i in range(k, len(s)):
                    cur += s[i] in vowels
                    cur -= s[i - k] in vowels
                    ans = max(ans, cur)
                return ans
                """,
            )
        if slug == "longest-subarray-of-1s-after-deleting-one-element":
            return note(
                "滑窗",
                "等价于窗口内最多保留 1 个 0，答案是窗口长度减 1。",
                "和 `Max Consecutive Ones III` 同模板。",
                "记得最后一定要删一个元素。",
                """
                l = zeros = ans = 0
                for r, x in enumerate(nums):
                    zeros += x == 0
                    while zeros > 1:
                        zeros -= nums[l] == 0
                        l += 1
                    ans = max(ans, r - l)
                return ans
                """,
            )
        if slug == "minimum-window-substring":
            return note(
                "滑窗",
                "最小覆盖子串：右边扩到全覆盖，左边缩到刚好不够。",
                "维护 `need` 计数和已满足字符数，复杂度 O(n)。",
                "这是滑窗高频母题，必须会。",
                """
                need = Counter(t)
                miss = len(t)
                l = start = end = 0
                for r, ch in enumerate(s, 1):
                    ...
                return s[start:end]
                """,
            )
        if slug == "substring-with-concatenation-of-all-words":
            return note(
                "滑窗",
                "单词等长，所以按偏移量分组滑窗，每次跨一个单词长度。",
                "对每个 offset 维护窗口内单词频次，超量就缩左边。",
                "比逐字符暴力高效很多。",
                """
                w = len(words[0])
                need = Counter(words)
                for offset in range(w):
                    l = r = offset
                    win = Counter()
                    ...
                """,
            )
        return note(
            "前缀和 + 哈希",
            "子数组和 = k 就想前缀和：若 `pre[j]-pre[i]=k`，则找 `pre[i]=pre[j]-k`。",
            "哈希表统计前缀和出现次数，边走边累加答案，O(n)。",
            "这是前缀和计数母题。",
            """
            cnt = Counter({0: 1})
            pre = ans = 0
            for x in nums:
                pre += x
                ans += cnt[pre - k]
                cnt[pre] += 1
            return ans
            """,
        )

    if slug in {"kth-largest-element-in-an-array", "top-k-frequent-elements", "find-k-pairs-with-smallest-sums", "ipo", "total-cost-to-hire-k-workers", "maximum-subsequence-score", "find-median-from-data-stream", "median-finder", "smallest-number-in-infinite-set", "online-stock-span"}:
        if slug == "kth-largest-element-in-an-array":
            return note(
                "堆",
                "保一个大小为 k 的小根堆，堆顶就是当前第 k 大。",
                "遍历数组时 push/pop，O(n log k)。",
                "追问可补充快选平均 O(n)。",
                """
                heap = []
                for x in nums:
                    heappush(heap, x)
                    if len(heap) > k:
                        heappop(heap)
                return heap[0]
                """,
            )
        if slug == "top-k-frequent-elements":
            return note(
                "哈希 + 堆",
                "先统计频次，再按频次拿 top k。",
                "`Counter` 后用 `nlargest` / 小根堆都行。",
                "桶排序是更优 O(n) 备选。",
                """
                cnt = Counter(nums)
                return [x for x, _ in heapq.nlargest(k, cnt.items(), key=lambda p: p[1])]
                """,
            )
        if slug == "find-k-pairs-with-smallest-sums":
            return note(
                "堆",
                "两个有序数组求最小 pair，用堆按和从小到大扩展。",
                "把 `(nums1[i]+nums2[0], i, 0)` 入堆，弹一个再补下一个 `j+1`。",
                "这是经典 k 路合并思路。",
                """
                heap = [(nums1[i] + nums2[0], i, 0) for i in range(min(k, len(nums1)))]
                heapq.heapify(heap)
                while heap and len(ans) < k:
                    _, i, j = heapq.heappop(heap)
                    ans.append([nums1[i], nums2[j]])
                    if j + 1 < len(nums2):
                        heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))
                """,
            )
        if slug == "ipo":
            return note(
                "贪心 + 堆",
                "先按所需资本排序，把当前能做的项目利润都扔进大根堆，每轮拿利润最大的。",
                "项目最多做 k 次，复杂度 O(n log n)。",
                "IPO 是“门槛 + 选最大收益”的堆模板。",
                """
                projects = sorted(zip(capital, profits))
                heap = []
                i = 0
                for _ in range(k):
                    while i < len(projects) and projects[i][0] <= w:
                        heappush(heap, -projects[i][1]); i += 1
                    if not heap: break
                    w -= heappop(heap)
                return w
                """,
            )
        if slug == "total-cost-to-hire-k-workers":
            return note(
                "堆",
                "左右两端各维护一个候选堆，每次取更便宜的一边，再从同侧补人。",
                "典型双堆模拟，O(k log candidates)。",
                "注意左右指针别交叉重复入堆。",
                """
                # left_heap / right_heap
                # 每次弹更小的，再从对应一侧补一个
                """,
            )
        if slug == "maximum-subsequence-score":
            return note(
                "排序 + 堆",
                "按 `nums2` 从大到小枚举“当前最小 nums2”，同时用小根堆保最大的 k 个 `nums1` 之和。",
                "答案 = 当前 `nums2` * 堆里 `nums1` 总和。",
                "这是“固定最小值 + top k 和”模型。",
                """
                pairs = sorted(zip(nums2, nums1), reverse=True)
                heap = []
                s = ans = 0
                for b, a in pairs:
                    heappush(heap, a); s += a
                    if len(heap) > k:
                        s -= heappop(heap)
                    if len(heap) == k:
                        ans = max(ans, s * b)
                return ans
                """,
            )
        if slug in {"find-median-from-data-stream", "median-finder"}:
            return note(
                "堆",
                "中位数流：左边大根堆存较小一半，右边小根堆存较大一半。",
                "始终保证两个堆大小差不超过 1。",
                "这是数据流中位数标准模板。",
                """
                heappush(low, -num)
                heappush(high, -heappop(low))
                if len(high) > len(low):
                    heappush(low, -heappop(high))
                """,
            )
        if slug == "smallest-number-in-infinite-set":
            return note(
                "设计 + 堆",
                "无限集本质是一个递增指针 + 一个“加回来的数”的最小堆。",
                "没被弹出过的最小值由指针给，`addBack` 过的值由堆给。",
                "注意用 set 防重复加回。",
                """
                if heap and heap[0] < cur:
                    return heappop(heap)
                cur += 1
                return cur - 1
                """,
            )
        return note(
            "单调栈",
            "股票跨度是往左找第一个比今天价格大的位置，所以维护价格递减栈。",
            "栈里存 `(price, span)`，弹掉不大于当前价格的项并累加跨度。",
            "在线 next greater / previous greater 常见模板。",
            """
            span = 1
            while st and st[-1][0] <= price:
                span += st.pop()[1]
            st.append((price, span))
            return span
            """,
        )

    if slug in {"design-hashset", "insert-delete-getrandom-o1"}:
        return note(
            "设计",
            "O(1) 随机集合 = 数组存值 + 哈希表存下标。",
            "删除时把待删元素和数组尾交换，再更新哈希表。",
            "这是常见数据结构设计题。",
            """
            i = pos[val]
            last = arr[-1]
            arr[i] = last
            pos[last] = i
            arr.pop()
            del pos[val]
            """,
        )

    if slug in {"decode-string", "asteroid-collision", "daily-temperatures", "largest-rectangle-in-histogram", "basic-calculator", "longest-valid-parentheses", "remove-all-adjacent-duplicates-in-string-ii", "removing-stars-from-a-string"}:
        if slug == "decode-string":
            return note(
                "栈",
                "遇 `[` 把当前数字和字符串现场压栈，遇 `]` 再弹出来展开。",
                "多层嵌套字符串解码标准栈题。",
                "递归也能写，但栈更直观。",
                """
                num = 0
                cur = ''
                st = []
                for ch in s:
                    ...
                return cur
                """,
            )
        if slug == "asteroid-collision":
            return note(
                "栈",
                "只有“栈顶向右、当前向左”才会相撞。",
                "栈保存稳定状态，新小行星和栈顶不断比较直到决出胜负。",
                "物理碰撞题常用栈模拟。",
                """
                st = []
                for x in asteroids:
                    alive = True
                    while alive and x < 0 and st and st[-1] > 0:
                        ...
                    if alive:
                        st.append(x)
                return st
                """,
            )
        if slug == "daily-temperatures":
            return note(
                "单调栈",
                "想知道下一个更大元素，就维护单调递减栈。",
                "当前温度更高时，栈里比它低的都能结算答案。",
                "单调栈母题。",
                """
                ans = [0] * len(temperatures)
                st = []
                for i, x in enumerate(temperatures):
                    while st and temperatures[st[-1]] < x:
                        j = st.pop()
                        ans[j] = i - j
                    st.append(i)
                return ans
                """,
            )
        if slug == "largest-rectangle-in-histogram":
            return note(
                "单调栈",
                "每根柱子只在“它是最矮柱子”时结算最大矩形。",
                "单调递增栈，弹出时用当前下标和新栈顶算宽度。",
                "柱状图最大矩形必须会。",
                """
                st = [-1]
                ans = 0
                for i, h in enumerate(heights + [0]):
                    while st[-1] != -1 and heights[st[-1]] > h:
                        H = heights[st.pop()]
                        W = i - st[-1] - 1
                        ans = max(ans, H * W)
                    st.append(i)
                return ans
                """,
            )
        if slug == "basic-calculator":
            return note(
                "栈",
                "只有加减和括号时，关键是维护当前符号和括号前的累计值。",
                "遇 `(` 就把当前答案和符号压栈，遇 `)` 再弹出来合并。",
                "这题不用真的转后缀。",
                """
                ans = num = 0
                sign = 1
                st = []
                for ch in s:
                    ...
                return ans + sign * num
                """,
            )
        if slug == "longest-valid-parentheses":
            return note(
                "栈 / DP",
                "栈里存“最后一个没被匹配的下标”，这样一旦匹配成功就能算长度。",
                "先压 `-1` 作为边界，遇右括号后若栈空就重置边界。",
                "这是最长有效括号标准栈解。",
                """
                st = [-1]
                ans = 0
                for i, ch in enumerate(s):
                    if ch == '(':
                        st.append(i)
                    else:
                        st.pop()
                        if not st:
                            st.append(i)
                        else:
                            ans = max(ans, i - st[-1])
                return ans
                """,
            )
        if slug == "removing-stars-from-a-string":
            return note(
                "栈",
                "星号就删掉前一个字符，天然用栈。",
                "普通字符入栈，遇 `*` 就 pop。",
                "纯模拟题。",
                """
                st = []
                for ch in s:
                    if ch == '*':
                        st.pop()
                    else:
                        st.append(ch)
                return ''.join(st)
                """,
            )

    if slug in {"h-index"}:
        return note(
            "排序",
            "先排序，再找最大的 `h` 满足“至少有 h 篇论文引用 >= h”。",
            "降序排序后找到最后一个 `citations[i] >= i+1` 的位置。",
            "计数桶也能做到 O(n)。",
            """
            citations.sort(reverse=True)
            h = 0
            for i, x in enumerate(citations, 1):
                if x >= i:
                    h = i
            return h
            """,
        )

    if slug in {"perfect-squares", "coin-change", "partition-equal-subset-sum", "domino-and-tromino-tiling", "maximal-square", "longest-increasing-subsequence", "increasing-triplet-subsequence", "ugly-number-ii", "translate-number-to-string", "construct-product-array"}:
        if slug == "perfect-squares":
            return note(
                "DP",
                "完全平方数就是完全背包：每个平方数都能无限用。",
                "`dp[i] = min(dp[i], dp[i-sq] + 1)`，O(n * sqrt(n))。",
                "BFS 也能做最短步数。",
                """
                dp = [0] + [10**9] * n
                for i in range(1, n + 1):
                    j = 1
                    while j * j <= i:
                        dp[i] = min(dp[i], dp[i - j * j] + 1)
                        j += 1
                return dp[n]
                """,
            )
        if slug == "coin-change":
            return note(
                "完全背包",
                "零钱兑换最少硬币数，完全背包一维 DP。",
                "外层金额，内层枚举硬币；或相反都可以，只要语义一致。",
                "注意初始化为正无穷。",
                """
                dp = [0] + [inf] * amount
                for x in range(1, amount + 1):
                    for c in coins:
                        if x >= c:
                            dp[x] = min(dp[x], dp[x - c] + 1)
                return -1 if dp[amount] == inf else dp[amount]
                """,
            )
        if slug == "partition-equal-subset-sum":
            return note(
                "0/1 背包",
                "分割等和子集等价于：能不能选一些数凑出 `sum/2`。",
                "0/1 背包布尔 DP，倒序遍历容量避免重复用数。",
                "这是子集和模板题。",
                """
                target = sum(nums) // 2
                dp = [False] * (target + 1)
                dp[0] = True
                for x in nums:
                    for j in range(target, x - 1, -1):
                        dp[j] |= dp[j - x]
                return dp[target]
                """,
            )
        if slug == "domino-and-tromino-tiling":
            return note(
                "DP",
                "铺砖题看状态机：完整铺满、缺一格等状态之间如何转移。",
                "记住标准递推即可，复杂度 O(n)。",
                "面试里重点说清状态含义。",
                """
                full = [0] * (n + 1)
                part = [0] * (n + 1)
                full[0] = full[1] = 1
                for i in range(2, n + 1):
                    full[i] = full[i - 1] + full[i - 2] + 2 * part[i - 1]
                    part[i] = part[i - 1] + full[i - 2]
                return full[n] % MOD
                """,
            )
        if slug == "maximal-square":
            return note(
                "二维 DP",
                "右下角为 1 的最大正方形边长 = 左、上、左上最小值 + 1。",
                "状态 `dp[i][j]` 表示以当前位置为右下角的最大边长。",
                "面积最后记得平方。",
                """
                dp = [[0] * (n + 1) for _ in range(m + 1)]
                ans = 0
                for i in range(1, m + 1):
                    for j in range(1, n + 1):
                        if matrix[i - 1][j - 1] == '1':
                            dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
                            ans = max(ans, dp[i][j])
                return ans * ans
                """,
            )
        if slug == "longest-increasing-subsequence":
            return note(
                "DP / 二分",
                "面试先给 DP 能过，再补充二分优化到 O(n log n)。",
                "DP：`dp[i]` 表示以 `i` 结尾的 LIS 长度。",
                "更优是维护 `tails`，用二分找当前数该放的位置。",
                """
                tails = []
                for x in nums:
                    i = bisect_left(tails, x)
                    if i == len(tails):
                        tails.append(x)
                    else:
                        tails[i] = x
                return len(tails)
                """,
            )
        if slug == "increasing-triplet-subsequence":
            return note(
                "贪心",
                "维护最小值 `first` 和次小值 `second`，若有数大于 `second` 就成功。",
                "一遍扫描 O(n) / O(1)。",
                "这是 LIS 的极简版。",
                """
                first = second = float('inf')
                for x in nums:
                    if x <= first:
                        first = x
                    elif x <= second:
                        second = x
                    else:
                        return True
                return False
                """,
            )
        if slug == "ugly-number-ii":
            return note(
                "DP",
                "丑数序列由已有丑数乘 2/3/5 推出来，三个指针归并。",
                "每次取三者最小值加入数组，并移动对应指针。",
                "这是经典多指针 DP。",
                """
                dp = [1] * n
                i2 = i3 = i5 = 0
                for i in range(1, n):
                    dp[i] = min(dp[i2]*2, dp[i3]*3, dp[i5]*5)
                    if dp[i] == dp[i2]*2: i2 += 1
                    if dp[i] == dp[i3]*3: i3 += 1
                    if dp[i] == dp[i5]*5: i5 += 1
                return dp[-1]
                """,
            )
        if slug == "translate-number-to-string":
            return note(
                "DP",
                "当前位置可由单独翻译或和前一位一起翻译转移过来。",
                "只要两位数在 10~25 内，就多一种转移。",
                "这题本质是台阶 DP。",
                """
                s = str(num)
                a = b = 1
                for i in range(1, len(s)):
                    c = a + b if '10' <= s[i-1:i+1] <= '25' else a
                    b, a = a, c
                return a
                """,
            )
        return note(
            "前后缀",
            "构建乘积数组别用除法：前缀积 * 后缀积。",
            "第一遍写左侧乘积，第二遍从右往左乘后缀积。",
            "这和 `除自身以外数组的乘积` 是同题型。",
            """
            ans = [1] * len(a)
            for i in range(1, len(a)):
                ans[i] = ans[i - 1] * a[i - 1]
            suf = 1
            for i in range(len(a) - 1, -1, -1):
                ans[i] *= suf
                suf *= a[i]
            return ans
            """,
        )

    if slug in {"find-the-duplicate-number", "reverse-pairs", "first-missing-positive", "trapping-rain-water", "max-points-on-a-line", "number-of-digit-one", "nth-digit"}:
        if slug == "find-the-duplicate-number":
            return note(
                "快慢指针",
                "把数组看成链表：`i -> nums[i]`，重复数就是环入口。",
                "Floyd 判环后找入口，O(n) / O(1)。",
                "比哈希更优，且满足不改数组条件。",
                """
                slow = fast = nums[0]
                while True:
                    slow = nums[slow]
                    fast = nums[nums[fast]]
                    if slow == fast: break
                slow = nums[0]
                while slow != fast:
                    slow = nums[slow]
                    fast = nums[fast]
                return slow
                """,
            )
        if slug == "reverse-pairs":
            return note(
                "归并排序",
                "逆序对本质是归并时，左边某个数大于右边当前数时，左边剩余全都构成逆序对。",
                "归并排序边排序边计数，O(n log n)。",
                "这是计数逆序对标准解。",
                """
                def sort(arr):
                    if len(arr) <= 1: return arr
                    mid = len(arr) // 2
                    left = sort(arr[:mid]); right = sort(arr[mid:])
                    # merge and count
                """,
            )
        if slug == "first-missing-positive":
            return note(
                "原地哈希",
                "让值 `x` 尽量放到下标 `x-1` 的位置上，最后第一个不匹配的位置就是答案。",
                "循环交换直到每个正数回到自己该在的位置，O(n) / O(1)。",
                "这题最关键是原地索引映射。",
                """
                n = len(nums)
                for i in range(n):
                    while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                        j = nums[i] - 1
                        nums[i], nums[j] = nums[j], nums[i]
                for i, x in enumerate(nums):
                    if x != i + 1:
                        return i + 1
                return n + 1
                """,
            )
        if slug == "trapping-rain-water":
            return note(
                "双指针",
                "哪边矮就先算哪边，因为蓄水高度由短板决定。",
                "维护左右最大高度，移动较矮一侧时结算当前格子的水量，O(n)。",
                "单调栈也能做，但双指针更短。",
                """
                l, r = 0, len(height) - 1
                lmax = rmax = ans = 0
                while l < r:
                    if height[l] < height[r]:
                        lmax = max(lmax, height[l])
                        ans += lmax - height[l]
                        l += 1
                    else:
                        ...
                return ans
                """,
            )
        if slug == "max-points-on-a-line":
            return note(
                "哈希",
                "枚举一个基点，统计它和其他点的斜率出现次数。",
                "斜率用约分后的 `(dy, dx)` 表示，避免浮点误差，O(n^2)。",
                "这题关键是斜率归一化。",
                """
                for i in range(n):
                    cnt = Counter()
                    for j in range(i + 1, n):
                        dy = yj - yi
                        dx = xj - xi
                        g = gcd(dy, dx)
                        cnt[(dy // g, dx // g)] += 1
                """,
            )
        if slug == "number-of-digit-one":
            return note(
                "数学",
                "按位统计 1 的贡献：看高位、当前位、低位三部分。",
                "每一位分别计算出现次数，复杂度 O(log n)。",
                "这是数位统计经典题。",
                """
                digit = 1
                ans = 0
                while digit <= n:
                    high = n // (digit * 10)
                    cur = (n // digit) % 10
                    low = n % digit
                    ...
                    digit *= 10
                return ans
                """,
            )
        return note(
            "数学",
            "第 k 位数字题按位数分段：1 位数有 9 个，2 位数有 90 个 ...",
            "先定位落在哪个数位区间，再定位到具体数字和具体哪一位。",
            "关键是分段扣减。",
            """
            digit, start, count = 1, 1, 9
            while n > count:
                n -= count
                digit += 1
                start *= 10
                count = 9 * start * digit
            num = start + (n - 1) // digit
            return int(str(num)[(n - 1) % digit])
            """,
        )

    if slug in {"partition-labels", "dota2-senate", "determine-if-two-strings-are-close", "max-number-of-k-sum-pairs", "string-compression"}:
        if slug == "partition-labels":
            return note(
                "贪心",
                "每个字符最后出现位置决定当前分段最远要扩到哪里。",
                "顺扫时维护本段最远右边界，走到边界就切一刀。",
                "分段覆盖题的常见贪心。",
                """
                last = {ch: i for i, ch in enumerate(s)}
                ans = []
                start = end = 0
                for i, ch in enumerate(s):
                    end = max(end, last[ch])
                    if i == end:
                        ans.append(end - start + 1)
                        start = i + 1
                return ans
                """,
            )
        if slug == "dota2-senate":
            return note(
                "队列",
                "两派各维护一个队列，谁下标更小谁先出手，并把自己加到下一轮。",
                "队列模拟回合制博弈，O(n)。",
                "比字符串反复删除高效。",
                """
                r = deque(i for i, ch in enumerate(senate) if ch == 'R')
                d = deque(i for i, ch in enumerate(senate) if ch == 'D')
                n = len(senate)
                while r and d:
                    a, b = r.popleft(), d.popleft()
                    if a < b: r.append(a + n)
                    else: d.append(b + n)
                return 'Radiant' if r else 'Dire'
                """,
            )
        if slug == "determine-if-two-strings-are-close":
            return note(
                "哈希",
                "close 的条件：字符集合相同，且频次数组排序后相同。",
                "因为你只能重排字符和交换字符频次。",
                "核心是“集合一致 + 频次 multiset 一致”。",
                """
                c1, c2 = Counter(word1), Counter(word2)
                return set(c1) == set(c2) and sorted(c1.values()) == sorted(c2.values())
                """,
            )
        if slug == "max-number-of-k-sum-pairs":
            return note(
                "哈希 / 双指针",
                "面试先给哈希计数配对：来一个数就看补数库存够不够。",
                "一次遍历 O(n)。",
                "若先排序，也能用双指针 O(n log n)。",
                """
                cnt = Counter()
                ans = 0
                for x in nums:
                    if cnt[k - x]:
                        cnt[k - x] -= 1
                        ans += 1
                    else:
                        cnt[x] += 1
                return ans
                """,
            )
        return note(
            "双指针",
            "压缩字符串就双指针分组：统计连续段长度后原地写回。",
            "慢指针负责写，快指针负责找段尾。",
            "原地字符串数组处理常见模板。",
            """
            write = left = 0
            while left < len(chars):
                right = left
                while right < len(chars) and chars[right] == chars[left]:
                    right += 1
                ...
                left = right
            return write
            """,
        )

    if slug in {"equal-row-and-column-pairs"}:
        return note(
            "哈希",
            "把每一行序列当 key 计数，再枚举每一列去查。",
            "行转 tuple 存 Counter，列也转 tuple 匹配，O(n^2)。",
            "矩阵行列匹配题标准解。",
            """
            rows = Counter(tuple(row) for row in grid)
            ans = 0
            for col in zip(*grid):
                ans += rows[tuple(col)]
            return ans
            """,
        )

    if slug in {"dices-probability"}:
        return note(
            "DP",
            "骰子概率题：`dp[i][s]` 表示扔 i 个骰子得到和 s 的方案数。",
            "每多一个骰子，就从上一轮所有点数和转移 1..6；最后总方案数除以 `6^n`。",
            "滚动数组能把空间压下来，写法也不难。",
            """
            dp = [1] * 6
            for k in range(2, n + 1):
                ndp = [0] * (5 * k + 1)
                for i, cnt in enumerate(dp):
                    for face in range(1, 7):
                        ndp[i + face - 1] += cnt
                dp = ndp
            total = 6 ** n
            return [x / total for x in dp]
            """,
        )

    if slug in {"string-to-integer-atoi", "valid-number", "regular-expression-matching"}:
        if slug == "string-to-integer-atoi":
            return note(
                "模拟",
                "按题意一条条规则扫：去空格、读符号、读数字、判断越界。",
                "模拟题关键是顺序别错，尤其是越界处理。",
                "Python 虽不溢出，也要按 32 位整数边界裁剪。",
                """
                i, n = 0, len(s)
                while i < n and s[i] == ' ': i += 1
                sign = -1 if i < n and s[i] == '-' else 1
                ...
                """,
            )
        if slug == "valid-number":
            return note(
                "状态机 / 模拟",
                "有效数字题规则碎，最稳是有限状态机或分情况布尔标记。",
                "面试先给标记法：是否见过数字、小数点、指数。",
                "若面试官追问严谨性，再说 DFA。",
                """
                seen_num = seen_dot = seen_e = False
                for i, ch in enumerate(s.strip()):
                    ...
                return seen_num
                """,
            )
        return note(
            "DP",
            "正则匹配只有 `.` 和 `*`，DP 最稳：`dp[i][j]` 表示前缀是否匹配。",
            "遇 `*` 时要考虑匹配 0 次和匹配多次两种情况。",
            "这是困难字符串 DP 高频题。",
            """
            dp = [[False] * (n + 1) for _ in range(m + 1)]
            dp[0][0] = True
            for j in range(2, n + 1):
                if p[j - 1] == '*':
                    dp[0][j] = dp[0][j - 2]
            """,
        )

    return fallback_note(problem)


def render_problem(problem: Problem) -> tuple[str, str]:
    desc = describe(problem)
    hint = canonical_hint(problem)
    extra = f"｜原型：{hint}" if hint else ""
    header = f"## {problem.index:03d}. {problem.pid} {problem.title}【{problem.difficulty}】"
    body = "\n".join(
        [
            header,
            f"- 套路：{desc['family']}｜分类：{compact_track(problem)}{extra}",
            f"- 一句话速记：{desc['memory']}",
            f"- 面试可过：{desc['baseline']}",
            f"- 更优/补充：{desc['optimized']}",
            "```python",
            desc["code"],
            "```",
            "",
        ]
    )
    return desc["family"], body


def render_day(day_idx: int, chunk: list[Problem]) -> str:
    families = Counter()
    lines: list[str] = []
    for problem in chunk:
        family, body = render_problem(problem)
        families[family] += 1
        lines.append(body)

    top_families = "、".join(name for name, _ in families.most_common(5))
    diff_cnt = Counter(p.difficulty for p in chunk)
    start = chunk[0].index
    end = chunk[-1].index
    header = [
        f"# 面试阶梯思路速记 Day {day_idx}（{start:03d}-{end:03d}）",
        "",
        f"> 范围：{start:03d}-{end:03d}，共 {len(chunk)} 题。",
        f"> 难度：简单 {diff_cnt.get('简单', 0)} / 中等 {diff_cnt.get('中等', 0)} / 困难 {diff_cnt.get('困难', 0)}。",
        f"> 今日主线：{top_families}。",
        "> 刷法：先背“一句话速记”，再默写代码骨架，最后补“更优/补充”。",
        "",
        "---",
        "",
    ]
    return "\n".join(header + lines)


def chunk_problems(problems: list[Problem]) -> list[list[Problem]]:
    chunks = []
    pos = 0
    for size in DAY_SIZES:
        chunks.append(problems[pos : pos + size])
        pos += size
    return chunks


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    problems = load_problems()
    chunks = chunk_problems(problems)
    fallback_only: list[str] = []

    for day_idx, chunk in enumerate(chunks, 1):
        content = render_day(day_idx, chunk)
        out = OUTPUT_DIR / f"Day{day_idx}_{chunk[0].index:03d}-{chunk[-1].index:03d}.md"
        out.write_text(content)

    # 生成一个简短控制台摘要，便于 spot check。
    for p in problems:
        if describe(p)["family"] == "综合":
            fallback_only.append(f"{p.index:03d} {p.pid} {p.title}")

    print(f"Generated {len(chunks)} files in {OUTPUT_DIR}")
    if fallback_only:
        print("\nGeneric fallback used on these problems:")
        for row in fallback_only:
            print(row)


if __name__ == "__main__":
    main()
