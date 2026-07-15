import re

with open('hf_space/app.py', encoding='utf-8') as f:
    content = f.read()

marker_end = '</html>\"\"\"'
idx = content.find(marker_end)
second_idx = content.find(marker_end, idx + 1)

if second_idx != -1:
    keep_before = content[:idx + len(marker_end)]
    keep_after = content[second_idx + len(marker_end):]
    new_content = keep_before + keep_after
    with open('hf_space/app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Fixed. New line count:', new_content.count('\n'))
else:
    print('No duplicate found -- file is already clean')
