# Subject-Specific Onset of Muscle Insufficiency During Sit-to-Stand Under Simulated Sarcopenia

This repository holds the code, setup files, derived data and results for the paper *Subject-Specific Onset of Muscle Insufficiency During Sit-to-Stand Under Simulated Sarcopenia* (A. Goyal). Using four subject-specific OpenSim models, it finds the lowest uniform muscle weakness at which static optimization needs more than 1 Nm of reserve torque at the hip, knee or ankle of each limb to reproduce the recorded sit-to-stand.

## Contents

```
README.md
scripts/            analysis pipeline (Python 3, OpenSim 4.6 Python API)
figures/            scripts that draw Figures 1-3, and the PNGs used in the paper
results/            CSV outputs behind every table and figure
data/
  Subject_<ID>/     setup files, derived kinematics/kinetics and modified models for each subject
  static_optimization_results_*.zip   every Static Optimization force output and log used in the paper (two parts; plus `static_optimization_results_sensitivity.zip` for the filter/window sensitivity runs)
```

## Requirements

- OpenSim 4.6 with its Python bindings, e.g. `conda install -c opensim-org opensim=4.6`
- Python 3.11. Tested with numpy 2.4 / scipy 1.17 (OpenSim environment) and matplotlib 3.11 (figures).

## Data

The raw motion-capture, force-plate and scaled-model files come from the public SimTK dataset by Caruthers et al.:
**https://simtk.org/projects/osufullbody_sts** (accessed [add date]). Those files are not redistributed here.

Set it up as follows:

1. Download the dataset.
2. For each subject, create a folder `Subject_<ID>/` in the repository root. The IDs are 1106151, 1106231, 1106301 and 1110111.
3. Copy into each folder:
   - the trial files `<ID>_STS05.trc` and `<ID>_STS05_kinetics.mot`
   - the scaled model, saved as `Subject_<ID>_scaled_model.osim`
4. Copy the contents of `data/Subject_<ID>/` into the same folder.
5. (Optional) Unzip the `data/static_optimization_results_*.zip` files in the repository root. This restores every Static Optimization result, so you can skip step 6 of the pipeline.

Run every command below from the repository root. Each script finds the subject folders there, or in the folder named by `STS_ROOT`.

## Pipeline

| Step | Command | Output |
|---|---|---|
| 1. Inverse kinematics | `opensim-cmd run-tool Subject_<ID>/IK_setup_fixed.xml` (run inside the subject folder) | `Subject_<ID>_IK_redo.mot` (provided) |
| 2. Inverse dynamics (6 Hz) | `python scripts/run_id.py <ID>` | `ID_v46.sto` (provided) |
| 2a. Filter cut-off check (Winter residual analysis) | `python scripts/winter.py` | `results/winter_residual_cutoffs.csv` |
| 2b. Marker error | `python scripts/marker_err.py` | `results/ik_marker_errors_summary.csv` |
| 3. Centre of mass, seat-off, ROM | `python scripts/run_bk.py <ID>` then `python scripts/com_table.py` | `results/COM_ROM_fixed.csv` |
| 4. Pelvis residuals and interlimb NSI | `python scripts/residuals_asym.py` | `results/residuals_rise.csv`, `results/asymmetry_NSI_rise.csv` |
| 5. Residual reduction | `python scripts/run_rra.py <ID> <t0> <t1> r2`, then for the male subjects `python scripts/resample.py Subject_<ID>/RRA_r2/r2_Kinematics_q.sto Subject_<ID>/Subject_<ID>_IK_redo.mot Subject_<ID>/RRA_r2_q150.sto`. Windows: 1106151 0.80–1.80 s, 1106231 1.08–1.77 s, 1106301 1.15–1.94 s, 1110111 1.07–1.90 s | `Subject_<ID>_RRA_r2.osim`, `RRA_r2/` (provided) |
| 6a. Hip/trunk correction for 1106151 | `python scripts/make_hipdoubled_model.py` | `Subject_1106151_hipdoubled.osim`, `Subject_1106151_RRA_r2_hd.osim` (provided) |
| 6b. Static optimization, all conditions (216 runs) | `python scripts/make_jobs.py` then `sh scripts/run_jobs.sh` (set `PYTHON=` to the OpenSim Python if needed) | `Subject_<ID>/SO_<tag>/`, `so_<tag>.log` |
| 7. Onset summary | `python scripts/summarize_onset.py` | `results/SO_all_scenarios_summary.csv` |
| 8. Table values | `python scripts/peak_moments.py`, `python scripts/deficit_stats.py`, `python scripts/summ_rra.py`, `python scripts/strategy.py`, `python scripts/make_supplementary_table.py`, `python scripts/deficit_timing.py` | see the table below |
| 8a. Sensitivity to filtering and window | `cat jobs_sens.txt \| xargs -P 2 -L 1 sh -c 'cd Subject_$0 && SO_MAXIT=3000 SO_MODEL=$5 SO_LP=$6 python ../scripts/run_so.py $0 $1 $2 $3 $4 > so_$4.log 2>&1'` then `python scripts/sensitivity_summary.py` | `results/sensitivity_onset.csv` |
| 9. Figures | `python figures/make_fig1_fig2.py`, `python figures/make_fig3.py` | `figures/fig1.png` to `fig3.png` |

