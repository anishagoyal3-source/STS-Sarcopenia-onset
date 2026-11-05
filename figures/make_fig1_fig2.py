"""Figures 1 and 2. Run from the repository root (the folder holding Subject_<ID>/):  python figures/make_fig1_fig2.py
Figure 1: hip, knee and ankle extensor moments from inverse dynamics (ID_v46.sto), right solid / left dashed, rising phase shaded.
Figure 2: onset severity by joint, limb and subject for the main (unscaled) analysis; values typed in from results/SO_all_scenarios_summary.csv
(Subject 1106151 = hip/trunk-corrected model)."""
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#555','axes.linewidth':0.8})
S=['1106151','1106231','1106301','1110111']
INFO={'1106151':('F',57.49,1.70,0.838,1.704,30.6),'1106231':('M',83.59,None,1.125,1.677,51.6),'1106301':('M',89.19,1.87,1.195,1.837,41.8),'1110111':('M',88.69,None,1.109,1.750,39.5)}
COL={'Hip':'#2563a8','Knee':'#d97a1e','Ankle':'#2e8b57'}; INK='#222'; MUTED='#777'
def rd(p):
    L=open(p).read().splitlines(); i=[k for k,l in enumerate(L) if l.strip()=='endheader'][0]
    h=[n.strip() for n in L[i+1].split('\t')]; d=np.array([[float(v) for v in l.split()] for l in L[i+2:] if l.strip()]); return h,d
# ---------- Figure 1 ----------
fig,axs=plt.subplots(2,2,figsize=(12,7.2),sharey=True)
for ax,s in zip(axs.flat,S):
    h,d=rd(f'Subject_{s}/ID_v46.sto'); t=d[:,0]; sex,m,_,so,re,_=INFO[s]
    ax.axvspan(so,re,color='#000',alpha=0.05,lw=0)
    for j,c in [('hip_flexion','Hip'),('knee_angle','Knee'),('ankle_angle','Ankle')]:
        for side,ls in [('r','-'),('l','--')]:
            k=[i for i,n in enumerate(h) if n.startswith(f'{j}_{side}_') and 'beta' not in n][0]
            ax.plot(t,-d[:,k],ls,color=COL[c],lw=1.8)
    ax.axhline(0,color=MUTED,lw=0.6)
    for x,lab in [(so,'seat-off'),(re,'end of rise')]:
        ax.axvline(x,color=MUTED,lw=0.8,ls=':'); ax.text(x,1.0,lab,transform=ax.get_xaxis_transform(),ha='center',va='bottom',fontsize=8.5,color=MUTED)
    pass  # title left to the caption: ax.set_title(f'Subject {s} ({sex}, {m:.1f} kg)',fontsize=11.5,pad=16); ax.grid(alpha=0.25,lw=0.6)
    ax.set_xlabel('Time (s)')
for ax in axs[:,0]: ax.set_ylabel('Extensor moment (Nm)')
hand=[Line2D([],[],color=COL[c],lw=2,label=c) for c in COL]+[Line2D([],[],color=INK,lw=1.8,ls='-',label='Right'),Line2D([],[],color=INK,lw=1.8,ls='--',label='Left'),plt.Rectangle((0,0),1,1,color='#000',alpha=0.08,label='Rising phase')]
fig.legend(handles=hand,loc='lower center',ncol=6,frameon=False,bbox_to_anchor=(0.5,-0.01))
fig.tight_layout(rect=(0,0.05,1,1)); fig.savefig('figures/fig1.png',dpi=250,bbox_inches='tight'); plt.close()
# ---------- Figure 2 ----------
# onset (%) per subject: hipR hipL kneeR kneeL ankR ankL ; None = no onset up to 70%
ON={'1106151':[50,65,55,60,None,None],'1106231':[30,10,30,10,None,None],'1106301':[15,15,15,10,None,65],'1110111':[30,45,30,30,None,70]}
cols=['Hip R','Hip L','Knee R','Knee L','Ankle R','Ankle L']
import matplotlib.colors as mc
cmap=mc.LinearSegmentedColormap.from_list('seq',['#7a1f12','#c8553d','#f0b38a','#fbe9dc'])  # dark = early onset
fig,ax=plt.subplots(figsize=(9.5,4.6))
A=np.array([[np.nan if v is None else v for v in ON[s]] for s in S],float)
im=ax.imshow(A,cmap=cmap,vmin=5,vmax=70,aspect='auto')
for i,s in enumerate(S):
    for j,v in enumerate(ON[s]):
        if v is None:
            ax.add_patch(plt.Rectangle((j-.5,i-.5),1,1,facecolor='#eeeeec',edgecolor='none')); ax.text(j,i,'none',ha='center',va='center',color=MUTED,fontsize=10)
        else: ax.text(j,i,f'{v}%',ha='center',va='center',fontsize=12,fontweight='bold',color='white' if v<=35 else INK)
for k in range(1,6): ax.axvline(k-.5,color='white',lw=2 if k%2 else 5)
for k in range(1,4): ax.axhline(k-.5,color='white',lw=2)
ax.set_xticks(range(6),cols); ax.set_yticks(range(4),[f'{s}\n({INFO[s][0]}, {INFO[s][1]:.1f} kg)' for s in S])
ax.tick_params(length=0); [sp.set_visible(False) for sp in ax.spines.values()]
cb=fig.colorbar(im,ax=ax,fraction=0.04,pad=0.02); cb.set_label('Onset severity (% weakness)'); cb.outline.set_visible(False)
pass  # title left to the caption: ax.set_title('Onset of muscle insufficiency by joint, limb, and subject\n(lower % = insufficient at milder weakness; "none" = no onset up to 70%)',fontsize=11)
fig.tight_layout(); fig.savefig('figures/fig2.png',dpi=250,bbox_inches='tight'); plt.close()
print('figures/fig1.png, figures/fig2.png written')
