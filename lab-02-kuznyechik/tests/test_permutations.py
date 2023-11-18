from binascii import a2b_hex

import pytest

from kuznyechik import Kuznyechik

samples_S_transform: list[tuple[bytes, bytes]] = [
    (a2b_hex("ffeeddccbbaa99881122334455667700"), a2b_hex("b66cd8887d38e8d77765aeea0c9a7efc")),
    (a2b_hex("b66cd8887d38e8d77765aeea0c9a7efc"), a2b_hex("559d8dd7bd06cbfe7e7b262523280d39")),
    (a2b_hex("559d8dd7bd06cbfe7e7b262523280d39"), a2b_hex("0c3322fed531e4630d80ef5c5a81c50b")),
    (a2b_hex("0c3322fed531e4630d80ef5c5a81c50b"), a2b_hex("23ae65633f842d29c5df529c13f5acda")),
]

samples_R_transform: list[tuple[bytes, bytes]] = [
    (a2b_hex("00000000000000000000000000000100"), a2b_hex("94000000000000000000000000000001")),
    (a2b_hex("94000000000000000000000000000001"), a2b_hex("a5940000000000000000000000000000")),
    (a2b_hex("a5940000000000000000000000000000"), a2b_hex("64a59400000000000000000000000000")),
    (a2b_hex("64a59400000000000000000000000000"), a2b_hex("0d64a594000000000000000000000000")),
]

samples_L_transform: list[tuple[bytes, bytes]] = [
    (a2b_hex("64a59400000000000000000000000000"), a2b_hex("d456584dd0e3e84cc3166e4b7fa2890d")),
    (a2b_hex("d456584dd0e3e84cc3166e4b7fa2890d"), a2b_hex("79d26221b87b584cd42fbc4ffea5de9a")),
    (a2b_hex("79d26221b87b584cd42fbc4ffea5de9a"), a2b_hex("0e93691a0cfc60408b7b68f66b513c13")),
    (a2b_hex("0e93691a0cfc60408b7b68f66b513c13"), a2b_hex("e6a8094fee0aa204fd97bcb0b44b8580")),
]

@pytest.mark.parametrize("message, expected", samples_S_transform)
def test_S(message: bytes, expected: bytes) -> None:
    assert Kuznyechik.S(message) == expected


@pytest.mark.parametrize("message, expected", samples_R_transform)
def test_R(message: bytes, expected: bytes) -> None:
    assert Kuznyechik.R(message) == expected


@pytest.mark.parametrize("message, expected", samples_L_transform)
def test_L(message: bytes, expected: bytes) -> None:
    assert Kuznyechik.L(message) == expected
