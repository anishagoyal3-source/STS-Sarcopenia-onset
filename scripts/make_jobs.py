"""Write jobs_all.txt: one Static Optimization run per line
   SUBJECT STRENGTH T0 T1 TAG MODEL KINEMATICS
STRENGTH multiplies every muscle's maximum isometric force (run_so.py).
Conditions (weakness w = 0-70% in 5% steps unless noted):
  orig  : as-published models, strength = 1 - w            (tags base, s95 ... s30; strength kept in the tag)
  hd    : 1106151 with hip/trunk corrections, 1 - w         (hd_wXX)          <- main analysis for 1106151
  ms2   : strength x (m / m_ref)^(2/3) x (1 - w)             (ms2_wXX)
  pk    : strength x (m / m_ref) x (1 - w)                   (pk_wXX)
  rra   : RRA-adjusted models/kinematics at levels around onset (rra_sXX, rrahd_wXX)
m_ref = 75.337 kg (generic Full Body Model).  1106151 uses the hip-corrected model for hd, ms2, pk and rrahd.
Time window = seat-off to end of rise (95% of COM rise) for each subject."""
M_REF = 75.337
MASS = {'1106151': 57.49, '1106231': 83.59, '1106301': 89.19, '1110111': 88.69}
WIN  = {'1106151': (0.838, 1.724), '1106231': (1.124, 1.664), '1106301': (1.198, 1.844), '1110111': (1.111, 1.797)}
SCALED = lambda s: f'Subject_{s}_scaled_model.osim'
HD = 'Subject_1106151_hipdoubled.osim'
IK = lambda s: f'Subject_{s}_IK_redo.mot'
W = range(0, 75, 5); jobs = []
for s, (t0, t1) in WIN.items():
    for w in W:   # unscaled (for 1106151 this is the unmodified-model sensitivity check)
        jobs.append((s, round(1 - w/100, 5), t0, t1, 'base' if w == 0 else f's{100-w:02d}', SCALED(s), IK(s)))
    for pre, k in (('ms2', (MASS[s]/M_REF)**(2/3)), ('pk', MASS[s]/M_REF)):
        for w in W:
            jobs.append((s, round(k*(1 - w/100), 5), t0, t1, f'{pre}_w{w:02d}', HD if s == '1106151' else SCALED(s), IK(s)))
for w in W:
    jobs.append(('1106151', round(1 - w/100, 5), *WIN['1106151'], f'hd_w{w:02d}', HD, IK('1106151')))
# residual-reduction sensitivity: levels bracketing each limb's onset
for w in (45, 50, 55, 60, 65, 70):
    jobs.append(('1106151', round(1 - w/100, 5), 0.838, 1.704, f'rrahd_w{w:02d}', 'Subject_1106151_RRA_r2_hd.osim', 'RRA_r2/r2_Kinematics_q.sto'))
RRA_W = {'1106231': (5, 10, 15, 20, 25, 30), '1106301': (5, 10, 15, 20, 25), '1110111': (25, 30, 35, 40)}
for s, ws in RRA_W.items():
    for w in ws:
        jobs.append((s, round(1 - w/100, 5), *WIN[s], f'rra_s{100-w:02d}', f'Subject_{s}_RRA_r2.osim', 'RRA_r2_q150.sto'))
with open('jobs_all.txt', 'w') as fh:
    for j in jobs: fh.write(' '.join(str(v) for v in j) + '\n')
print(len(jobs), 'jobs written to jobs_all.txt')
