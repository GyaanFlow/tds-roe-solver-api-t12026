# inspect_ga3_questions.py
import re

content = open("scratch/ga3_raw.js", encoding="utf-8").read()

# Let's find each return statement return{id:..., title:...}
# We can find all blocks that look like `return{id:...,title:...,...}`
pattern = r'return\{id:(\w+),title:([^\},]+),weight:([^\},]+),question:([^\},]+),answer:async\s+([a-zA-Z0-9_]+)=>(.*?)\}'
matches = re.finditer(pattern, content, re.DOTALL)

print("Parsed Questions:")
for i, m in enumerate(matches):
    qid_var = m.group(1)
    qtitle_var = m.group(2)
    qweight_var = m.group(3)
    qans_param = m.group(5)
    qans_body = m.group(6)
    
    # Resolve the literal id and title values from the JS file
    # Let's search for assignments to the variable name (e.g. qid_var = "...")
    # Typically, at the bottom of the IIFE/module, there is something like qid_var="actual-id", qtitle_var="actual-title"
    literal_id = qid_var
    literal_title = qtitle_var
    
    id_match = re.search(rf'{qid_var}="([^"]+)"', content)
    if id_match:
        literal_id = id_match.group(1)
    else:
        # try single quotes
        id_match = re.search(rf"{qid_var}='([^']+)'", content)
        if id_match:
            literal_id = id_match.group(1)
            
    title_match = re.search(rf'{qtitle_var}="([^"]+)"', content)
    if title_match:
        literal_title = title_match.group(1)
    else:
        title_match = re.search(rf"{qtitle_var}='([^']+)'", content)
        if title_match:
            literal_title = title_match.group(1)
            
    needs_api = "deployed API base URL" in qans_body or "deployed /extract" in qans_body or "deployed /dynamic-extract" in qans_body
    
    # Check if the code does validation on URL
    is_url = "http://" in qans_body or "https://" in qans_body or "URL" in qans_body
    
    print(f"\n{i+1}. Variable QID: {qid_var} -> Literal ID: {literal_id}")
    print(f"   Title: {literal_title}")
    print(f"   API Server Question?: {needs_api or (is_url and qid_var != 'q-youtube-metadata-filter-server')}")
    # print the first 200 chars of answer code to inspect
    print(f"   Code snippet: {qans_body[:200].strip()}...")
