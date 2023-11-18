from binascii import a2b_hex
from collections.abc import Generator
from importlib.resources import as_file, files

import pytest

from kuznyechik import Kuznyechik
from tests import resources


@pytest.fixture
def cipher() -> Kuznyechik:
    return Kuznyechik(a2b_hex("8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef"))


@pytest.fixture
def message() -> Generator[bytes, None, None]:
    with as_file(files(resources) / "message.txt") as file:
        yield file.read_bytes()

def test_write_read(cipher: Kuznyechik, message: bytes) -> None:
    with as_file(files(resources) / "cipher_text.txt") as file:
        file.write_bytes(cipher_text := cipher.encrypt(message))

    with as_file(files(resources) / "cipher_text.txt") as file:
        read_cipher_text: bytes = file.read_bytes()

    assert cipher_text == read_cipher_text

    read_message: bytes = cipher.decrypt(read_cipher_text)
    with as_file(files(resources) / "restored_message.txt") as file:
        file.write_bytes(read_message)

    assert message == read_message
