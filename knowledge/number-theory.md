# Number theory
tags: number theory, math

## Divisibility, gcd and primes
The greatest common divisor is computed with Euclid's algorithm, gcd(a, b) = gcd(b, a mod b), in O(log min(a, b)); in C++ use std::gcd. lcm(a, b) = a / gcd(a, b) * b, dividing first to avoid overflow. A number n has at most about 2 * sqrt(n) divisors, all found by trying d up to sqrt(n). Trial division up to sqrt(n) tests primality and factorizes a single number. Facts used constantly: gcd of a whole array, the fact that a number is divisible by 3 if its digit sum is, and that any n > 1 has a prime factor at most sqrt(n) or is prime itself.

## Sieve of Eratosthenes
To find all primes up to N (around 1e7), mark multiples of each prime starting from p * p; the sieve runs in O(N log log N). Store the smallest prime factor of every number instead of a boolean and you can factorize any number up to N in O(log n) by repeatedly dividing by spf[n]. This is the standard tool when a problem asks about the prime factors of many numbers, for example counting how many array elements share a factor.

## Modular arithmetic
Counting answers are often asked modulo 1e9+7, which is prime. Addition, subtraction and multiplication work modulo m if you reduce after every operation; for subtraction add m before taking the modulo to avoid negatives. Division needs the modular inverse: for prime m, the inverse of a is a^(m-2) mod m by Fermat's little theorem, computed with fast exponentiation in O(log m). Use long long for the product of two values below 1e9+7, because it reaches about 1e18.

## Common mistakes in number theory
Overflow is the main enemy: a * b with both near 1e9 overflows int, and even long long when both are near 1e18. Loops like for (d = 1; d * d <= n; d++) need d as long long when n is large. Forgetting that 1 is not prime, or that gcd(0, x) = x, causes edge-case failures. When a brute force over divisors is too slow, think about iterating over multiples instead, which totals N log N by the harmonic series.
