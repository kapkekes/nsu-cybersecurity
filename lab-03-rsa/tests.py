import pytest

from rsa import RSA, PrivateKey, PublicKey, RSAKeyGenerator

keys_1024 = RSAKeyGenerator.len_1024()
keys_2048 = RSAKeyGenerator.len_2048()


@pytest.mark.parametrize("keys", [keys_1024, keys_2048])
def test_encryption(keys: tuple[PublicKey, PrivateKey]):
    system = RSA(*keys)
    message = b"Hello, World!" * 1024

    assert message == system.decrypt(system.encrypt(message))


@pytest.mark.parametrize("keys", [keys_1024, keys_2048])
def test_signing(keys: tuple[PublicKey, PrivateKey]):
    system = RSA(*keys)
    message = b"Hello, World!" * 1024
    signature = system.sign(message)

    assert not system.validate(message[:-1], signature)
    assert system.validate(message, signature)
