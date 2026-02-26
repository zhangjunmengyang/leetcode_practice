#
# @lc app=leetcode.cn id=1 lang=python3
#
# [1] 两数之和
#

# @lc code=start
# class Solution:
#     def twoSum(self, nums: List[int], target: int) -> List[int]:
#         for i in range(len(nums)):
#             minus = target - nums[i]
#             for j in range(i + 1, len(nums)):
#                 if minus == nums[j]:
#                     return [i, j]
#         return list()

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # 哈希表，存的时候判断有没有 match 的，没有 match 的再存，空间换时间
        memory = dict()
        for i in range(len(nums)):
            if nums[i] in memory:
                return [memory[nums[i]], i]
            else:
                memory[target - nums[i]] = i
        return [] 
# @lc code=end

