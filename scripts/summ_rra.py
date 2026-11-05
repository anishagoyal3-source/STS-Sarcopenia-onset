"""Table 4: onset (R / L) after residual reduction, and the maximum kinematic adjustment RRA required.
Onset = lowest tested weakness at which hip or knee |reserve| > 1 Nm (non-converged frames excluded).
Subject 1106151 uses the hip/trunk-corrected RRA model (rrahd_wXX tags, XX = weakness %);
the male subjects use rra_sXX tags (XX = strength kept, weakness = 100 - XX).
Max adjustment = largest |position error| (RRA r2_pErr.sto) over the rising phase:
translations of the pelvis (cm) and all rotational coordinates (deg).  Run from the folder holding Subject_<ID>/."""
import numpy as np, glob, re, os, csv
exec(open('scripts/io_helpers.py').read())            # rd()
RISE={'1106151':(0.838,1.704),'1106231':(1.125,1.677),'1106301':(1.195,1.837),'1110111':(1.109,1.750)}
out=[]
for s,(t0,t1) in RISE.items():
    lv={}
    for d in glob.glob(f'Subject_{s}/SO_rra*'):
        tag=d.split('SO_')[1]
        if s=='1106151' and not tag.startswith('rrahd_w'): continue
        if s!='1106151' and not re.match(r'rra_s\d+$',tag): continue
        w=int(tag.split('_w')[1]) if 'rrahd' in tag else 100-int(tag.split('_s')[1])
        F=rd(glob.glob(d+'/*_StaticOptimization_force.sto')[0]); t=F['time']; keep=np.ones(len(t),bool)
        lg=f'Subject_{s}/so_{tag}.log'
        if os.path.exists(lg):
            for b in re.findall(r'could not find a solution at time = ([0-9.eE+-]+)',open(lg).read()): keep&=np.abs(t-float(b.rstrip('.')))>1e-6
        lv[w]={x:max(np.abs(F[f'reserve_{j}_{x}'][keep]).max() for j in ('hip_flexion','knee_angle')) for x in 'rl'}
    on={x:min([w for w in sorted(lv) if lv[w][x]>1] or [None]) for x in 'rl'}
    P=rd(f'Subject_{s}/RRA_r2/r2_pErr.sto'); t=P['time']; k=(t>=t0)&(t<=t1)
    tr=max(np.abs(P[c][k]).max() for c in P if c in ('pelvis_tx','pelvis_ty','pelvis_tz'))*100
    rot=max(np.abs(P[c][k]).max() for c in P if c!='time' and c not in ('pelvis_tx','pelvis_ty','pelvis_tz'))*180/np.pi
    out.append([s,on['r'],on['l'],round(tr,1),round(rot,1),' '.join(str(w) for w in sorted(lv))])
os.makedirs('results',exist_ok=True)
with open('results/table4_rra_onset_and_adjustment.csv','w',newline='') as fh:
    csv.writer(fh).writerows([['subject','onset_RRA_R_pct','onset_RRA_L_pct','max_translation_cm','max_rotation_deg','weakness_levels_tested']]+out)
for r in out: print(r)
