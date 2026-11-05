import numpy as np, os, opensim as osim
def rd(p):
    L=open(p).read().splitlines(); i=[k for k,l in enumerate(L) if l.strip()=='endheader'][0]
    h=L[i+1].split('\t'); d=np.array([[float(v) for v in l.split()] for l in L[i+2:] if l.strip()]); return {n.strip():d[:,k] for k,n in enumerate(h)}
mass={'1106151':57.49,'1106231':83.59,'1106301':89.19,'1110111':88.69}
osim.Logger.setLevelString('error')
rows=[]
for s,m in mass.items():
    d=f'Subject_{s}'; P=rd(f'{d}/BK_fixed/bk_BodyKinematics_pos_global.sto'); V=rd(f'{d}/BK_fixed/bk_BodyKinematics_vel_global.sto')
    t=P['time']; y=P['center_of_mass_Y']; vy=V['center_of_mass_Y']; vx=V['center_of_mass_X']
    G=rd(f'{d}/'+[f for f in os.listdir(d) if f.endswith('_kinetics.mot')][0]); tg=G['time']
    Fy=G['ground_force_vy']+G['1_ground_force_vy']; BW=m*9.81
    above=Fy>=0.85*BW; i=np.where(~above[:np.argmax(Fy)])[0]; so=tg[i[-1]+1] if len(i) else tg[0]
    # independent check: integrate GRF after seat-off from BK velocity at seat-off
    k0=np.argmin(abs(t-so)); vy_grf=vy[k0]+np.concatenate([[0],np.cumsum(((np.interp(t,tg,Fy)-BW)/m)[k0:-1]*np.diff(t[k0:]))])
    ip=k0+np.argmax(vy[k0:]); ip_all=np.argmax(vy)
    y0=y[:k0].min() if k0>0 else y[0]; rise=y.max()-y[0]
    iend=np.argmax(y>=y[0]+0.95*rise)
    M=osim.Model(f'{d}/Subject_{s}_scaled_model.osim'); cs=M.getCoordinateSet()
    K=rd(f'{d}/Subject_{s}_IK_redo.mot')
    def deg(n):
        v=K[n]; return v if cs.get(n).getMotionType()==1 else np.degrees(v)
    rom=lambda n:np.ptp(deg(n))
    rows.append(dict(s=s,so=so,peakVy=vy.max(),t_peak=t[ip_all],peakVy_after_so=vy[ip],tpk_after_so=t[ip]-so,
        vy_grf_peak=vy_grf.max(),rise=rise,end=t[iend],risedur=t[iend]-so,
        pelvis=rom('pelvis_tilt'),hip=(rom('hip_flexion_r'),rom('hip_flexion_l')),knee=(rom('knee_angle_r'),rom('knee_angle_l')),
        ankle=(rom('ankle_angle_r'),rom('ankle_angle_l')),trunk=rom('flex_extension'),
        mt={n:cs.get(n).getMotionType() for n in ['pelvis_tilt','hip_flexion_r','knee_angle_r','ankle_angle_r','flex_extension']}))
import csv
w=csv.writer(open("results/COM_ROM_fixed.csv","w",newline=""))
w.writerow(["subject","seat_off_s","COM_rise_m","peak_COM_Vy_mps","t_peak_after_seatoff_ms","GRF_integrated_peak_Vy_mps","rise_end_95pct_s","rise_duration_s","pelvis_ROM","hip_R","hip_L","knee_R","knee_L","ankle_R","ankle_L","trunk_ROM"])
for r in rows: w.writerow([r["s"],round(r["so"],3),round(r["rise"],3),round(r["peakVy"],2),round((r["t_peak"]-r["so"])*1000),round(r["vy_grf_peak"],2),round(r["end"],3),round(r["risedur"],3),round(r["pelvis"],1)]+[round(x,1) for x in (*r["hip"],*r["knee"],*r["ankle"])]+[round(r["trunk"],1)])
for r in rows:
    print(f"{r['s']}: seat-off {r['so']:.3f}s | COM rise {r['rise']:.3f} m | peak COM Vy {r['peakVy']:.2f} m/s @ {r['t_peak']:.3f}s ({(r['t_peak']-r['so'])*1000:.0f} ms after seat-off) | GRF-integrated peak Vy {r['vy_grf_peak']:.2f} | 95%-rise at {r['end']:.3f}s, rise dur {r['risedur']:.3f}s")
    print(f"     ROM deg: pelvis {r['pelvis']:.1f} hip {r['hip'][0]:.1f}/{r['hip'][1]:.1f} knee {r['knee'][0]:.1f}/{r['knee'][1]:.1f} ankle {r['ankle'][0]:.1f}/{r['ankle'][1]:.1f} trunk {r['trunk']:.1f}   motiontypes {r['mt']}")
