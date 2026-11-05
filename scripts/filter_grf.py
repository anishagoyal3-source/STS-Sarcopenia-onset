"""Low-pass the force-plate data at the same cutoff as the kinematics (zero-lag 2nd-order Butterworth),
write <kinetics>_lp6.mot and ExternalLoads_lp6.xml, then run ID -> ID_grf6.sto"""
import sys, os, glob, numpy as np, opensim as osim
ROOT = os.environ.get('STS_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # folder holding Subject_<ID>/
from scipy.signal import butter, filtfilt
s=sys.argv[1]; fc=float(sys.argv[2]) if len(sys.argv)>2 else 6.0
os.chdir(os.path.join(ROOT, f'Subject_{s}'))
src=glob.glob('*_kinetics.mot')[0]; L=open(src).read().splitlines(); i=[k for k,l in enumerate(L) if l.strip()=='endheader'][0]
hdr=L[:i+2]; cols=L[i+1].split('\t'); d=np.array([[float(v) for v in l.split()] for l in L[i+2:] if l.strip()])
fs=1/np.median(np.diff(d[:,0])); b,a=butter(2,fc/(fs/2))
out=d.copy()
for k,c in enumerate(cols):
    if c.strip()=='time': continue
    out[:,k]=filtfilt(b,a,d[:,k])
dst=src.replace('.mot',f'_lp{int(fc)}.mot')
with open(dst,'w') as f:
    f.write('\n'.join(hdr)+'\n'); np.savetxt(f,out,fmt='%.8f',delimiter='\t')
el=open('ExternalLoads.xml').read().replace(src,dst); open(f'ExternalLoads_lp{int(fc)}.xml','w').write(el)
t=osim.InverseDynamicsTool(); t.setModelFileName(f'Subject_{s}_scaled_model.osim')
t.setCoordinatesFileName(f'Subject_{s}_IK_redo.mot'); t.setLowpassCutoffFrequency(fc)
t.setExternalLoadsFileName(f'ExternalLoads_lp{int(fc)}.xml'); t.setStartTime(0); t.setEndTime(2.34)
ex=osim.ArrayStr(); ex.append('Muscles'); t.setExcludedForces(ex); t.setResultsDir('.'); t.setOutputGenForceFileName(f'ID_grf{int(fc)}.sto'); t.run()
print(s,'fs',round(fs),'done')
