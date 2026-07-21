import json
from pathlib import Path

transcript_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\8b9c65e9-af90-47f2-a539-f7a81daafcac\.system_generated\logs\transcript.jsonl")

dossiers = None
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        # Search in planner response tool calls or system inputs
        tool_calls = data.get("tool_calls") or []
        for tc in tool_calls:
            args = tc.get("args") or {}
            cmd = args.get("CommandLine") or ""
            if "mailroom" in cmd and "propose" in cmd:
                # This might contain a curl command with dossiers
                pass
        
        # Also check content if it has the dossiers
        content = data.get("content") or ""
        if "ga5-mailroom-action-gate/v2" in content and "dossiers" in content:
            try:
                # Find the JSON part
                idx = content.find("{")
                if idx != -1:
                    parsed = json.loads(content[idx:])
                    if parsed.get("operation") == "propose" and len(parsed.get("dossiers", [])) > 20:
                        dossiers = parsed["dossiers"]
            except Exception:
                pass

if dossiers:
    print(f"Extracted {len(dossiers)} dossiers!")
    with open("scratch/stable_dossiers.json", "w", encoding="utf-8") as out:
        json.dump(dossiers, out, indent=2)
else:
    print("Could not find dossiers in content. Let's search inside transcript.jsonl more aggressively.")
