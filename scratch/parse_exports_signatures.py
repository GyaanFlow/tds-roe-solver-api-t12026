# parse_exports_signatures.py
import re

content = open("scratch/ga3_raw.js", encoding="utf-8").read()

fn_map = {
    "de": "Lt",
    "he": "$t",
    "me": "Jt",
    "ye": "Vt",
    "ve": "ao",
    "Se": "ro",
    "qe": "io",
    "Ae": "lo",
    "Le": "ho",
    "Ce": "mo",
    "Ze": "Lo",
    "st": "Mo",
    "ht": "jo"
}

for obj_name, fn_name in fn_map.items():
    # Find where the function starts
    # e.g., `async function $t` or `function $t`
    start_pos = -1
    for prefix in [f"async function {fn_name}", f"function {fn_name}"]:
        pos = content.find(prefix)
        if pos != -1:
            start_pos = pos
            break
            
    if start_pos != -1:
        # Get the first 600 characters from start_pos to print the definition and return statement
        snippet = content[start_pos:start_pos+3000]
        # Let's search for the return statement return{id:...}
        ret_match = re.search(r'return\s*\{.*?id:\s*(\w+),\s*title:\s*(\w+)', snippet, re.DOTALL)
        qid = "unknown"
        qtitle = "unknown"
        if ret_match:
            id_var = ret_match.group(1)
            title_var = ret_match.group(2)
            
            # Find the string assignments for id_var and title_var in the snippet or the whole file
            id_val_match = re.search(rf'\b{id_var}\s*=\s*(?:"([^"]+)"|\'([^\']+)\')', content)
            title_val_match = re.search(rf'\b{title_var}\s*=\s*(?:"([^"]+)"|\'([^\']+)\')', content)
            
            id_val = id_val_match.group(1) if id_val_match else id_var
            title_val = title_val_match.group(1) if title_val_match else title_var
            
            print(f"Object: {obj_name} | Fn: {fn_name} | QID: {id_val} | Title: {title_val}")
        else:
            print(f"Object: {obj_name} | Fn: {fn_name} | Return statement not matched in snippet.")
    else:
        print(f"Object: {obj_name} | Fn: {fn_name} | Function not found.")
