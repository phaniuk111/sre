#!/usr/bin/env python3
"""Run every hands-on command in hands.py and record what it prints (hands_out.json).
build.py shows that output in the course, so "what you should see" is never made up."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hands

ROOT = os.path.dirname(HERE)
out, bad = {}, 0
only = sys.argv[1:]
for key, t in hands.T.items():
    if only and key not in only:
        continue
    for which, typed in (('cmd', t['see']), ('change_cmd', t['change_see'])):
        if typed:
            out[f'{key}.{which}'] = typed
            continue
        r = subprocess.run(['bash', '-c', t[which]], cwd=ROOT, capture_output=True, text=True, timeout=120)
        text = (r.stdout + r.stderr).rstrip()
        out[f'{key}.{which}'] = text
        if r.returncode != 0 or 'Traceback' in text or not text:
            bad += 1
            print(f'!! {key}.{which} exit={r.returncode}\n{text[-600:]}\n')
if not only:
    json.dump(out, open(os.path.join(HERE, 'hands_out.json'), 'w'), indent=1, ensure_ascii=False)
else:
    for k, v in out.items():
        print(f'--- {k}\n{v}\n')
print(f'{len(out)} commands run, {bad} failed')
sys.exit(1 if bad else 0)
