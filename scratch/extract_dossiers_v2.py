import json
from pathlib import Path

transcript_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\8b9c65e9-af90-47f2-a539-f7a81daafcac\.system_generated\logs\transcript.jsonl")

dossiers = None
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        if '"dossiers"' in line:
            try:
                data = json.loads(line)
                content = data.get("content") or ""
                # Let's extract any JSON substring
                import re
                matches = re.findall(r"\{.*\}", content)
                for m in matches:
                    try:
                        parsed = json.loads(m)
                        if parsed.get("operation") == "propose" and len(parsed.get("dossiers", [])) > 20:
                            dossiers = parsed["dossiers"]
                            break
                    except Exception:
                        pass
                if dossiers:
                    break
            except Exception:
                pass

if dossiers:
    print(f"Extracted {len(dossiers)} dossiers!")
    with open("scratch/stable_dossiers.json", "w", encoding="utf-8") as out:
        json.dump(dossiers, out, indent=2)
else:
    # Let's read transcript_full.jsonl instead
    full_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\8b9c65e9-af90-47f2-a539-f7a81daafcac\.system_generated\logs\transcript_full.jsonl")
    if full_path.exists():
        print("Searching in transcript_full.jsonl...")
        with open(full_path, "r", encoding="utf-8") as f:
            for line in f:
                if '"dossiers"' in line:
                    try:
                        data = json.loads(line)
                        content = data.get("content") or ""
                        import re
                        # Find the first JSON block that matches our pattern
                        start_idx = content.find('{"profile":"ga5-mailroom-action-gate/v2"')
                        if start_idx != -1:
                            # Parse until matching braces or simple json loads
                            # Let's extract from start_idx to the end
                            sub = content[start_idx:]
                            # Trim to end of json
                            end_idx = sub.rfind('}')
                            if end_idx != -1:
                                try:
                                    parsed = json.loads(sub[:end_idx+1])
                                    if parsed.get("operation") == "propose" and len(parsed.get("dossiers", [])) > 20:
                                        dossiers = parsed["dossiers"]
                                        break
                                except Exception as e:
                                    print("Sub-parse err:", e)
                        if dossiers:
                            break
                    except Exception as e:
                        pass
    if dossiers:
        print(f"Extracted {len(dossiers)} dossiers from transcript_full!")
        with open("scratch/stable_dossiers.json", "w", encoding="utf-8") as out:
            json.dump(dossiers, out, indent=2)
    else:
        print("Still nothing.")
