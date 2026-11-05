"""Static optimization for one STS trial.
usage: run_so.py SUBJECT STRENGTH T0 T1 OUTTAG
STRENGTH = fraction of max isometric force kept (1.0 = healthy, 0.6 = 40% weakness)
Reserve actuators: lower-limb sagittal coords get WEAK reserves (optimal force 1 Nm),
so any reserve torque there = torque the muscles could not supply.
Pelvis residuals and upper-body reserves are cheap (they are not the question)."""
import sys, os, opensim as osim
ROOT = os.environ.get('STS_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # folder holding Subject_<ID>/
subj, strength, t0, t1, tag = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
d = os.path.join(ROOT, f'Subject_{subj}'); os.chdir(d)
m = osim.Model(os.environ.get('SO_MODEL', f'Subject_{subj}_scaled_model.osim'))
# weakness: uniform scaling of all muscle max isometric force
mus = m.getMuscles()
for i in range(mus.getSize()):
    mu = mus.get(i); mu.setMaxIsometricForce(mu.getMaxIsometricForce() * strength)
LEG = {'hip_flexion','hip_adduction','hip_rotation','knee_angle','ankle_angle'}
cs = m.getCoordinateSet()
dep = set()
for i in range(m.getConstraintSet().getSize()):
    c = osim.CoordinateCouplerConstraint.safeDownCast(m.getConstraintSet().get(i))
    if c: dep.add(c.getDependentCoordinateName())
for i in range(cs.getSize()):
    c = cs.get(i); n = c.getName()
    if c.get_locked() or n in dep: continue
    a = osim.CoordinateActuator(n); a.setName('reserve_' + n)
    base = n[:-2] if n.endswith(('_r','_l')) else n
    if n.startswith('pelvis'):
        a.setOptimalForce(1000.0)          # residuals: cheap
    elif base in LEG:
        a.setOptimalForce(1.0)             # weak reserve: the measurement
    else:
        a.setOptimalForce(100.0)           # trunk/arm/neck: cheap, not studied
    a.setMinControl(-1e6); a.setMaxControl(1e6)
    m.addForce(a)
m.finalizeConnections(); m.printToXML(f'SO_model_{tag}.osim')
tool = osim.AnalyzeTool()
tool.setName(tag); tool.setModelFilename(f'SO_model_{tag}.osim')
tool.setCoordinatesFileName(os.environ.get('SO_KIN', f'Subject_{subj}_IK_redo.mot'))   # the CORRECT file (not degfixed)
tool.setLowpassCutoffFrequency(6)
tool.setExternalLoadsFileName(os.environ.get('SO_EL','ExternalLoads.xml'))
tool.setInitialTime(t0); tool.setFinalTime(t1)
tool.setResultsDir(f'SO_{tag}')
so = osim.StaticOptimization(); so.setStartTime(t0); so.setEndTime(t1)
so.setUseModelForceSet(True); so.setActivationExponent(2); so.setUseMusclePhysiology(True)
so.setConvergenceCriterion(1e-4); so.setMaxIterations(int(os.environ.get("SO_MAXIT","500")))
tool.getAnalysisSet().cloneAndAppend(so)
tool.printToXML(f'SO_setup_{tag}.xml')
osim.AnalyzeTool(f'SO_setup_{tag}.xml').run()
