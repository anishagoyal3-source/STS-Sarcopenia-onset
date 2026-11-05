import numpy as np, opensim as osim, csv
from scipy.signal import butter, filtfilt
osim.Logger.setLevelString('error')
def rd(p):
    L=open(p).read().splitlines(); i=[k for k,l in enumerate(L) if l.strip()=='endheader'][0]
    h=L[i+1].split('\t'); d=np.array([[float(v) for v in l.split()] for l in L[i+2:] if l.strip()]); return {n.strip():d[:,k] for k,n in enumerate(h)}
coords=['pelvis_tx','pelvis_ty','pelvis_tilt','hip_flexion_r','hip_flexion_l','knee_angle_r','knee_angle_l','ankle_angle_r','ankle_angle_l','flex_extension']
fcs=np.arange(1,25.5,0.5); fs=150
w=csv.writer(open('results/winter_residual_cutoffs.csv','w',newline='')); w.writerow(['subject']+coords)
allfc=[]
for s in ['1106151','1106231','1106301','1110111']:
    K=rd(f'Subject_{s}/Subject_{s}_IK_redo.mot'); m=osim.Model(f'Subject_{s}/Subject_{s}_scaled_model.osim'); cs=m.getCoordinateSet()
    row=[s]
    for c in coords:
        x=K[c]; x=x if (c.startswith('pelvis_t') or cs.get(c).getMotionType()==1) else np.degrees(x)
        x=x*100 if c.startswith('pelvis_t') else x   # cm
        xp=np.concatenate([x[::-1][:-1],x,x[::-1][1:]])  # reflect-pad to reduce end effects
        R=[]
        for fc in fcs:
            b,a=butter(2,fc/(fs/2)); y=filtfilt(b,a,xp)[len(x)-1:2*len(x)-1]
            R.append(np.sqrt(np.mean((x-y)**2)))
        R=np.array(R); tail=fcs>=15                       # noise region: linear fit over 15-25 Hz
        p=np.polyfit(fcs[tail],R[tail],1); thr=p[1]       # intercept = noise RMS (Winter)
        fc_opt=fcs[np.argmax(R<=thr)] if (R<=thr).any() else np.nan
        row.append(fc_opt); allfc.append(fc_opt)
    w.writerow(row); print(s, dict(zip(coords,row[1:])))
a=np.array(allfc); print('overall median',np.nanmedian(a),'range',np.nanmin(a),np.nanmax(a))
