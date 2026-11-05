#!/bin/sh
# Run every Static Optimization job in jobs_all.txt, two at a time.  Run from the folder that holds Subject_<ID>/ and scripts/.
# Each run writes Subject_<ID>/SO_<TAG>/ and a log Subject_<ID>/so_<TAG>.log (non-converged frames are listed in the log).
export STS_ROOT="$(pwd)"
PY=${PYTHON:-python}
cat jobs_all.txt | xargs -P ${NJOBS:-2} -L 1 sh -c 'cd "$STS_ROOT/Subject_$0" && SO_MAXIT=3000 SO_MODEL=$5 SO_KIN=$6 '"$PY"' "$STS_ROOT/scripts/run_so.py" $0 $1 $2 $3 $4 > so_$4.log 2>&1; echo done $0 $4'
