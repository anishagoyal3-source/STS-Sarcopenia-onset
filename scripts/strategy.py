import opensim as osim, numpy as np, sys, csv, os
# Global trunk inclination (thorax long axis vs vertical, from IK) and knee-to-hip peak extension moment ratio (Table 3).
# Run from the folder that holds Subject_<ID>/ ; writes results/trunk_strategy.csv
exec(open('scripts/io_helpers.py').read())
ROWS=[]
T={'1106151':(0.838,1.704),'1106231':(1.125,1.677),'1106301':(1.195,1.837),'1110111':(1.109,1.750)}
for s,(so,end) in T.items():
    m=osim.Model(f'Subject_{s}/Subject_{s}_scaled_model.osim'); st=m.initSystem()
    tb=osim.TimeSeriesTable(f'Subject_{s}/Subject_{s}_IK_redo.mot'); t=np.array(tb.getIndependentColumn()); labs=list(tb.getColumnLabels())
    cs=m.getCoordinateSet(); body=m.getBodySet().get('thorax') if m.getBodySet().contains('thorax') else None
    if body is None: print([m.getBodySet().get(i).getName() for i in range(m.getBodySet().getSize())][:30]); sys.exit()
    lean=[]; 
    for i in range(0,len(t)):
        row=tb.getRowAtIndex(i)
        for k,l in enumerate(labs):
            if not cs.contains(l): continue
            c=cs.get(l); v=row[k]
            if c.getMotionType()==1: v=np.radians(v)
            c.setValue(st,v,False)
        m.assemble(st); m.realizePosition(st)
        R=body.getTransformInGround(st).R(); y=np.array([R.get(r,1) for r in range(3)])  # thorax long axis
        lean.append(np.degrees(np.arctan2(y[0],y[1])))  # +x = forward
    lean=np.array(lean); base=np.median(lean[t<0.3]); i=np.argmax(lean)
    h,d=None,None
    F=rd(f'Subject_{s}/ID_v46.sto'); ft=F['time']; k=(ft>=so)&(ft<=end)
    def col(j,x):
        n=[c for c in F if c.startswith(f'{j}_{x}_') and 'beta' not in c][0]; return -F[n][k]
    hip=(col('hip_flexion','r')+col('hip_flexion','l')); knee=(col('knee_angle','r')+col('knee_angle','l'))
    print(s,f"seated lean {base:5.1f}  peak lean {lean[i]:5.1f} at {1000*(t[i]-so):+5.0f} ms re seat-off; lean at seat-off {np.interp(so,t,lean):5.1f};",
          f"peak hip {hip.max():5.1f} knee {knee.max():5.1f} Nm (both legs); knee/hip peak {knee.max()/hip.max():.2f}; knee/hip impulse {np.trapezoid(np.clip(knee,0,None),ft[k])/np.trapezoid(np.clip(hip,0,None),ft[k]):.2f}")
    ROWS.append([s,round(base,1),round(float(lean[i]),1),round(1000*(t[i]-so)),round(float(np.interp(so,t,lean)),1),round(hip.max(),1),round(knee.max(),1),round(knee.max()/hip.max(),2)])
os.makedirs('results',exist_ok=True)
with open('results/trunk_strategy.csv','w',newline='') as fh:
    csv.writer(fh).writerows([['subject','seated_incl_deg','peak_incl_deg','t_peak_after_seatoff_ms','incl_at_seatoff_deg','peak_hip_ext_both_legs_Nm','peak_knee_ext_both_legs_Nm','knee_to_hip_peak_ratio']]+ROWS)
