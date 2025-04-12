import json
import pytest
from main import list_functions, get_pseudocode, list_structures, get_structure

# Patch main.ctx directly for mocking
@pytest.fixture(autouse=True)
def inject_mock_context(monkeypatch):
    monkeypatch.setattr("main.ctx_ready", True)
    monkeypatch.setattr("main.is_context_ready", lambda: True)
    monkeypatch.setattr("main.load_context", lambda: None)
    monkeypatch.setattr("main.ctx", json.loads(json.dumps({
        "program": "mock.bin",
        "functions": [
            {
                "name": "main",
                "entry": "0x1000",
                "signature": "int main()",
                "pseudocode": "int main() { return 0; }"
            }
        ],
        "data_types": {
            "structures": [
                {
                    "name": "User",
                    "length": 12,
                    "members": [
                        {"name": "id", "datatype": "int", "offset": 0},
                        {"name": "age", "datatype": "int", "offset": 4}
                    ]
                }
            ],
            "enums": [],
            "function_definitions": []
        }
    })))

@pytest.mark.asyncio
async def test_list_functions():
    assert await list_functions() == ["main"]

@pytest.mark.asyncio
async def test_get_pseudocode():
    pseudocode = await get_pseudocode("main")
    assert "int main()" in pseudocode

@pytest.mark.asyncio
async def test_list_structures():
    assert await list_structures() == ["User"]

@pytest.mark.asyncio
async def test_get_structure():
    result = await get_structure("User")
    assert result["name"] == "User"
    assert any(m["name"] == "id" for m in result["members"])
