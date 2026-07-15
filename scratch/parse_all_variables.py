# parse_all_variables.py
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
    start_pos = -1
    for prefix in [f"async function {fn_name}", f"function {fn_name}"]:
        pos = content.find(prefix)
        if pos != -1:
            start_pos = pos
            break
            
    if start_pos != -1:
        # Get the first 1000 characters from start_pos
        snippet = content[start_pos:start_pos+1000]
        # Let's find assignments like `let t=...` or `let t = ...` or `let t=At`
        # Let's extract the first variable declarations
        decl_match = re.search(r'let\s+(\w+)\s*=\s*(\w+),\s*(\w+)\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|\w+)', snippet)
        
        # Let's look for assignments in the function body
        # E.g. `let t=At` or `let t="some-id"`
        # Let's find all `let` declarations or variable assignments
        assigns = re.findall(r'\b(\w+)\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|\w+)', snippet[:300])
        print(f"Object: {obj_name} | Fn: {fn_name}")
        print("  Assigns in first 300 chars:", assigns)
        
        # Let's look for the actual return statement and print the answer block to see if it makes a fetch request
        ans_match = re.search(r'answer\s*:\s*async\s*\w+\s*=>\s*\{(.*?)\}', snippet, re.DOTALL)
        if ans_match:
            print("  Answer snippet:", ans_match.group(1)[:200].strip() + "...")
        else:
            # Let's search a wider snippet for answer
            snippet_wide = content[start_pos:start_pos+3000]
            ans_match_wide = re.search(r'answer\s*:\s*async\s*\w+\s*=>\s*\{(.*?)\}', snippet_wide, re.DOTALL)
            if ans_match_wide:
                print("  Answer snippet (wide):", ans_match_wide.group(1)[:250].strip() + "...")
        print("-" * 60)
