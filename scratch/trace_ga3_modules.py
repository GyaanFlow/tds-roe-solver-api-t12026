# trace_ga3_modules.py
import re

content = open("scratch/ga3_raw.js", encoding="utf-8").read()

# Define all the IIFE/module initialization functions we found in the array:
fn_names = ["ue", "pe", "fe", "ge", "ke", "Ie", "Te", "Oe", "_e", "Ee", "et", "it", "pt"]

for name in fn_names:
    # Find the function definition, e.g., `var ue=O(()=>{"use strict";...});`
    # Let's search for `var ue=O(` or `var ue = O(` or `var ue=g(`
    pat = rf"var\s+{name}\s*=\s*\w+\(\(\)\s*=>\s*\{{(.*?)\}}\);"
    m = re.search(pat, content, re.DOTALL)
    if not m:
        # try without variable assignment or simple definition
        pat = rf"function\s+{name}\s*\(.*?\)\s*\{{(.*?)\}}"
        m = re.search(pat, content, re.DOTALL)
        
    if m:
        body = m.group(1)
        # Search for assignments to strings in the body
        # E.g. `Tt="actual-id"`, `Nt="actual-id"`, etc.
        # Find all string assignments of form: `[a-zA-Z0-9_]+="[^"]+"` or `[a-zA-Z0-9_]+='[^']+'`
        str_assigns = re.findall(r'(\b\w+)\s*=\s*(?:"([^"]+)"|\'([^\']+)\')', body)
        assign_dict = {}
        for var_name, d_val, s_val in str_assigns:
            assign_dict[var_name] = d_val if d_val else s_val
            
        # Try to find return value of the default function (often returns {id, title, ...})
        # Let's search for `return{id:` or `return {id:`
        ret_match = re.search(r'return\s*\{.*?id:\s*(\w+),.*?title:\s*(\w+)', body, re.DOTALL)
        qid = "unknown"
        qtitle = "unknown"
        if ret_match:
            id_var = ret_match.group(1)
            title_var = ret_match.group(2)
            qid = assign_dict.get(id_var, id_var)
            qtitle = assign_dict.get(title_var, title_var)
            
        # Let's see if this question's answer function takes a URL
        # We can look for `/backendVerify` and checking of `http` in the answer function
        # E.g. `answer:async \w+=>`
        ans_match = re.search(r'answer\s*:\s*async\s*\w+\s*=>\s*\{(.*?)\}', body, re.DOTALL)
        needs_api = "unknown"
        if ans_match:
            ans_code = ans_match.group(1)
            needs_api = "deployed API base URL" in ans_code or "deployed /extract" in ans_code or "deployed /dynamic-extract" in ans_code or "http://" in ans_code or "https://" in ans_code
            # Special check for audio and other APIs
            if "audio_base64" in ans_code:
                needs_api = True
            if "candidates" in ans_code and "cosine-similarity" in ans_code:
                needs_api = True
            if "arithmetic" in ans_code and "reasoning" in ans_code:
                # wait, let's verify if arithmetic solver microservice needs API
                needs_api = "your API endpoint" in body.lower() or "deployed service" in body.lower() or "microservice" in body.lower() or "http://" in ans_code or "https://" in ans_code
            
        print(f"Name: {name} -> QID: {qid} | Title: {qtitle} | Needs API?: {needs_api}")
        if ans_match:
            print("  Code snippet:", ans_match.group(1)[:250].strip() + "...")
        print("-" * 50)
