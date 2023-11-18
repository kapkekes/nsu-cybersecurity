__all__ = ["Kuznyechik"]

from itertools import repeat
from operator import getitem, xor

from kuznyechik.constants import LINEAR_COEFFICIENTS, MLT_TABLE, PI, PI_INV
from kuznyechik.types_extensions import u8


class Kuznyechik:
    _buffer: bytearray
    _keys: list[bytes]

    def __init__(self, key: bytes) -> None:
        # if len(key) != 32:
        #     exc_msg = f"key length should be 32, while {len(key) = }"
        #     raise ValueError(exc_msg)

        self._keys = [bytes(key[:16]), bytes(key[16:])]
        k1, k2 = self._keys
        for i in range(4):
            for j in range(8):
                k1, k2 = self.F(KEY_CONSTANTS[8 * i + j], k1, k2)
            self._keys.append(k1)
            self._keys.append(k2)

    @staticmethod
    def linear(buffer: bytes | bytearray) -> u8:
        r = 0
        for b, lc in zip(buffer, LINEAR_COEFFICIENTS):
            r ^= MLT_TABLE.precomputed(b, lc)
        return r

    @staticmethod
    def X(k: bytes, m: bytes) -> bytes:
        return bytes(map(xor, k, m))

    @staticmethod
    def S(m: bytes) -> bytes:
        return bytes(map(getitem, repeat(PI), m))

    @staticmethod
    def S_inv(m: bytes) -> bytes:
        return bytes(map(getitem, repeat(PI_INV), m))

    @staticmethod
    def R(m: bytes) -> bytes:
        return bytes([Kuznyechik.linear(m)]) + m[:-1]

    @staticmethod
    def R_inv(ct: bytes) -> bytes:
        head, *tail = ct
        return bytes(tail) + bytes([Kuznyechik.linear(bytes(tail + [head]))])

    @staticmethod
    def L(m: bytes) -> bytes:
        for _ in range(16):
            m = Kuznyechik.R(m)
        return m

    @staticmethod
    def L_inv(ct: bytes) -> bytes:
        for _ in range(16):
            ct = Kuznyechik.R_inv(ct)
        return ct

    @staticmethod
    def F(k: bytes, a1: bytes, a0: bytes) -> tuple[bytes, bytes]:
        return bytes(map(xor, Kuznyechik.L(Kuznyechik.S(Kuznyechik.X(k, a1))), a0)), a1

    def encrypt(self, message: bytes) -> bytes:
        message_blocks: list[bytes] = [message[idx: idx + 16] for idx in range(0, len(message), 16)]
        message_blocks[-1] = message_blocks[-1].ljust(16, b"\0")

        cipher_text_blocks: list[bytes] = []
        for block in message_blocks:
            for idx in range(9):
                block = self.L(self.S(self.X(self._keys[idx], block)))
            cipher_text_blocks.append(self.X(self._keys[-1], block))

        return b"".join(cipher_text_blocks)

    def decrypt(self, cipher_text: bytes) -> bytes:
        cipher_text_blocks: list[bytes] = [cipher_text[idx: idx + 16] for idx in range(0, len(cipher_text), 16)]
        if len(cipher_text_blocks[-1]) < 16:
            cipher_text_blocks[-1] = cipher_text_blocks[-1].ljust(16, b"\0")

        message_blocks: list[bytes] = []
        for block in cipher_text_blocks:
            for idx in range(9, 0, -1):
                block = self.S_inv(self.L_inv(self.X(self._keys[idx], block)))
            message_blocks.append(self.X(self._keys[0], block))

        return b"".join(message_blocks).rstrip(b"\0")


KEY_CONSTANTS: list[bytes] = [Kuznyechik.L(bytes(15) + bytes([i])) for i in range(1, 33)]
