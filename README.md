

GHIDRA_CONTEXT_JSON="/Users/tomi/Documents/ghidra_mcp/ghidra_context.json" \
/Users/tomi/Downloads/ghidra_11.3.1_PUBLIC/support/analyzeHeadless \
/Users/tomi/Documents/ghidra_mcp ghidra_ctx \
-import /Users/tomi/Documents/ghidra_mcp/crackme \
-overwrite \
-scriptPath /Users/tomi/Documents/ghidra_mcp \
-postScript export_context.py \
-deleteProject

gcc -Wall hello.c -o crackme
