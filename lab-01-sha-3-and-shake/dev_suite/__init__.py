import hashlib
from collections.abc import Callable
from importlib.resources import as_file, files
from itertools import chain
from typing import NamedTuple

from keccak import KeccakF1600

from . import resources

RESOURCES = files(resources)
HASHES = RESOURCES.joinpath("hashes")
MESSAGES = RESOURCES.joinpath("messages")

FIXED_LENGTH_HASHES = ["SHA3-224", "SHA3-256", "SHA3-384", "SHA3-512"]
VARIABLE_LENGTH_HASHES = ["SHAKE-128", "SHAKE-256"]

MACHINE_FIXED = [h.lower().replace("-", "_") for h in FIXED_LENGTH_HASHES]
MACHINE_VARIABLE = [h.lower().replace("-", "_") for h in VARIABLE_LENGTH_HASHES]


class FixedCase(NamedTuple):
    keccak_init: Callable[[], KeccakF1600]
    hex_digest: str
    encoded: bytes


class FixedTestcases(NamedTuple):
    cases: list[FixedCase]
    ids: list[str]


class VariableCase(NamedTuple):
    keccak_init: Callable[[int], KeccakF1600]
    output_len: int
    hex_digest: str
    encoded: bytes


class VariableTestcases(NamedTuple):
    cases: list[VariableCase]
    ids: list[str]


FIXED_TESTCASES: FixedTestcases | None = None
VARIABLE_TESTCASES: VariableTestcases | None = None


def assemble_cases() -> None:
    sum_files: dict[str, list[str]] = {
        f"{name}-SUMS": []
        for name in chain(FIXED_LENGTH_HASHES, VARIABLE_LENGTH_HASHES)
    }

    for entry in MESSAGES.iterdir():
        if not entry.is_file():
            continue

        encoded_msg = entry.read_text("UTF-8").encode("UTF-8")

        for human_name, func_name in zip(FIXED_LENGTH_HASHES, MACHINE_FIXED):
            func = getattr(hashlib, func_name)
            line = f"{func(encoded_msg).digest().hex()}  {entry.name}"
            sum_files[f"{human_name}-SUMS"].append(line)

        for human_name, func_name in zip(VARIABLE_LENGTH_HASHES, MACHINE_VARIABLE):
            func = getattr(hashlib, func_name)
            length = int(human_name.split("-")[-1]) // 4
            line = f"{func(encoded_msg).digest(length).hex()}  {entry.name}"
            sum_files[f"{human_name}-SUMS"].append(line)

    for hash_name, lines in sum_files.items():
        with as_file(HASHES.joinpath(hash_name)) as hash_file:
            hash_file.write_text("\n".join(lines), "UTF-8")


def collect_cases() -> None:
    encoded_messages: dict[str, bytes] = {}
    for message_file in MESSAGES.iterdir():
        encoded_messages[message_file.name] = message_file.read_text("UTF-8").encode("UTF-8")

    fixed_cases = []
    fixed_ids = []

    for human_name, func_name in zip(FIXED_LENGTH_HASHES, MACHINE_FIXED):
        lines = map(str.split, HASHES.joinpath(f"{human_name}-SUMS").read_text().split("\n"))
        # hash_func = getattr(KeccakF1600, func_name)
        hash_func = getattr(hashlib, func_name)
        for hex_digest, message_name in lines:
            fixed_cases.append(FixedCase(hash_func, hex_digest, encoded_messages[message_name]))
            fixed_ids.append(f"{human_name} : {message_name}")

    global FIXED_TESTCASES
    FIXED_TESTCASES = FixedTestcases(fixed_cases, fixed_ids)

    variable_cases = []
    variable_ids = []

    for human_name, func_name in zip(VARIABLE_LENGTH_HASHES, MACHINE_VARIABLE):
        lines = map(str.split, HASHES.joinpath(f"{human_name}-SUMS").read_text().split("\n"))
        # hash_func = getattr(KeccakF1600, func_name)
        hash_func = getattr(hashlib, func_name)
        output_len = int(human_name.split("-")[-1]) // 4
        for hex_digest, message_name in lines:
            variable_cases.append(VariableCase(hash_func, output_len, hex_digest, encoded_messages[message_name]))
            variable_ids.append(f"{human_name} : {message_name}")

    global VARIABLE_TESTCASES
    VARIABLE_TESTCASES = VariableTestcases(variable_cases, variable_ids)


def get_fixed() -> FixedTestcases:
    if FIXED_TESTCASES is None:
        collect_cases()

    return FIXED_TESTCASES


def get_variable() -> VariableTestcases:
    if VARIABLE_TESTCASES is None:
        collect_cases()

    return VARIABLE_TESTCASES
