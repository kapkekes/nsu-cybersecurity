from array import array
from itertools import product, repeat
from typing import Self

ROUND_CONSTANTS: list[int] = [
    0x0000000000000001, 0x0000000000008082,
    0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088,
    0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B,
    0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080,
    0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080,
    0x0000000080000001, 0x8000000080008008
]
ROTATION_OFFSETS: list[list[int]] = [
    [0, 36, 3, 41, 18],
    [1, 44, 10, 45, 2],
    [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39, 8, 14]
]


def uint64_t_rol(x: int, n: int) -> int:
    return ((x >> (64 - (n % 64))) + (x << (n % 64))) % (1 << 64)


class KeccakF1600:
    __slots__ = ["_rate_bytes", "_output_len_bytes", "_suffix", "_state", "_A", "_B", "_C", "_D"]

    _rate_bytes: int
    _output_len_bytes: int
    _suffix: int

    _state: bytearray
    _A: list[array]
    _B: list[array]
    _C: array
    _D: array

    def __init__(self, rate_bits: int, suffix: int, output_len_bits: int | None = None) -> None:
        self.set_rate_and_output(rate_bits, suffix, output_len_bits)

        self._state = bytearray(200)
        self._A = [array("Q", repeat(0, 5)) for _ in range(5)]
        self._B = [array("Q", repeat(0, 5)) for _ in range(5)]
        self._C = array("Q", repeat(0, 5))
        self._D = array("Q", repeat(0, 5))

    def set_rate_and_output(self, rate_bits: int, suffix: int, output_len_bytes: int | None) -> None:
        if not (8 <= rate_bits <= 1592):
            raise ValueError(f"rate_bits should be a positive integer from 8 to 1592, while it is {rate_bits}")

        if rate_bits % 8 != 0:
            raise ValueError(f"rate_bits should be a multiple of 8, while {rate_bits % 8 = }")

        self._rate_bytes = rate_bits // 8

        match suffix:
            case 0x06:
                self._output_len_bytes = (200 - self._rate_bytes) // 2
            case 0x1F:
                if output_len_bytes is None:
                    raise ValueError("output_len_bytes can't be None if suffix is 0x1F")
                elif output_len_bytes <= 0:
                    raise ValueError(f"output_len_bytes should be a positive integer, while it is {output_len_bytes}")
                else:
                    self._output_len_bytes = output_len_bytes
            case reserved_suffix:
                raise ValueError(f"{reserved_suffix} is reserved and can't be used as suffix")

        self._suffix = suffix

    @property
    def rate_bytes(self) -> int:
        return self._rate_bytes

    @property
    def capacity_bytes(self) -> int:
        return 200 - self._rate_bytes

    @property
    def output_len_bytes(self) -> int:
        return self._output_len_bytes

    def _theta(self) -> Self:
        for x in range(5):
            self._C[x] = self._A[x][0] ^ self._A[x][1] ^ self._A[x][2] ^ self._A[x][3] ^ self._A[x][4]

        for x in range(5):
            self._D[x] = self._C[(x - 1) % 5] ^ uint64_t_rol(self._C[(x + 1) % 5], 1)

        for x, y in product(range(5), range(5)):
            self._A[x][y] ^= self._D[x]

        return self

    def _rho_pi(self) -> Self:
        for x, y in product(range(5), range(5)):
            self._B[y][(2 * x + 3 * y) % 5] = uint64_t_rol(self._A[x][y], ROTATION_OFFSETS[x][y])

        return self

    def _chi(self) -> Self:
        for x, y in product(range(5), range(5)):
            self._A[x][y] = self._B[x][y] ^ (~self._B[(x + 1) % 5][y] & self._B[(x + 2) % 5][y])

        return self

    def _iota(self, rc: int) -> None:
        self._A[0][0] ^= rc

    def _round24(self, rc: int) -> None:
        self._theta()._rho_pi()._chi()._iota(rc)

    def _convert_to_c_arrays(self) -> Self:
        for x, y in product(range(5), range(5)):
            bytestring = self._state[(idx := 8 * (x + 5 * y)): idx + 8]
            self._A[x][y] = int.from_bytes(bytestring, "little", signed=False)

        return self

    def _permutate(self) -> Self:
        for round_idx in range(24):
            self._round24(ROUND_CONSTANTS[round_idx])

        return self

    def _convert_to_bytearray(self) -> None:
        for x, y in product(range(5), range(5)):
            bytestring = self._A[x][y].to_bytes(8, "little", signed=False)
            self._state[(idx := 8 * (x + 5 * y)): idx + 8] = bytestring

    def get_hash(self, message: bytes) -> bytes:
        zero_pad_len = -(len(message) + 2) % self._rate_bytes
        message += bytes((self._suffix, *repeat(0, zero_pad_len), 0x80))
        for idx in range(len(self._state)):
            self._state[idx] = 0

        for segment in (message[idx: idx + self._rate_bytes] for idx in range(0, len(message), self._rate_bytes)):
            for idx, byte in enumerate(segment):
                self._state[idx] ^= byte
            self._convert_to_c_arrays()._permutate()._convert_to_bytearray()

        result = bytearray(self._state[:self._rate_bytes])
        while self._output_len_bytes > len(result):
            self._permutate()._convert_to_bytearray()
            result.extend(self._state[:self._rate_bytes])

        return bytes(result[:self._output_len_bytes])

    @classmethod
    def shake128(cls, output_length_bytes: int) -> Self:
        return cls(1344, 0x1F, output_length_bytes)

    @classmethod
    def shake256(cls, output_length_bytes: int) -> Self:
        return cls(1088, 0x1F, output_length_bytes)

    @classmethod
    def sha3_224(cls) -> Self:
        return cls(1152, 0x06)

    @classmethod
    def sha3_256(cls) -> Self:
        return cls(1088, 0x06)

    @classmethod
    def sha3_384(cls) -> Self:
        return cls(832, 0x06)

    @classmethod
    def sha3_512(cls) -> Self:
        return cls(576, 0x06)
