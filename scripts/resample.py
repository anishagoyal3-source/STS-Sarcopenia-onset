"""Resample RRA kinematics (1000 Hz) onto the original IK frame times (150 Hz) so SO runs at the same frames as the main analysis."""
import sys, numpy as np
src, ik, dst = sys.argv[1:4]
def rdall(p):
    L=open(p).read().splitlines(); i=[k for k,l in enumerate(L) if l.strip()=='endheader'][0]
    return L[:i+1], L[i+1].split('\t'), np.array([[float(v) for v in l.split()] for l in L[i+2:] if l.strip()])
hdr,cols,d=rdall(src); _,_,di=rdall(ik)
t=di[:,0]; t=t[(t>=d[0,0])&(t<=d[-1,0])]
out=np.column_stack([t]+[np.interp(t,d[:,0],d[:,k]) for k in range(1,d.shape[1])])
hdr=[('nRows=%d'%len(t)) if h.startswith('nRows') else h for h in hdr]
with open(dst,'w') as f: f.write('\n'.join(hdr)+'\n'+'\t'.join(cols)+'\n'); np.savetxt(f,out,fmt='%.8f',delimiter='\t')
