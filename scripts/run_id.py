import sys, os, opensim as osim
ROOT = os.environ.get('STS_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # folder holding Subject_<ID>/
s=sys.argv[1]; os.chdir(os.path.join(ROOT, f'Subject_{s}'))
t=osim.InverseDynamicsTool(); t.setModelFileName(f'Subject_{s}_scaled_model.osim')
t.setCoordinatesFileName(f'Subject_{s}_IK_redo.mot'); t.setLowpassCutoffFrequency(float(sys.argv[2]) if len(sys.argv)>2 else 6)
t.setExternalLoadsFileName('ExternalLoads.xml'); t.setStartTime(0); t.setEndTime(2.34)
ex=osim.ArrayStr(); ex.append('Muscles'); t.setExcludedForces(ex)
t.setResultsDir('.'); t.setOutputGenForceFileName(sys.argv[3] if len(sys.argv)>3 else 'ID_v46.sto'); t.run()
