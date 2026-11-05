"""Table 2 + baseline activation: peak reserve torque and % of the rising phase in deficit (|reserve| > 1 Nm)
at 50% weakness, and peak vastus activation at full strength, for the main (unscaled) analysis.
Subject 1106151 uses the hip/trunk-corrected model runs (hd_*); the male subjects use the as-published models (s*).
All frames of the Static Optimization window (seat-off to end of rise, as run) are used, including
frames where the optimizer did not fully converge (as in the paper's Table 2).  Run from the folder that holds Subject_<ID>/."""
import numpy as np, re, os, csv
exec(open('scripts/io_helpers.py').read())          # provides rd()
RISE={'1106151':(0.838,1.704),'1106231':(1.125,1.677),'1106301':(1.195,1.837),'1110111':(1.109,1.750)}
TAG={'1106151':('hd_w50','hd_w00'),'1106231':('s50','base'),'1106301':('s50','base'),'1110111':('s50','base')}
os.makedirs('results',exist_ok=True); rows=[]
for s,(t0,t1) in RISE.items():
    w50,w00=TAG[s]; f=f'Subject_{s}/SO_{w50}/{w50}_StaticOptimization_force.sto'; F=rd(f); t=F['time']
    lg=f'Subject_{s}/so_{w50}.log'
    bad=[float(x.rstrip('.')) for x in re.findall(r'could not find a solution at time = ([0-9.eE+-]+)',open(lg).read())] if os.path.exists(lg) else []
    k=np.ones(len(t),bool)
    A=rd(f'Subject_{s}/SO_{w00}/{w00}_StaticOptimization_activation.sto')
    for j,J in [('hip_flexion','hip'),('knee_angle','knee'),('ankle_angle','ankle')]:
        for x,X in [('r','R'),('l','L')]:
            r=np.abs(F[f'reserve_{j}_{x}'][k])
            rows.append([s,J,X,round(float(r.max()),2),round(100*float((r>1).mean()))])
    rows.append([s,'vastus_lateralis_peak_activation_full_strength','R',round(float(A['vaslat_r'].max()),2),''])
    rows.append([s,'vastus_lateralis_peak_activation_full_strength','L',round(float(A['vaslat_l'].max()),2),''])
with open('results/table2_reserve_and_deficit_at_50pct.csv','w',newline='') as fh:
    csv.writer(fh).writerows([['subject','joint_or_measure','limb','peak_reserve_Nm_or_activation','pct_rise_in_deficit']]+rows)
for r in rows: print(r)
