"""Table 1 / Results: peak hip and knee extension moments per kg for each limb over the Static Optimization window
(seat-off to end of rise), from inverse dynamics (ID_v46.sto; extension is negative in this model, reported positive).
Run from the folder that holds Subject_<ID>/ ; writes results/table1_peak_moments_per_kg.csv"""
import csv, os
exec(open('scripts/io_helpers.py').read())
WIN = {'1106151': (0.838, 1.724, 57.49), '1106231': (1.124, 1.664, 83.59), '1106301': (1.198, 1.844, 89.19), '1110111': (1.111, 1.797, 88.69)}
out = [['subject', 'mass_kg', 'hip_R_Nm_per_kg', 'hip_L_Nm_per_kg', 'knee_R_Nm_per_kg', 'knee_L_Nm_per_kg', 'ankle_R_Nm_per_kg', 'ankle_L_Nm_per_kg']]
for s, (a, b, m) in WIN.items():
    F = rd(f'Subject_{s}/ID_v46.sto'); t = F['time']; k = (t >= a) & (t <= b); row = [s, m]
    for j in ('hip_flexion', 'knee_angle', 'ankle_angle'):
        for x in 'rl':
            n = [c for c in F if c.startswith(f'{j}_{x}_') and 'beta' not in c][0]
            row.append(round(float((-F[n][k]).max()) / m, 2))
    out.append(row)
os.makedirs('results', exist_ok=True)
csv.writer(open('results/table1_peak_moments_per_kg.csv', 'w', newline='')).writerows(out)
for r in out: print(r)
