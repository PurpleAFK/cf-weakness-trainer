# Implementation and brute force
tags: implementation, brute force

## Implementation problems
Implementation problems test whether you can turn a statement into correct code without a clever algorithm. Read the statement twice, write down every rule and edge case, and simulate the examples by hand before coding. Choose simple data representations, split the code into small functions, and avoid copy-pasting blocks with small changes, which is where bugs hide. Most wrong answers here come from misreading the statement or from off-by-one indices.

## Brute force and complexity estimates
Before looking for something clever, estimate if brute force fits: about 1e8 simple operations run in one second. With n up to 20, try all subsets; up to 8 to 10, all permutations; up to 500, O(n^3); up to 5000, O(n^2); up to 2e5, O(n log n). Brute force is also the tool for finding patterns: print answers for small inputs and look for a formula. Keep a brute force solution to stress-test your real one.

## Avoiding careless mistakes
Use long long whenever values can exceed about 2e9. Reset global arrays and counters between test cases, and make sure the sum of n over test cases is what bounds the complexity. Print exactly the required format, including YES or NO casing if the judge is strict. Test edge cases deliberately: n = 1, all equal elements, maximum values, and an empty answer.
