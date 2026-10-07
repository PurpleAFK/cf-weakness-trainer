# Game theory
tags: games

## Winning and losing positions
In two-player games with perfect information where the player who cannot move loses, every position is either winning (some move leads to a losing position) or losing (every move leads to a winning position). Compute this for small positions by brute force, then look for a pattern such as "losing when n is divisible by k+1" in subtraction games. Many Codeforces game problems are solved by symmetry or mirroring strategies, or by noticing that the first move decides everything.

## Nim and Sprague-Grundy
In Nim, the first player wins exactly when the XOR of all pile sizes is non-zero. The Sprague-Grundy theorem generalizes this: every impartial game position has a Grundy number (the mex of the Grundy numbers of the positions reachable in one move), and a sum of independent games is won by the first player when the XOR of their Grundy numbers is non-zero. Compute Grundy numbers for small sizes and look for periodicity.
