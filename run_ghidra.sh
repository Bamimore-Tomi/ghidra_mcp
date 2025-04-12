#!/bin/bash

# === Configuration ===
GHIDRA_PATH="/Users/tomi/Downloads/ghidra_11.3.1_PUBLIC"
PROJECT_DIR="/Users/tomi/Documents/ghidra_mcp"
BINARY="$PROJECT_DIR/crackme"
PROJECT_NAME="ghidra_ctx"
SCRIPT_NAME="export_context.py"
OUTPUT_JSON="$PROJECT_DIR/ghidra_context.json"

# === Run Ghidra headless ===
GHIDRA_CONTEXT_JSON="$OUTPUT_JSON" \
"$GHIDRA_PATH/support/analyzeHeadless" \
"$PROJECT_DIR" "$PROJECT_NAME" \
-import "$BINARY" \
-overwrite \
-scriptPath "$PROJECT_DIR" \
-postScript "$SCRIPT_NAME" \
-deleteProject
