# Greedy algorithms
tags: greedy

## What makes a greedy correct
A greedy algorithm makes the locally best choice at each step and never undoes it. It is correct only if you can argue that some optimal solution makes the same choice. The standard proof is an exchange argument: take an optimal solution that differs from the greedy one, swap the differing choice for the greedy choice, and show the result is no worse. If you cannot sketch such an argument in two lines, test the greedy on small cases before submitting.

## Classic greedy patterns
Activity selection: to fit the most non-overlapping intervals, sort by end time and always take the interval that ends first. Scheduling to minimize lateness: sort by deadline. Coins: always taking the largest coin works for standard coin systems but not for arbitrary ones. Pairing problems: sort both arrays and match smallest with smallest, or smallest with largest, depending on the goal. Many greedy solutions start with sorting by the right key, and choosing that key is the whole difficulty.

## Avoiding wrong greedy submissions
Most wrong answers on greedy problems come from an idea that is plausible but false. Before submitting, try to break it: write a brute force for n up to 8 and compare outputs on random tests (stress testing), or try hand-made cases such as all equal values, a single element, and values in decreasing order. If a counterexample appears, the problem may need DP instead. Reading the constraints helps: n up to 2e5 rules out most DP over values and suggests sorting plus greedy.

## How to practice greedy
Solve greedy problems in your rating range and, for each one, write the exchange argument in a sentence after getting AC. Keep a list of greedy ideas that failed and why; the same false greedy patterns keep returning. Learn to write a quick brute force and a random test generator, because stress testing is the fastest way to catch a wrong greedy before the judge does.
