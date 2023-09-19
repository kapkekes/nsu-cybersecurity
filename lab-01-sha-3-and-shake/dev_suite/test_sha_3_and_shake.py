import pytest
from pytest_benchmark.plugin import benchmark

from . import get_fixed, get_variable


@pytest.mark.parametrize("impl, hex_digest, encoded", get_fixed().cases, ids=get_fixed().ids)
def test_bench_fixed(benchmark, impl, hex_digest: str, encoded: bytes) -> None:
# def test_bench_fixed(benchmark, impl, hex_digest: str, encoded: bytes) -> None:
    assert benchmark(impl, encoded).digest().hex() == hex_digest
    # assert benchmark(impl().get_hash, encoded).hex() == hex_digest


@pytest.mark.parametrize("impl, output_len, hex_digest, encoded", get_variable().cases, ids=get_variable().ids)
def test_bench_variable(benchmark, impl, output_len: int, hex_digest: str, encoded: bytes) -> None:
# def test_bench_variable(benchmark, impl, output_len: int, hex_digest: str, encoded: bytes) -> None:
    assert benchmark(impl, encoded).digest(output_len).hex() == hex_digest
    # assert benchmark(impl(output_len).get_hash, encoded).hex() == hex_digest
