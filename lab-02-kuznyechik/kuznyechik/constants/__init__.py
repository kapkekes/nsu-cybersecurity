__all__ = ["MLT_TABLE", "PI", "PI_INV", "LINEAR_COEFFICIENTS"]

from importlib.resources import as_file, files
from typing import Self

from kuznyechik.constants import resources
from kuznyechik.types_extensions import u8


class MultiplicationTable:
    _table: list[list[u8]]

    def __init__(self, _table: list[list[u8]]) -> None:
        self._table = _table

    @staticmethod
    def manual(a: u8, b: u8) -> u8:
        r = 0
        while a:
            if a & 1:
                r ^= b

            b <<= 1
            if b & 0b1_0000_0000:
                b ^= 0b1_1100_0011  # x^8 + x^7 + x^6 + x + 1

            a >>= 1

        return r

    def precomputed(self, a: u8, b: u8) -> u8:
        return self._table[a][b]

    def packed(self, x: tuple[u8, u8]) -> u8:
        return self.precomputed(*x)

    @classmethod
    def load(cls) -> Self:
        anchor = files(resources)
        with as_file(anchor / "mlt_tables.csv") as tables_file:
            if not tables_file.exists():
                table = [[cls.manual(a, b) for b in range(0, 256)] for a in range(0, 256)]
                tables_file.write_text("\n".join(",".join(map(str, row)) for row in table))
            else:
                table = [[int(elem) for elem in row.split(",")]for row in tables_file.read_text().split("\n")]

            return cls(table)


MLT_TABLE = MultiplicationTable.load()

with as_file(files(resources) / "pi.csv") as pi_file:
    PI: list[u8] = [int(elem) for row in pi_file.read_text().split("\n") for elem in row.split(",")]

assert len(PI) == 256, f"PI constant is corrupted, {len(PI) = }, while it should be 256"
for idx, p in enumerate(PI):
    assert 0 <= p <= 255, f"{PI[idx] = } is out of [0, 255] segment"

PI_INV: list[u8] = [PI.index(idx) for idx in range(len(PI))]

LINEAR_COEFFICIENTS: list[u8] = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]
