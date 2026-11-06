"""Sensitivity of onset to phase boundaries and filtering (noise).
Runs (made by make_jobs.py --sens / jobs_sens.txt): weakness levels around each limb's onset, main-analysis models
(1106151 hip-corrected; men as published).
  lp4_wXX, lp8_wXX : kinematics low-pass filtered at 4 or 8 Hz instead of 6 Hz, standard window.
  win_wXX          : 6 Hz, window from 50 ms before seat-off to 100% of COM rise; sub-windows are cut from it.
Onset = lowest tested level with |reserve| > 1 Nm (hip/knee/ankle, each limb); non-converged frames excluded.
Writes results/sensitivity_onset.csv.  Run from the folder that holds Subject_<ID>/."""
import numpy as np, glob, re, os, csv
exec(open('scripts/io_helpers.py').read())
SO = {'1106151': 0.838, '1106231': 1.125, '1106301': 1.195, '1110111': 1.109}
END = {'1106151': (1.624, 1.704, 1.977), '1106231': (1.644, 1.677, 1.764), '1106301': (1.797, 1.837, 2.243), '1110111': (1.690, 1.750, 1.924)}  # 90/95/100% COM rise
J = [('hip_flexion', 'hip'), ('knee_angle', 'knee'), ('ankle_angle', 'ankle')]
def load(s, tag):
    F = rd(glob.glob(f'Subject_{s}/SO_{tag}/*_StaticOptimization_force.sto')[0]); t = F['time']; keep = np.ones(len(t), bool)
    lg = f'Subject_{s}/so_{tag}.log'
    if os.path.exists(lg):
        for b in re.findall(r'could not find a solution at time = ([0-9.eE+-]+)', open(lg).read()): keep &= np.abs(t - float(b.rstrip('.'))) > 1e-6
    return F, t, keep
def onset(s, prefix, t0=None, t1=None):
    lv = {}
    for d in glob.glob(f'Subject_{s}/SO_{prefix}_w*'):
        tag = d.split('SO_')[1]; w = int(tag.split('_w')[1]); F, t, keep = load(s, tag)
        k = keep & ((t >= t0) if t0 is not None else True) & ((t <= t1) if t1 is not None else True)
        lv[w] = {f'{J_}_{X}': np.abs(F[f'reserve_{j}_{x}'][k]).max() for j, J_ in J for x, X in (('r', 'R'), ('l', 'L'))}
    ws = sorted(lv); return {key: next((w for w in ws if lv[w][key] > 1), None) for key in lv[ws[0]]}, ws
out = [['subject', 'variant', 'levels_tested', 'hip_R', 'hip_L', 'knee_R', 'knee_L', 'ankle_R', 'ankle_L']]
for s in SO:
    so = SO[s]; e90, e95, e100 = END[s]
    V = [('6 Hz, seat-off to 95% (from win runs)', 'win', so, e95), ('4 Hz filter', 'lp4', None, None), ('8 Hz filter', 'lp8', None, None),
         ('start 50 ms before seat-off', 'win', so - 0.05, e95), ('start 50 ms after seat-off', 'win', so + 0.05, e95),
         ('end at 90% of rise', 'win', so, e90), ('end at 100% of rise', 'win', so, e100)]
    for name, pre, a, b in V:
        o, ws = onset(s, pre, a, b)
        out.append([s, name, ' '.join(map(str, ws))] + [o[k] if o[k] is not None else '>' + str(ws[-1]) for k in ('hip_R', 'hip_L', 'knee_R', 'knee_L', 'ankle_R', 'ankle_L')])
os.makedirs('results', exist_ok=True)
csv.writer(open('results/sensitivity_onset.csv', 'w', newline='')).writerows(out)
for r in out: print(r)
