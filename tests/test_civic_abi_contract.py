from pathlib import Path


ROOT = Path(__file__).parents[1]
API = ROOT / ".agileplus/civic-warfare-program/contracts/public-api.md"
HEADER = ROOT / ".agileplus/civic-warfare-program/contracts/civic_warfare.h"


def test_abi_version_packing_has_golden_value():
    text = API.read_text()
    assert "(major << 16) | minor" in text
    assert "ABI 2.7 therefore encodes as `0x0002_0007`" in text


def test_header_and_stable_error_contract_are_aligned():
    header = HEADER.read_text()
    api = API.read_text()
    assert "csw_destroy(CswRuntime **runtime)" in header
    assert "`csw_destroy` returns `void`" in api
    assert "`DuplicateCommand`" not in api
    assert "`CommandRejected`" not in api
