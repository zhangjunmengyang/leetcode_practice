#
# @lc app=leetcode.cn id=13 lang=python3
#
# [13] 罗马数字转整数
#

# @lc code=start
class Solution:
    def romanToInt(self, s: str) -> int:
        num_map = {
            "I": 1,
            "V": 5,
            "X": 10,
            "L": 50, 
            "C": 100,
            "D": 500,
            "M": 1000,
            "IV": 4,
            "IX": 9,
            "XL": 40,
            "XC": 90,
            "CD": 400,
            "CM": 900,
        }
        l = len(s)
        res = 0
        i = 0
        while i < l:
            # 先检查双字符组合（需要确保 i+1 不越界）
            if i + 1 < l and s[i] + s[i + 1] in num_map:
                res += num_map[s[i] + s[i + 1]]
                i += 2  # 跳过两个字符
            else:
                res += num_map[s[i]]
                i += 1  # 只跳过一个字符
        return res

        
# @lc code=end

