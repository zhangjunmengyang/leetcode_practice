#
# @lc app=leetcode.cn id=9 lang=python3
#
# [9] 回文数
#

# @lc code=start
class Solution:
    def isPalindrome(self, x: int) -> bool:
        if x < 0: return False
        s = str(x)
        l = len(s)
        if l <= 1: return True
        i = 0
        while i < (l//2 + 1):
            if s[i] != s[l-1-i]:
                return False
            i += 1
        return True
        
# @lc code=end

