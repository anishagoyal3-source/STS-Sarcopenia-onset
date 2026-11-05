import sys, os, opensim as osim
ROOT = os.environ.get('STS_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # folder holding Subject_<ID>/
subj=sys.argv[1]; os.chdir(os.path.join(ROOT, f'Subject_{subj}'))
t=osim.AnalyzeTool(); t.setName('bk'); t.setModelFilename(f'Subject_{subj}_scaled_model.osim')
t.setCoordinatesFileName(f'Subject_{subj}_IK_redo.mot'); t.setLowpassCutoffFrequency(6)
t.setInitialTime(0); t.setFinalTime(2.34); t.setResultsDir('BK_fixed')
bk=osim.BodyKinematics(); bk.setStartTime(0); bk.setEndTime(2.34); bk.setInDegrees(True)
a=osim.ArrayStr(); a.append('center_of_mass'); bk.setBodiesToRecord(a)
t.getAnalysisSet().cloneAndAppend(bk); t.printToXML('BK_fixed_setup.xml'); osim.AnalyzeTool('BK_fixed_setup.xml').run()
