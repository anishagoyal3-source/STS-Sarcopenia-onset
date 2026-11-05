import numpy as np, os, csv
def rd(p):
    L=open(p).read().splitlines(); i=[k for k,l in enumerate(L) if l.strip()=='endheader'][0]
    h=L[i+1].split('\t'); d=np.array([[float(v) for v in l.split()] for l in L[i+2:] if l.strip()]); return {n.strip():d[:,k] for k,n in enumerate(h)}
mass={'1106151':57.49,'1106231':83.59,'1106301':89.19,'1110111':88.69}
C={r['subject']:r for r in csv.DictReader(open('results/COM_ROM_fixed.csv'))}
cols={'hip':('hip_flexion_r_force','hip_flexion_l_moment'),'knee':('knee_angle_r_moment','knee_angle_l_force'),'ankle':('ankle_angle_r_force','ankle_angle_l_force')}
def nsi(R,L):
    lo=min(R.min(),L.min()); hi=max(R.max(),L.max())
    Rn=(R-lo)/(hi-lo)*100+100; Ln=(L-lo)/(hi-lo)*100+100      # Queen et al. 2020 normalisation (100-200)
    return (Rn-Ln)/np.maximum(Rn,Ln)*100                        # + = right-dominant
res=csv.writer(open('results/residuals_rise.csv','w',newline='')); res.writerow(['subject','resid_F_peak_N','resid_F_peak_pct_maxGRF','resid_M_peak_Nm','resid_M_peak_pct_COMh_x_maxGRF','resid_F_rms_N','resid_M_rms_Nm'])
asy=csv.writer(open('results/asymmetry_NSI_rise.csv','w',newline='')); asy.writerow(['subject','measure','NSI_mean','NSI_sd','NSI_peak_abs','NSI_at_peak_demand','classic_SI_at_peaks_paper_method'])
for s,m in mass.items():
    d=f'Subject_{s}'; D=rd(f'{d}/ID_v46.sto'); t=D['time']; so=float(C[s]['seat_off_s']); end=float(C[s]['rise_end_95pct_s'])
    w=(t>=so)&(t<=end)
    G=rd(f'{d}/'+[f for f in os.listdir(d) if f.endswith('_kinetics.mot')][0])
    Fr=np.interp(t,G['time'],G['ground_force_vy']); Fl=np.interp(t,G['time'],G['1_ground_force_vy'])
    Gmag=np.sqrt(sum(np.interp(t,G['time'],G[p+'ground_force_v'+a])  for p in ['','1_'] for a in 'x')**2+(Fr+Fl)**2+sum(np.interp(t,G['time'],G[p+'ground_force_vz']) for p in ['','1_'])**2)
    rf=np.sqrt(sum(D[f'pelvis_t{a}_force']**2 for a in 'xyz')); rm=np.sqrt(sum(D[f'pelvis_{a}_moment']**2 for a in ['tilt','list','rotation']))
    P=rd(f'{d}/BK_fixed/bk_BodyKinematics_pos_global.sto'); comh=np.interp(t,P['time'],P['center_of_mass_Y'])[w].mean()
    mg=Gmag[w].max()
    res.writerow([s,round(rf[w].max(),1),round(100*rf[w].max()/mg,1),round(rm[w].max(),1),round(100*rm[w].max()/(comh*mg),1),round(np.sqrt((rf[w]**2).mean()),1),round(np.sqrt((rm[w]**2).mean()),1)])
    print(f"{s}: residual F peak {rf[w].max():.0f} N ({100*rf[w].max()/mg:.1f}% max GRF) rms {np.sqrt((rf[w]**2).mean()):.0f} N | residual M peak {rm[w].max():.0f} Nm ({100*rm[w].max()/(comh*mg):.1f}% of COMh*maxGRF) rms {np.sqrt((rm[w]**2).mean()):.0f} Nm")
    meas={'vGRF':(Fr,Fl)}; meas.update({j:(-D[a],-D[b]) for j,(a,b) in cols.items()})  # extensor = positive
    for k,(R,L) in meas.items():
        R=R[w]; L=L[w]; n=nsi(R,L); ip=np.argmax(R+L)
        Rp,Lp=R.max(),L.max(); si=(Rp-Lp)/(0.5*(Rp+Lp))*100
        asy.writerow([s,k,round(n.mean(),1),round(n.std(),1),round(np.abs(n).max(),1),round(n[ip],1),round(si,1)])
        print(f"    {k:6s} NSI mean {n.mean():+6.1f} ± {n.std():4.1f}  |max| {np.abs(n).max():5.1f}  at combined peak {n[ip]:+6.1f}   (old peak-vs-peak SI {si:+6.1f})")
