__all__ = ("BitArray",)

from array import array
from itertools import repeat
from typing import Self

BITS: list[int] = [1 << index for index in range(64)]


class BitArray(array[int]):
    @classmethod
    def zeroes(cls, bits: int) -> Self:
        c, r = divmod(bits, 64)
        return cls("Q", repeat(0, c + (1 if r else 0)))

    @classmethod
    def ones(cls, bits: int) -> Self:
        c, r = divmod(bits, 64)
        return cls("Q", repeat(0xFFFFFFFFFFFFFFFF, c + (1 if r else 0)))

    def __getitem__(self, index: int) -> int:  # type: ignore
        c, r = divmod(index, 64)
        return super().__getitem__(c) & BITS[r]

    def __setitem__(self, index: int, bit: int) -> None:  # type: ignore
        c, r = divmod(index, 64)
        super().__setitem__(c, (super().__getitem__(c) & ~(1 << r)) | (bit << r))
