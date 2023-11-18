from binascii import a2b_hex

from kuznyechik import Kuznyechik

iteration_keys = list(map(a2b_hex, [
    "8899aabbccddeeff0011223344556677",
    "fedcba98765432100123456789abcdef",
    "db31485315694343228d6aef8cc78c44",
    "3d4553d8e9cfec6815ebadc40a9ffd04",
    "57646468c44a5e28d3e59246f429f1ac",
    "bd079435165c6432b532e82834da581b",
    "51e640757e8745de705727265a0098b1",
    "5a7925017b9fdd3ed72a91a22286f984",
    "bb44e25378c73123a5f32f73cdb6e517",
    "72e9dd7416bcf45b755dbaa88e4a4043"
]))


def test_specification_key() -> None:
    k = Kuznyechik(a2b_hex("8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef"))
    assert k._keys == iteration_keys  # type: ignore
