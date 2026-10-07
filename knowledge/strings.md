# Strings
tags: strings, hashing

## String basics for contests
Most string problems at ratings 800 to 1400 need counting and careful implementation: frequency arrays of 26 letters, checking palindromes with two pointers, comparing a string with its reverse, and counting occurrences of a short pattern by sliding over every position. Build strings with += in a loop rather than repeated s = s + c, which copies the whole string each time and becomes O(n^2). Remember that substr(pos, len) takes a length, not an end index.

## Pattern matching with prefix function and Z-function
To find all occurrences of a pattern p in a text t in O(n + m), compute the prefix function (KMP) of p + '#' + t: positions where the value equals |p| mark matches. The Z-function gives, for each position, the length of the longest substring starting there that matches a prefix of the string; it also finds periods and borders. These two are interchangeable for most problems; learn one well.

## String hashing
Polynomial hashing maps a string to a number, h = s[0] * B^(n-1) + ... + s[n-1] mod M, and prefix hashes let you compare any two substrings in O(1). Use a random base and a large modulus (or two moduli) to avoid collisions and anti-hash tests. Hashing plus binary search finds the longest common substring or the longest repeated substring in O(n log n).
