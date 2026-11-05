import numpy as np, opensim as osim, xml.etree.ElementTree as ET, glob, csv
osim.Logger.setLevelString('error')
def rd(p):
    L=open(p).read().splitlines(); i=[k for k,l in enumerate(L) if l.strip()=='endheader'][0]
    h=L[i+1].split('\t'); d=np.array([[float(v) for v in l.split()] for l in L[i+2:] if l.strip()]); return {n.strip():d[:,k] for k,n in enumerate(h)}
w=csv.writer(open('results/ik_marker_errors_summary.csv','w',newline=''))
w.writerow(['subject','window','mean_RMS_cm','max_RMS_cm','max_marker_error_cm','worst_marker','worst_marker_mean_err_cm','frames_max_over_4cm_pct'])
for s in ['1106151','1106231','1106301','1110111']:
    d=f'Subject_{s}'; r=ET.parse(f'{d}/IK_setup_fixed.xml').getroot()
    use={t.get('name') for t in r.iter('IKMarkerTask') if t.findtext('apply').strip()=='true' and float(t.findtext('weight'))>0}
    m=osim.Model(f'{d}/Subject_{s}_scaled_model.osim'); st=m.initSystem(); cs=m.getCoordinateSet(); ms=m.getMarkerSet()
    trc=osim.TimeSeriesTableVec3(glob.glob(f'{d}/*_STS*.trc')[0]); unit=trc.getTableMetaDataString('Units') if trc.hasTableMetaDataKey('Units') else 'mm'
    sc=0.001 if unit.lower().startswith('mm') else 1.0
    lab=list(trc.getColumnLabels()); tt=np.array(trc.getIndependentColumn())
    K=rd(f'{d}/Subject_{s}_IK_redo.mot'); names=[n for n in K if n!='time']
    mk=[n for n in use if n in lab and ms.contains(n)]
    E=np.full((len(K['time']),len(mk)),np.nan)
    for f,t in enumerate(K['time']):
        for n in names:
            c=cs.get(n); v=K[n][f]; c.setValue(st, np.radians(v) if c.getMotionType()==1 else v, False)
        m.realizePosition(st); k=np.argmin(abs(tt-t)); row=trc.getRowAtIndex(int(k))
        for j,n in enumerate(mk):
            e=row[lab.index(n)]; ex=np.array([e[0],e[1],e[2]])*sc
            if np.isnan(ex).any(): continue
            p=ms.get(n).getLocationInGround(st); E[f,j]=np.linalg.norm(np.array([p[0],p[1],p[2]])-ex)
    tK=K['time']
    for win,mask in [('full trial',np.ones(len(tK),bool))]:
        Ew=E[mask]; rms=np.sqrt(np.nanmean(Ew**2,axis=1)); mx=np.nanmax(Ew,axis=1); wm=np.nanmean(Ew,axis=0); worst=mk[int(np.nanargmax(wm))]
        w.writerow([s,win,round(100*rms.mean(),2),round(100*rms.max(),2),round(100*mx.max(),2),worst,round(100*wm.max(),2),round(100*(mx>0.04).mean(),1)])
        print(f"{s} markers used {len(mk)} | RMS mean {100*rms.mean():.2f} cm max {100*rms.max():.2f} | max marker err {100*mx.max():.2f} cm | worst marker {worst} mean {100*wm.max():.2f} cm | frames >4cm {100*(mx>0.04).mean():.0f}%")
        top=np.argsort(-wm)[:4]; print('    top:',[(mk[i],round(100*wm[i],2)) for i in top])
