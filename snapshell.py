#! /usr/bin/env python3

import sys, os
import numpy

ii = 1

rshells, drshells = [], []
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

        rshells.append(rshell)
        drshells.append(drshell)
    elif opt == '-t' or opt == '-times':
        times = f"times=" + sys.argv[ii]; ii += 1
    elif opt == '-orbs':
        outorbs = [ int(s) for s in sys.argv[ii].split(',') ]; ii += 1
        if len(outorbs) == 1:
            outorbs.append(0)
    elif opt == '-h':
        Usage()

snapfile = '-' if ii >= len(sys.argv) else sys.argv[ii]

with os.popen(f'set -x; snapprint {times} in={snapfile} options=i,r,v,etot', 'r') as snapf:
    pts = []
    for line in snapf.readlines():
        pts.append( [float(s) for s in line.split()] )

    pts = numpy.array(pts)


ppts = []

for i, (rshell, drshell) in enumerate( zip(rshells, drshells) ):
    wanted = (numpy.abs(pts[:,1] - rshell) < drshell) & (pts[:,3] < 0)
    ppts.append( pts[wanted, :] )

print("i    rshell    n    vmin     vmean      vmax     emin    emean    emax")
for i, (pts, rshell) in enumerate(zip(ppts, rshells)):
    r = pts[:,1]
    vel = pts[:,2]
    etot = pts[:,3]
    n = len(r)
    if n > 0:
        print(f"{i:2} {rshell:8.4g} {n:4} {vel.min():8.4g} {vel.mean():8.4g} {vel.max():8.4g}  {etot.min():8.4g} {etot.mean():8.4g} {etot.max():8.4g}")


if outorbs is not None:
    for i, pts in enumerate(ppts):
        n = len(pts)
        iord = numpy.argsort( pts[:,3] )  # ordered by etot total energy.
        # choose (n-1) tightly bound orbits (probably near circular) (from the bottom quarter centile), plus one most-loosely-bound orbit (

        orbis = []
        etots = []
        for ifrac in numpy.linspace(0.05*n, 0.25*n, num=outorbs[0], dtype=int):  # sample from the bottom quarter centile
            orbis.append( pts[ iord[ifrac], 0 ] )
            etots.append( pts[ iord[ifrac], 3 ] )
        for ifrac in numpy.linspace(n-1, 0.75*n, num=outorbs[1], dtype=int)[::-1]:  # sample from the top quarter centile.  If there's only sample, be sure the max (n-1) is included.
            orbis.append( pts[ iord[ifrac], 0] )
            etots.append( pts[ iord[ifrac], 3 ] )
        #print("-orbs", ",".join(["%d"%i for i in orbis]), "# etot", " ".join(["%g" % e for e in etots]))
        print("-orbs", ",".join(["%d"%i for i in orbis]))
        


