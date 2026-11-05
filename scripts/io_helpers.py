"""Shared helper: read an OpenSim .sto/.mot file into a dict of numpy columns."""
import numpy as np
def rd(p):
    L = open(p).read().splitlines(); i = [k for k, l in enumerate(L) if l.strip() == 'endheader'][0]
    h = L[i+1].split('\t'); d = np.array([[float(v) for v in l.split()] for l in L[i+2:] if l.strip()])
    return {n.strip(): d[:, k] for k, n in enumerate(h)}
