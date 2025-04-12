import os
import json
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.model.symbol import RefType
from ghidra.program.model.listing import CodeUnit
from ghidra.program.model.data import Structure, Enum, FunctionDefinition

GHIDRA_CONTEXT_JSON = os.environ.get("GHIDRA_CONTEXT_JSON", "ghidra_context.json")

decompiler = DecompInterface()
decompiler.openProgram(currentProgram)

functions = []

# Iterate over all functions in the current program
for func in currentProgram.getFunctionManager().getFunctions(True):
    # Decompile the function
    result = decompiler.decompileFunction(func, 30, ConsoleTaskMonitor())
    pseudocode = result.getDecompiledFunction().getC() if result.decompileCompleted() else ""

    # Extract function parameters
    parameters = []
    for param in func.getParameters():
        parameters.append({
            "name": param.getName(),
            "datatype": str(param.getDataType()),
            "storage": str(param.getVariableStorage())
        })

    # Extract local variables
    local_vars = []
    for var in func.getLocalVariables():
        local_vars.append({
            "name": var.getName(),
            "datatype": str(var.getDataType()),
            "storage": str(var.getVariableStorage())
        })

    # Extract global variables referenced in the function
    global_vars = []
    ref_manager = currentProgram.getReferenceManager()
    symbol_table = currentProgram.getSymbolTable()
    for addr in func.getBody().getAddresses(True):
        for ref in ref_manager.getReferencesFrom(addr):
            if ref.getReferenceType() == RefType.READ:
                to_addr = ref.getToAddress()
                symbol = symbol_table.getPrimarySymbol(to_addr)
                if symbol and symbol.isGlobal():
                    global_vars.append({
                        "name": symbol.getName(),
                        "address": str(to_addr)
                    })

    # Extract strings referenced in the function
    strings = []
    for addr in func.getBody().getAddresses(True):
        data = currentProgram.getListing().getDataAt(addr)
        if data and data.hasStringValue():
            strings.append(str(data.getValue()))

    # Extract comments within the function
    comments = []
    for addr in func.getBody().getAddresses(True):
        comment = currentProgram.getListing().getComment(CodeUnit.PLATE_COMMENT, addr)
        if comment:
            comments.append({
                "address": str(addr),
                "comment": comment
            })

    # Append function details to the list
    functions.append({
        "name": func.getName(),
        "entry": hex(func.getEntryPoint().getOffset()),
        "signature": func.getPrototypeString(True, False),
        "parameters": parameters,
        "local_variables": local_vars,
        "global_variables": global_vars,
        "strings": strings,
        "comments": comments,
        "pseudocode": pseudocode
    })

# Extract data types: structures, enums, and function definitions
data_types = {
    "structures": [],
    "enums": [],
    "function_definitions": []
}

dtm = currentProgram.getDataTypeManager()
for dt in dtm.getAllDataTypes():
    if isinstance(dt, Structure):
        members = []
        for i in range(dt.getNumComponents()):
            comp = dt.getComponent(i)
            members.append({
                "name": comp.getFieldName(),
                "datatype": str(comp.getDataType()),
                "offset": comp.getOffset()
            })
        data_types["structures"].append({
            "name": dt.getName(),
            "length": dt.getLength(),
            "members": members
        })
    elif isinstance(dt, Enum):
        values = []
        for name in dt.getNames():
            values.append({
                "name": name,
                "value": dt.getValue(name)
            })
        data_types["enums"].append({
            "name": dt.getName(),
            "length": dt.getLength(),
            "values": values
        })
    elif isinstance(dt, FunctionDefinition):
        # Extract function definition details
        func_def = {
            "name": dt.getName(),
            "return_type": str(dt.getReturnType()),
            "parameters": []
        }
        for param in dt.getArguments():
            func_def["parameters"].append({
                "name": param.getName(),
                "datatype": str(param.getDataType())
            })
        data_types["function_definitions"].append(func_def)

with open(GHIDRA_CONTEXT_JSON, "w") as f:
    json.dump({
        "program": currentProgram.getName(),
        "functions": functions,
        "data_types": data_types
    }, f, indent=2)
