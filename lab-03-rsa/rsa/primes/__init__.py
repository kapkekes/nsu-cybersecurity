__all__ = ("kinda_randprime",)

from math import ceil, log2
from random import randrange

from rsa.primes.sieve import EratosthenesSieve

SIEVE = EratosthenesSieve(10000)
PRIMES_UP_TO_256 = [n for n in range(10000) if SIEVE.is_prime(n)]


def with_sieve(n: int) -> bool:
    return all(n % p for p in PRIMES_UP_TO_256)


def MillerRabin(n: int, r: int | None = None) -> bool:  # noqa: N802
    if n % 2 == 0 or n <= 1:
        return False

    d = n - 1
    s = 0
    while not d & 1:
        d >>= 1
        s += 1

    if r is None:
        r = ceil(log2(n))

    for _ in range(r):
        x = pow(randrange(2, n - 1), d, n)
        if x == 1 or x == n - 1:
            continue
        flag = False
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == 1:
                return False
            if x == n - 1:
                flag = True
                break
        if flag:
            continue
        return False
    return True


def kinda_randprime(bit_length: int) -> int:
    if bit_length < 1:
        raise ValueError(f"bit_length should be greater or equal to 2, while {bit_length = }")

    bound = 1 << (bit_length - 1)
    candidate = bound | randrange(bound)
    while not (all(candidate % p for p in PRIMES_UP_TO_256) and MillerRabin(candidate)):
        candidate = bound | randrange(bound)

    return candidate
