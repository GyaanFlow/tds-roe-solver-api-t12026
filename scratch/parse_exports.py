# parse_exports.py
import re

content = open("scratch/ga3_raw.js", encoding="utf-8").read()

# E.g. k(de,{default:()=>Lt,generateYoutubeMetadataTask:()=>le});
# Let's find all calls of k(..., {...})
export_calls = re.findall(r'k\((\w+),\{(.*?)\}\);', content)

print(f"Found {len(export_calls)} export definitions:")
for obj_name, exports in export_calls:
    print(f"Object: {obj_name} -> Exports: {exports}")
    # Let's search for the actual function definitions of the default export
    # e.g., default:()=>Lt -> find function Lt or var Lt = ...
    def_fn = re.search(r'default:\(\)=>(.*?)(?:,|\})', exports)
    if def_fn:
        fn_name = def_fn.group(1).strip()
        # Find function fn_name definition
        fn_pat = rf'(?:async\s+)?function\s+{fn_name}\s*\(.*?\)\s*\{{(.*?)\}}'
        fn_match = re.search(fn_pat, content, re.DOTALL)
        if fn_match:
            fn_body = fn_match.group(1)
            # Find the ID and Title
            # Typically returns something like `{id:t,title:d,weight:n,question:o,answer:...}`
            # Let's find what variables are passed to id and title
            ret_match = re.search(r'return\s*\{.*?id:\s*(\w+),\s*title:\s*(\w+)', fn_body)
            if ret_match:
                id_var = ret_match.group(1)
                title_var = ret_match.group(2)
                
                # Search for assignments to id_var and title_var in the scope
                # Let's search for `id_var="value"`
                id_val_match = re.search(rf'\b{id_var}\s*=\s*(?:"([^"]+)"|\'([^\']+)\')', content)
                title_val_match = re.search(rf'\b{title_var}\s*=\s*(?:"([^"]+)"|\'([^\']+)\')', content)
                
                id_val = id_val_match.group(1) if id_val_match else id_var
                title_val = title_val_match.group(1) if title_val_match else title_var
                
                print(f"  QID: {id_val} | Title: {title_val}")
                
                # Check the answer block
                ans_match = re.search(r'answer\s*:\s*async\s*(\w+)\s*=>\s*\{(.*?)\}', fn_body, re.DOTALL)
                if ans_match:
                    ans_body = ans_match.group(2)
                    # Detect if it's a server API
                    needs_api = "deployed API base URL" in ans_body or "deployed /extract" in ans_body or "deployed /dynamic-extract" in ans_body or "http://" in ans_body or "https://" in ans_body or "audio_base64" in ans_body or "candidates" in ans_body
                    print(f"  Needs Deployed API?: {needs_api}")
                    print(f"  Snippet: {ans_body[:200].strip()}...")
        print("-" * 60)
