import os
import json
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ghidra")

# === Configuration ===
EXPORT_SCRIPT_NAME = "export_context.py"
EXPORT_SCRIPT_PATH = os.path.abspath(EXPORT_SCRIPT_NAME)
GHIDRA_CONTEXT_JSON = os.path.join(os.getcwd(), "ghidra_context.json")

# === Internal state ===
ctx_ready = False
last_binary = None
ctx = {}

def run_headless(ghidra_path: str, binary_path: str):
    analyze_headless = os.path.join(ghidra_path, "support", "analyzeHeadless")
    project_dir = os.getcwd()
    project_name = "ghidra_ctx"
    cmd = [
        analyze_headless,
        project_dir,
        project_name,
        "-import", binary_path,
        "-overwrite",
        "-scriptPath", os.path.dirname(EXPORT_SCRIPT_PATH),
        "-postScript", os.path.basename(EXPORT_SCRIPT_PATH),
        "-deleteProject"
    ]
    env = os.environ.copy()
    env["GHIDRA_CONTEXT_JSON"] = GHIDRA_CONTEXT_JSON
    return subprocess.run(cmd, capture_output=True, text=True, env=env)

def load_context():
    global ctx
    with open(GHIDRA_CONTEXT_JSON) as f:
        ctx = json.load(f)

def is_context_ready():
    return os.path.exists(GHIDRA_CONTEXT_JSON)

@mcp.tool()
async def setup_context(ghidra_path: str = "/Users/tomi/Downloads/ghidra_11.3.1_PUBLIC", binary_path: str = "/Users/tomi/Documents/ghidra_mcp/crackme") -> str:
    """Run Ghidra headless decompilation to export binary context."""
    global ctx_ready, last_binary

    if not os.path.isdir(ghidra_path):
        return f"❌ Ghidra path '{ghidra_path}' is not valid."
    if not os.path.isfile(binary_path):
        return f"❌ Binary file '{binary_path}' does not exist."

    result = run_headless(ghidra_path, binary_path)

    if result.returncode != 0:
        return f"❌ Ghidra failed:\n{result.stderr}"

    if not is_context_ready():
        return f"❌ Export script ran but no context was saved."

    load_context()
    ctx_ready = True
    last_binary = os.path.basename(binary_path)
    return f"✅ Context loaded for '{last_binary}'."

@mcp.tool()
async def list_functions() -> list[str]:
    """List all function names from the loaded binary."""
    if not ctx_ready:
        return ["❌ Context not ready. Run `setup_context()` first."]
    return [f["name"] for f in ctx.get("functions", [])]

@mcp.tool()
async def get_pseudocode(name: str) -> str:
    """Get pseudocode for a specific function by name."""
    if not ctx_ready:
        return "❌ Context not ready. Run `setup_context()` first."
    for f in ctx.get("functions", []):
        if f["name"] == name:
            return f["pseudocode"]
    return f"❌ Function '{name}' not found."

@mcp.tool()
async def list_structures() -> list[str]:
    """List all structure names from the loaded binary."""
    if not ctx_ready:
        return ["❌ Context not ready. Run `setup_context()` first."]
    return [s["name"] for s in ctx.get("data_types", {}).get("structures", [])]

@mcp.tool()
async def get_structure(name: str) -> dict:
    """Get details of a specific structure by name."""
    if not ctx_ready:
        return {"error": "Context not ready. Run `setup_context()` first."}
    for s in ctx.get("data_types", {}).get("structures", []):
        if s["name"] == name:
            return s
    return {"error": f"Structure '{name}' not found."}

@mcp.tool()
async def list_enums() -> list[str]:
    """List all enum names from the loaded binary."""
    if not ctx_ready:
        return ["❌ Context not ready. Run `setup_context()` first."]
    return [e["name"] for e in ctx.get("data_types", {}).get("enums", [])]

@mcp.tool()
async def get_enum(name: str) -> dict:
    """Get details of a specific enum by name."""
    if not ctx_ready:
        return {"error": "Context not ready. Run `setup_context()` first."}
    for e in ctx.get("data_types", {}).get("enums", []):
        if e["name"] == name:
            return e
    return {"error": f"Enum '{name}' not found."}

@mcp.tool()
async def list_function_definitions() -> list[str]:
    """List all function definition names from the loaded binary."""
    if not ctx_ready:
        return ["❌ Context not ready. Run `setup_context()` first."]
    return [f["name"] for f in ctx.get("data_types", {}).get("function_definitions", [])]

@mcp.tool()
async def get_function_definition(name: str) -> dict:
    """Get details of a specific function definition by name."""
    if not ctx_ready:
        return {"error": "Context not ready. Run `setup_context()` first."}
    for f in ctx.get("data_types", {}).get("function_definitions", []):
        if f["name"] == name:
            return f
    return {"error": f"Function definition '{name}' not found."}

if __name__ == "__main__":
    mcp.run(transport="stdio")
