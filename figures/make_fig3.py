"""Figure 3. Run from the repository root:  python figures/make_fig3.py
A: body mass vs first-limb onset under the three strength conditions; B: seat-off vs lumbar flexion ROM;
C: peak hip/knee extension moment per kg vs per-kg-scaled onset for each limb.
Values come from results/SO_all_scenarios_summary.csv, results/COM_ROM_fixed.csv and Table 1."""
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11.5,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#555','axes.linewidth':0.8})
S=['1106151','1106231','1106301','1110111']; INK='#222'
C={'1106151':'#2563a8','1106231':'#d97a1e','1106301':'#2e8b57','1110111':'#7b4fa0'}
MASS={'1106151':57.49,'1106231':83.59,'1106301':89.19,'1110111':88.69}
XOFF={'1106151':0,'1106231':0,'1106301':0.9,'1110111':-0.9}
FIRST={'unscaled':{'1106151':50,'1106231':10,'1106301':10,'1110111':30},
       'ms2':{'1106151':45,'1106231':15,'1106301':20,'1110111':35},
       'pk':{'1106151':35,'1106231':20,'1106301':25,'1110111':40}}
SO={'1106151':0.838,'1106231':1.125,'1106301':1.195,'1110111':1.109}
LUMB={'1106151':30.6,'1106231':51.6,'1106301':41.8,'1110111':39.5}
# per limb: (peak extensor moment Nm/kg = max(hip,knee), per-kg-scaled onset)
LIMB={('1106151','R'):(1.08,35),('1106151','L'):(0.81,50),('1106231','R'):(0.99,35),('1106231','L'):(1.26,20),
      ('1106301','R'):(1.23,30),('1106301','L'):(1.25,25),('1110111','R'):(0.98,40),('1110111','L'):(1.08,40)}
fig=plt.figure(figsize=(12,9.6)); gs=fig.add_gridspec(2,4,hspace=0.38,wspace=0.6)
a=fig.add_subplot(gs[0,0:2]); b=fig.add_subplot(gs[0,2:4]); c=fig.add_subplot(gs[1,1:3])
# A
for s in S:
    x=MASS[s]+XOFF[s]; u,m2,p=FIRST['unscaled'][s],FIRST['ms2'][s],FIRST['pk'][s]
    a.annotate('',xy=(x,p),xytext=(x,u),arrowprops=dict(arrowstyle='-|>',color=C[s],lw=1.4,alpha=0.6,shrinkA=6,shrinkB=7))
    a.scatter(x,u,s=80,facecolor='white',edgecolor=C[s],lw=1.8,zorder=3)
    a.scatter(x,m2,s=40,marker='D',facecolor='#bbb',edgecolor='white',lw=0.8,zorder=3)
    a.scatter(x,p,s=90,facecolor=C[s],edgecolor='white',lw=1.2,zorder=4)
    lx,ha={'1106151':(x+1.3,'left'),'1106231':(x-1.3,'right'),'1106301':(x+1.3,'left'),'1110111':(x-1.3,'right')}[s]
    ly={'1106151':42,'1106231':15,'1106301':17,'1110111':35}[s]
    a.text(lx,ly,s,color=C[s],fontsize=9.5,ha=ha,va='center',fontweight='bold')
a.set_xlim(50,96); a.set_ylim(0,60); a.set_xlabel('Body mass (kg)'); a.set_ylabel('First-limb onset (% weakness)')
a.set_title('A. Body mass vs. first-limb onset',loc='left',fontsize=11); a.grid(alpha=0.25,lw=0.6)
a.legend(handles=[Line2D([],[],ls='',marker='o',ms=8,mfc='white',mec='#555',mew=1.6,label='Unscaled'),
                  Line2D([],[],ls='',marker='D',ms=6,mfc='#bbb',mec='white',label='Scaled by mass$^{2/3}$'),
                  Line2D([],[],ls='',marker='o',ms=8,mfc='#555',mec='white',label='Scaled per kg')],
         loc='upper center',bbox_to_anchor=(0.52,1.0),frameon=False,fontsize=9)
# B
for s in S:
    mk='^' if s=='1106151' else 'o'
    b.scatter(SO[s],LUMB[s],s=100,marker=mk,facecolor=C[s],edgecolor='white',lw=1.2,zorder=3)
    b.text(SO[s]+0.012,LUMB[s]+(1.3 if s!='1110111' else -2.6),s,color=C[s],fontsize=9.5,fontweight='bold')
b.set_xlim(0.78,1.3); b.set_ylim(25,57); b.set_xlabel('Seat-off time (s)'); b.set_ylabel('Lumbar flexion ROM (°)')
b.set_title('B. Seat-off time vs. lumbar flexion ROM',loc='left',fontsize=11); b.grid(alpha=0.25,lw=0.6)
b.legend(handles=[Line2D([],[],ls='',marker='^',ms=8,mfc='#777',mec='white',label='Female'),Line2D([],[],ls='',marker='o',ms=8,mfc='#777',mec='white',label='Male')],loc='lower right',frameon=False,fontsize=9)
# C
off={('1106151','R'):(0.012,1.8),('1106151','L'):(0.012,1.8),('1106231','R'):(-0.012,-3.2),('1106231','L'):(-0.012,-3.2),
     ('1106301','R'):(-0.012,2.0),('1106301','L'):(0.008,2.0),('1110111','R'):(-0.012,1.8),('1110111','L'):(0.012,1.8)}
for (s,l),(x,y) in LIMB.items():
    c.scatter(x,y,s=85,facecolor=C[s] if l=='R' else 'white',edgecolor=C[s],lw=1.8,zorder=3)
    dx,dy=off[(s,l)]; c.text(x+dx,y+dy,f'{s} {l}',color=C[s],fontsize=8.5,ha='left' if dx>0 else 'right')
c.text(0.97,0.96,'Spearman ρ = −0.92\n(8 limbs; not independent)',transform=c.transAxes,ha='right',va='top',fontsize=9,color='#444')
c.set_xlim(0.72,1.34); c.set_ylim(10,58); c.set_xlabel('Peak hip or knee extension moment (Nm/kg)'); c.set_ylabel('Onset, scaled per kg (% weakness)')
c.set_title('C. Demand per kg vs. onset (scaled per kg)',loc='left',fontsize=11); c.grid(alpha=0.25,lw=0.6)
c.legend(handles=[Line2D([],[],ls='',marker='o',ms=8,mfc='#777',mec='#777',label='Right limb'),Line2D([],[],ls='',marker='o',ms=8,mfc='white',mec='#777',mew=1.6,label='Left limb')],loc='lower left',frameon=False,fontsize=9)
fig.tight_layout(); fig.savefig('figures/fig3.png',dpi=250,bbox_inches='tight')
