from hashlib import sha3_256
from math import gcd
from random import randrange
from typing import NamedTuple

from rsa.primes import kinda_randprime


class PublicKey(NamedTuple):
    e: int
    n: int
    len: int


class PrivateKey(NamedTuple):
    d: int
    n: int
    len: int


class RSAKeyGenerator:
    __slots__ = ("_bit_length",)

    def __init__(self, bit_length: int) -> None:
        self._bit_length = bit_length

    def generate(self) -> tuple[PublicKey, PrivateKey]:
        p, q = kinda_randprime(self._bit_length), kinda_randprime(self._bit_length)
        n = p * q
        fi_n = (p - 1) * (q - 1)

        e = randrange(3, fi_n)
        while gcd(e, fi_n) != 1:
            e = randrange(3, fi_n)

        d = pow(e, -1, fi_n)
        return PublicKey(e, n, self._bit_length >> 3), PrivateKey(d, n, self._bit_length >> 3)

    @classmethod
    def len_1024(cls) -> tuple[PublicKey, PrivateKey]:
        return cls(1024).generate()

    @classmethod
    def len_2048(cls) -> tuple[PublicKey, PrivateKey]:
        return cls(2048).generate()


class RSA:
    __slots__ = ("_public", "_private")

    def __init__(self, public: PublicKey | None = None, private: PrivateKey | None = None) -> None:
        self._public = public
        self._private = private

    def encrypt(self, message: bytes) -> bytes:
        if self._public is None:
            raise AttributeError("message cannot be encrypted without the public key")

        upper = self._public.len * 2
        return b"".join(
            pow(
                int.from_bytes(message[idx: idx + self._public.len], "little"), self._public.e, self._public.n
            ).to_bytes(upper, "little")
            for idx in range(0, len(message), self._public.len)
        )

    def decrypt(self, cipher_text: bytes) -> bytes:
        if self._private is None:
            raise AttributeError("cipher_text cannot be decrypted without the private key")

        upper = self._private.len * 2
        return b"".join(
            pow(
                int.from_bytes(cipher_text[idx: idx + upper], "little"), self._private.d, self._private.n
            ).to_bytes(self._private.len, "little")
            for idx in range(0, len(cipher_text), upper)
        ).rstrip(b"\0")

    def sign(self, message: bytes) -> bytes:
        return self.encrypt(sha3_256(message).hexdigest().encode())

    def validate(self, message: bytes, signature: bytes) -> bool:
        h = sha3_256(message).hexdigest().encode("UTF-8")
        return h == self.decrypt(signature).ljust(32, b"\0")
