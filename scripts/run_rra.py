import sys, os, opensim as osim
ROOT = os.environ.get('STS_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # folder holding Subject_<ID>/
s, t0, t1, tag = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
os.chdir(os.path.join(ROOT, f'Subject_{s}'))
m = osim.Model(f'Subject_{s}_scaled_model.osim'); m.initSystem()
cs = m.getCoordinateSet()
dep = set()
for i in range(m.getConstraintSet().getSize()):
    c = osim.CoordinateCouplerConstraint.safeDownCast(m.getConstraintSet().get(i))
    if c: dep.add(c.getDependentCoordinateName())
free = [cs.get(i).getName() for i in range(cs.getSize()) if not cs.get(i).get_locked() and cs.get(i).getName() not in dep]
acts = osim.ForceSet(); tasks = osim.CMC_TaskSet()
for nm,ax in [('FX',(1,0,0)),('FY',(0,1,0)),('FZ',(0,0,1))]:
    a=osim.PointActuator('pelvis'); a.setName(nm); a.set_direction(osim.Vec3(*ax)); a.set_force_is_global(True)
    a.set_point(m.getBodySet().get('pelvis').getMassCenter()); a.set_point_is_global(False)
    a.setOptimalForce(float(os.environ.get('RF','10'))); a.setMinControl(-1e4); a.setMaxControl(1e4); acts.cloneAndAppend(a)
for nm,ax in [('MX',(1,0,0)),('MY',(0,1,0)),('MZ',(0,0,1))]:
    a=osim.TorqueActuator(); a.setName(nm); a.set_bodyA('pelvis'); a.set_bodyB('ground'); a.set_axis(osim.Vec3(*ax)); a.set_torque_is_global(True)
    a.setOptimalForce(float(os.environ.get('RM','5'))); a.setMinControl(-1e4); a.setMaxControl(1e4); acts.cloneAndAppend(a)
for n in free:
    a = osim.CoordinateActuator(n); a.setName(('resid_' if n.startswith('pelvis') else 'act_') + n)
    if n.startswith('pelvis_t'): a.setOptimalForce(4.0)      # residual forces: expensive -> RRA alters kinematics/mass
    elif n.startswith('pelvis'): a.setOptimalForce(2.0)      # residual moments
    else: a.setOptimalForce(500.0)                           # joint actuators: cheap
    a.setMinControl(-1e4); a.setMaxControl(1e4); (None if n.startswith("pelvis") else acts.cloneAndAppend(a))
    tk = osim.CMC_Joint(); tk.setName(n); tk.setCoordinateName(n)
    tk.setKP(100); tk.setKV(20); tk.setActive(True, False, False)
    tk.setWeight(20.0 if (n.startswith('pelvis') or n in ('flex_extension','lat_bending','axial_rotation')) else 1.0); tasks.cloneAndAppend(tk)
acts.printToXML(f'RRA_acts_{tag}.xml'); tasks.printToXML(f'RRA_tasks_{tag}.xml')
r = osim.RRATool()
r.setName(tag); r.setModelFilename(f'Subject_{s}_scaled_model.osim')
fsf = osim.ArrayStr(); fsf.append(f'RRA_acts_{tag}.xml'); r.setForceSetFiles(fsf); r.setReplaceForceSet(True)
r.setTaskSetFileName(f'RRA_tasks_{tag}.xml'); r.setDesiredKinematicsFileName(f'Subject_{s}_IK_redo.mot')
r.setLowpassCutoffFrequency(6); r.setExternalLoadsFileName('ExternalLoads.xml')
r.setInitialTime(t0); r.setFinalTime(t1); r.setResultsDir(f'RRA_{tag}')
r.setAdjustCOMToReduceResiduals(True); r.setAdjustedCOMBody('torso'); r.setOutputModelFileName(f'Subject_{s}_RRA_{tag}.osim')
r.setMaximumNumberOfSteps(30000); r.setMaxDT(1); r.setMinDT(1e-8); r.setErrorTolerance(1e-5)
r.printToXML(f'RRA_setup_{tag}.xml')
osim.RRATool(f'RRA_setup_{tag}.xml').run()
