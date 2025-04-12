import os
import json
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ghidra")

# === Configuration ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GHIDRA_CONTEXT_JSON = os.path.join(BASE_DIR, "ghidra_context.json")
GHIDRA_PROJECT_DIR = BASE_DIR
GHIDRA_PROJECT_NAME = "ghidra_ctx"
EXPORT_SCRIPT_NAME = "export_context.py"
EXPORT_SCRIPT_PATH = os.path.join(BASE_DIR, EXPORT_SCRIPT_NAME)

# === Internal state ===
ctx_ready = False
last_binary = None

def run_headless(ghidra_path: str, binary_path: str):
    analyze_headless = os.path.join(ghidra_path, "support", "analyzeHeadless")
    cmd = [
        analyze_headless,
        GHIDRA_PROJECT_DIR,
        GHIDRA_PROJECT_NAME,
        "-import", binary_path,
        "-overwrite",
        "-scriptPath", os.path.dirname(EXPORT_SCRIPT_PATH),
        "-postScript", os.path.basename(EXPORT_SCRIPT_PATH),
        "-deleteProject"
    ]

    env = os.environ.copy()
    env["GHIDRA_CONTEXT_JSON"] = GHIDRA_CONTEXT_JSON

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)

    # Read and print output line by line
    for line in process.stdout:
        print(line, end='')

    process.wait()
    return process

def load_context():
    with open(GHIDRA_CONTEXT_JSON) as f:
        return json.load(f)

def is_context_ready():
    return os.path.exists(GHIDRA_CONTEXT_JSON)

@mcp.tool()
async def setup_context(
    ghidra_path: str = "/Users/tomi/Downloads/ghidra_11.3.1_PUBLIC",
    binary_path: str = "/Users/tomi/Documents/ghidra_mcp/crackme"
) -> str:
    """Run Ghidra headless decompilation to export binary context."""
    global ctx_ready, last_binary

    if not os.path.isdir(ghidra_path):
        return f"❌ Ghidra path '{ghidra_path}' is not valid."
    if not os.path.isfile(binary_path):
        return f"❌ Binary file '{binary_path}' does not exist."

    result = run_headless(ghidra_path, binary_path)

    if result.returncode != 0:
        return f"❌ Ghidra failed with return code {result.returncode}."

    if not is_context_ready():
        return f"❌ Export script ran but no context was saved."

    ctx_ready = True
    last_binary = os.path.basename(binary_path)
    return f"✅ Context loaded for '{last_binary}'."

@mcp.tool()
async def list_functions() -> list[str]:
    """List all function names from the loaded binary."""
    if not is_context_ready():
        return ["❌ Context not ready. Run `setup_context()` first."]
    ctx = load_context()
    return [f["name"] for f in ctx["functions"]]

@mcp.tool()
async def get_pseudocode(name: str) -> str:
    """Get pseudocode for a specific function by name."""
    if not is_context_ready():
        return "❌ Context not ready. Run `setup_context()` first."
    ctx = load_context()
    for f in ctx["functions"]:
        if f["name"] == name:
            return f["pseudocode"]
    return f"❌ Function '{name}' not found."

@mcp.tool()
async def hello_world(name: str) -> str:
    return f"Hello {name}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
