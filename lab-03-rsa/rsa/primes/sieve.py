__all__ = ("EratosthenesSieve",)

from typing import Self

from rsa.primes.bitarray import BitArray


class EratosthenesSieve:
    def __init__(self, up_to: int) -> None:
        self._upper_bound = up_to
        self._primes = BitArray.ones(up_to)
        self._process()

    def _process(self) -> Self:
        self._primes[0] = 0
        self._primes[1] = 0

        for i in range(2, self._upper_bound):
            if self._primes[i]:
                for j in range(i << 1, self._upper_bound, i):
                    self._primes[j] = 0

        return self

    def is_prime(self, x: int) -> int:
        if not 0 <= x < self._upper_bound:
            message = f"{x = } isn't in [0, {self._upper_bound})"
            raise ValueError(message)

        return self._primes[x]
