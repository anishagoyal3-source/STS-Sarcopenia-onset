"""Apply the published hip/trunk strength corrections to Subject 1106151's model.

In the original study (Caruthers 2017 dissertation) the hip muscles' maximum isometric
forces were doubled and the erector spinae (2500 N) and rectus abdominis (348.76 N) were
strengthened. The three male models in the dataset contain these changes; the female
model (1106151) does not. Muscle forces in the dataset are not scaled to body size, so the
male models are identical in every muscle: this script copies each muscle's maximum
isometric force from a male model (1106231) wherever the female model's value differs.

usage (from the folder that holds Subject_<ID>/):  python make_hipdoubled_model.py
output: Subject_1106151/Subject_1106151_hipdoubled.osim (and Subject_1106151_RRA_r2_hd.osim if the RRA model exists)
"""
import opensim as osim
ref = osim.Model('Subject_1106231/Subject_1106231_scaled_model.osim')
R = {ref.getMuscles().get(i).getName(): ref.getMuscles().get(i).getMaxIsometricForce() for i in range(ref.getMuscles().getSize())}
def apply(src, dst):
  m = osim.Model(src); changed = []
  for i in range(m.getMuscles().getSize()):
    mu = m.getMuscles().get(i); f0 = mu.getMaxIsometricForce(); f1 = R[mu.getName()]
    if abs(f0 - f1) > 1e-6:
        mu.setMaxIsometricForce(f1); changed.append((mu.getName(), round(f0, 2), round(f1, 2)))
  m.printToXML(dst); print(f'{dst}: {len(changed)} muscles changed')
  for c in changed: print('  %-22s %9.2f -> %9.2f N' % c)

import os
apply('Subject_1106151/Subject_1106151_scaled_model.osim', 'Subject_1106151/Subject_1106151_hipdoubled.osim')
# same correction for the RRA-adjusted model (run run_rra.py first), used for the RRA sensitivity analysis
if os.path.exists('Subject_1106151/Subject_1106151_RRA_r2.osim'):
    apply('Subject_1106151/Subject_1106151_RRA_r2.osim', 'Subject_1106151/Subject_1106151_RRA_r2_hd.osim')
