#! /usr/bin/env python3

import sys, os
import numpy

ii = 1

rshell, drshell = None, None
times = ''
outorbs = None

def Usage():
    print(f"""Usage: {sys.argv[0]} [-r r0-r1 or -r rmid,dr] [-t times] [-orbs orb1,orb2,...] infile.snp""", file=sys.stderr)
    sys.exit(1)

while ii < len(sys.argv) and sys.argv[ii][0] == '-' and len(sys.argv[ii])>1:
    opt = sys.argv[ii]; ii += 1
    if opt == '-r' or opt == '-rshell':
        arg = sys.argv[ii]; ii += 1
        if '-' in arg:
            ss = arg.split('-')
            r0, r1 = float(ss[0]), float(ss[1])
            rshell, drshell = 0.5*(r1+r0), 0.5*(r1-r0)
        elif ',' in arg:
            ss = arg.split(',')
            rshell, drshell = float(ss[0]), float(ss[1]) 
    elif opt == '-t' or opt == '-times':
        times = f"times=" + sys.argv[ii]; ii += 1
    elif opt == '-orbs':
        outorbs = int( sys.argv[ii] ); ii += 1
    elif opt == '-h':
        Usage()

snapfile = '-' if ii >= len(sys.argv) else sys.argv[ii]

with os.popen(f'set -x; snapprint {times} in={snapfile} options=i,r,v,etot', 'r') as snapf:
    pts = []
    for line in snapf.readlines():
        pts.append( [float(s) for s in line.split()] )

    pts = numpy.array(pts)

wanted = (numpy.abs(pts[:,1] - rshell) < drshell) & (pts[:,3] < 0)

n = numpy.count_nonzero(wanted)

if n == 0:
    raise ValueError(f"No stars (of {len(pts)}) have r within +/- {drshell} of radius {rshell}")

print(f"{n} stars of {len(pts)} with r within {drshell} of radius {rshell} and with etot<0")
r = pts[wanted, 1]
print(f"r    {r.min():9.5g} .. {r.max():9.5g} mean {r.mean():9.5g} std {r.std():9.5g}")
vel = pts[wanted, 2]
print(f"vel  {vel.min():9.5g} .. {vel.max():9.5g} mean {vel.mean():9.5g} std {vel.std():9.5g}")
etot = pts[wanted, 3]
print(f"etot {etot.min():9.5g} .. {etot.max():9.5g} mean {etot.mean():9.5g} std {etot.std():9.5g}")

if outorbs is not None:
    everynth = max( 1, int( n / outorbs ) )
    ii = pts[wanted, 0][::everynth]
    print("-orbs", ",".join(["%d"%i for i in ii]))


