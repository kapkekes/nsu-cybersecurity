from binascii import a2b_hex

import pytest

from kuznyechik import Kuznyechik


@pytest.fixture
def cipher() -> Kuznyechik:
    return Kuznyechik(a2b_hex("8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef"))


def test_encrypt(cipher: Kuznyechik) -> None:
    expected = a2b_hex("7f679d90bebc24305a468d42b9d4edcd")
    assert cipher.encrypt(a2b_hex("1122334455667700ffeeddccbbaa9988")) == expected


def test_decrypt(cipher: Kuznyechik) -> None:
    expected = a2b_hex("1122334455667700ffeeddccbbaa9988")
    assert cipher.decrypt(a2b_hex("7f679d90bebc24305a468d42b9d4edcd")) == expected

