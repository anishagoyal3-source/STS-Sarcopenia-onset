"""Supplementary Table S1: onset (R / L) by joint under three muscle-strength conditions.
Reads results/SO_all_scenarios_summary.csv (written by summarize_onset.py); writes results/Supplementary_Table_S1.csv.
Unscaled row for 1106151 = hip/trunk-corrected model ('hd'); the male subjects' unscaled rows = as-published models ('orig')."""
import csv
rows = list(csv.DictReader(open('results/SO_all_scenarios_summary.csv')))
K = ['hip_R', 'hip_L', 'knee_R', 'knee_L', 'ankle_R', 'ankle_L']
def onset(s, c):
    rs = sorted([r for r in rows if r['subject'] == s and r['condition'] == c], key=lambda r: int(r['weakness_pct']))
    o = [next((int(r['weakness_pct']) for r in rs if float(r[k]) > 1), None) for k in K]
    return o, sum(int(r['failed_frames']) for r in rs)
f = lambda v: '–' if v is None else f'{v}%'
out = [['Subject', 'Muscle strength', 'Hip (R / L)', 'Knee (R / L)', 'Ankle (R / L)', 'First limb (onset)', 'Non-converged frames (all levels)']]
for s in ['1106151', '1106231', '1106301', '1110111']:
    for c, lab in [('orig', 'Unscaled'), ('ms2', 'Scaled by (m/m_ref)^2/3'), ('pk', 'Scaled by m/m_ref (equal per kg)')]:
        o, fl = onset(s, 'hd' if (s == '1106151' and c == 'orig') else c)
        R = min(v for v in o[0::2] if v); L = min(v for v in o[1::2] if v)
        first = f'Both ({R}%)' if R == L else (f'Right ({R}%)' if R < L else f'Left ({L}%)')
        out.append([s, lab] + [f'{f(o[i])} / {f(o[i+1])}' for i in (0, 2, 4)] + [first, str(fl)])
csv.writer(open('results/Supplementary_Table_S1.csv', 'w', newline='')).writerows(out)
for r in out: print(r)