## Where each result in the paper comes from

| Paper item | Script | File |
|---|---|---|
| Table 1: peak hip/knee moments (Nm/kg) | `peak_moments.py` | `results/table1_peak_moments_per_kg.csv` |
| Table 1: onsets (unscaled and per-kg), earliest joint | `summarize_onset.py` | `results/SO_all_scenarios_summary.csv` (conditions `hd` for 1106151, `orig` for the men, `pk`) |
| Table 2: onset, peak reserve and % of rise in deficit at 50% | `summarize_onset.py`, `deficit_stats.py` | `results/SO_all_scenarios_summary.csv`, `results/table2_reserve_and_deficit_at_50pct.csv` |
| Baseline vastus lateralis activation | `deficit_stats.py` | `results/table2_reserve_and_deficit_at_50pct.csv` |
| Table 3: ROM, seat-off, COM rise, velocity and timing | `com_table.py` | `results/COM_ROM_fixed.csv` |
| Table 3: trunk inclination, knee-to-hip moment ratio | `strategy.py` | `results/trunk_strategy.csv` |
| Table 4: onset after RRA, kinematic adjustment | `summ_rra.py` | `results/table4_rra_onset_and_adjustment.csv` |
| Table 5: interlimb NSI; pelvis residuals | `residuals_asym.py` | `results/asymmetry_NSI_rise.csv`, `results/residuals_rise.csv` |
| Timing and direction of each deficit at onset |`deficit_timing.py` | `results/deficit_timing.csv` |
| Sensitivity to filter cut-off (4/8 Hz) and window boundaries | `sensitivity_summary.py` | `results/sensitivity_onset.csv` |
| Supplementary Table S1: all strength conditions | `make_supplementary_table.py` | `results/Supplementary_Table_S1.csv` |
| Figure 1 | `figures/make_fig1_fig2.py` | `figures/fig1.png` |
| Figure 2 | `figures/make_fig1_fig2.py` | `figures/fig2.png` |
| Figure 3 | `figures/make_fig3.py` | `figures/fig3.png` |

## Method notes

- **Weakness:** every muscle's maximum isometric force is multiplied by `STRENGTH`, set in `run_so.py`. The weakness levels run from 0 to 70% in 5% steps.
- **Reserve actuators:** the lower-limb sagittal coordinates get reserve actuators with an optimal force of 1 Nm. Pelvis residuals get 1000 and the other upper-body coordinates get 100. Onset is the lowest weakness at which a joint's peak |reserve| exceeds 1 Nm in that limb.
- **Strength conditions (the run tag prefix):**
  - `orig`: models as published. The tag stores the strength kept, so `s70` means 30% weakness.
  - `hd`: Subject 1106151 with the hip-doubling and trunk corrections already present in the male models. This is the main analysis for 1106151.
  - `ms2`: strength × (m / 75.337)^(2/3).
  - `pk`: strength × m / 75.337, which gives equal strength per kilogram.
  
  75.337 kg is the mass of the generic Full Body Model. Subject 1106151's `ms2` and `pk` runs start from the corrected model.
- **Non-converged frames:** these are listed in each `so_<tag>.log`. `summarize_onset.py` and `summ_rra.py` exclude them when finding onset. `deficit_stats.py` (Table 2 magnitudes) uses every frame.
- **Unreported runs:** the RRA runs for 1106151 tagged `rra_s60`, `rra_s65` and `rra_s70` used her unmodified model. They are included in the zip but not reported in the paper.

## Citation

If you use this code, please cite the paper and the original dataset (Caruthers et al., SimTK `osufullbody_sts`).
