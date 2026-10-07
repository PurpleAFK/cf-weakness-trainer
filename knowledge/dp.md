# Dynamic programming
tags: dp

## How to design a DP
Dynamic programming solves a problem by combining answers to smaller subproblems that overlap. Design it in four steps: define the state in words (dp[i] = the best answer using the first i elements), write the transition (how dp[i] is built from smaller states), set the base cases, and fix the order of computation so every state is computed before it is used. The answer is usually dp[n] or the best over all states. If you cannot describe the state in one sentence, the DP is not ready to code.

## Classic DP patterns
Learn the patterns that keep repeating: one-dimensional DP over a prefix (climbing stairs, frog jump, maximum sum with no two adjacent), knapsack (dp[w] = best value with capacity w; iterate capacity backwards for 0/1 knapsack), longest increasing subsequence (O(n^2) DP, or O(n log n) with binary search), longest common subsequence and edit distance on two strings (dp[i][j]), and grid paths (dp[r][c] from the top and the left). Most Div. 2 C DP problems are one of these with a twist in the state.

## Adding information to the state
When the transition needs to know something about the past, add it to the state. Examples: dp[i][last] when the next choice depends on the previous element, dp[i][k] when you may use at most k operations, and dp[i][0 or 1] for "is the previous item taken". The state size times the transition cost is the complexity, so check it against the limits: n = 2e5 allows O(n) or O(n log n) states, while n = 5000 allows O(n^2).

## Common mistakes in DP
Wrong base cases and wrong iteration order cause most wrong answers. Initialize impossible states with -infinity or +infinity, not 0, when you take a max or min. Use long long when values add up, and take the modulo after every addition when the problem asks for counts modulo 1e9+7. Recursion with memoization is easier to write but can overflow the stack for n around 1e5 or more; switch to an iterative loop. Test on the smallest cases by hand first.

## How to practice DP
Start with the CSES dynamic programming section or AtCoder Educational DP Contest (problems A to E), which teach the standard patterns one by one. For every problem, write the state definition as a comment before coding. Re-solve problems you failed after a few days without looking, because DP is learned by recognizing patterns, and recognition comes from repetition.
