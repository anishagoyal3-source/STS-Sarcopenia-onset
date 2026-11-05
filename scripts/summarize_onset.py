# Onset per joint and limb for every strength condition (unscaled "orig", hip-corrected "hd", mass^(2/3) "ms2", per-kg "pk").
# Peak |reserve| per joint/limb per weakness level, excluding frames where SO reported a failed optimization.
# Writes results/SO_all_scenarios_summary.csv and prints onsets.  Run from the folder that holds Subject_<ID>/.
import numpy as np, os, re, csv
exec(open('scripts/io_helpers.py').read())
J=['hip_flexion','knee_angle','ankle_angle']
def tagname(pre,w): return ('base' if w==0 else f's{100-w:02d}') if pre=='orig' else f'{pre}_w{w:02d}'
rows=[]
for s in ['1106151','1106231','1106301','1110111']:
  for pre in ['orig','hd','ms2','pk']:
    for w in range(0,75,5):
      tag=tagname(pre,w); f=f'Subject_{s}/SO_{tag}/{tag}_StaticOptimization_force.sto'; lg=f'Subject_{s}/so_{tag}.log'
      if not os.path.exists(f): continue
      F=rd(f); bad=[float(x.rstrip('.')) for x in re.findall(r'could not find a solution at time = ([0-9.eE+-]+)',open(lg).read())] if os.path.exists(lg) else []
      keep=np.ones(len(F['time']),bool)
      for b in bad: keep&=np.abs(F['time']-b)>1e-6
      r=[round(float(np.abs(F[f'reserve_{j}_{x}'][keep]).max()),2) for j in J for x in 'rl']
      rows.append([s,pre,w,len(bad)]+r)
hdr=['subject','condition','weakness_pct','failed_frames','hip_R','hip_L','knee_R','knee_L','ankle_R','ankle_L']
csv.writer(open('results/SO_all_scenarios_summary.csv','w',newline='')).writerows([hdr]+rows)
for s in ['1106151','1106231','1106301','1110111']:
  for pre in ['orig','hd','ms2','pk']:
    rs=sorted([r for r in rows if r[0]==s and r[1]==pre],key=lambda r:r[2])
    if not rs: continue
    o=[]
    for k in range(6):
      w=[r[2] for r in rs if r[4+k]>1]; o.append(w[0] if w else None)
    print(s,pre.ljust(4),'levels',len(rs),'hipR/L',o[0:2],'kneeR/L',o[2:4],'ankleR/L',o[4:6],'fails',sum(r[3] for r in rs))
