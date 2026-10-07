# Constructive algorithms
tags: constructive algorithms

## How to approach constructive problems
A constructive problem asks you to build any object (an array, a permutation, a string, a graph) that satisfies conditions, or to say that none exists. Start by solving tiny cases by hand, n = 1, 2, 3, 4, and look for a pattern you can generalize. Find the impossible cases first: often a parity argument, a sum constraint, or a counting bound shows when no answer exists. Then aim for a simple construction such as alternating values, sorting, or placing the largest element in a fixed position.

## Common construction ideas
Useful patterns: alternating high and low values to avoid equal neighbors, writing the answer in two halves, using 1 and n as special positions, sorting and then cyclically shifting, and building the answer greedily from left to right while keeping enough freedom for the rest. For permutations, consider what happens when you reverse or swap pairs. When a problem asks for at most n operations, there is usually one operation per element.

## Checking a construction
Constructive solutions fail by missing a corner case where the pattern breaks, typically n = 1, n = 2 or an odd n. Write a checker that verifies your output satisfies all conditions, and run it on all small n. Many accepted solutions are short, so if your construction needs many special cases, look for a simpler pattern.
