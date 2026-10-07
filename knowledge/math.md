# Math and observations
tags: math

## Finding the key observation
Many math problems at ratings 800 to 1300 hinge on one observation, such as parity (the sum's parity never changes under an operation), an invariant preserved by every move, or the fact that the answer only depends on the minimum, the maximum, or the count of some value. Try small cases, compute the answer by brute force, and look for the pattern before proving it. Write the observation as a sentence; if you cannot, you are probably guessing.

## Useful formulas and facts
The sum 1 + 2 + ... + n is n(n+1)/2. An arithmetic progression's sum is (first + last) * count / 2. Floor division rounds toward zero in C++ for negative numbers, so handle negatives carefully; ceil(a / b) for positive values is (a + b - 1) / b. Avoid floating point when an integer formula exists, and compare squared distances instead of distances to stay exact.
