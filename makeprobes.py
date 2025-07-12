#! /usr/bin/env python3

import sys, os
import numpy

# tabtos in=table out=snap header=nbody,ndim,time block1=mass block2=pos block3=vel

infrom = sys.argv[1] if (len(sys.argv)>1 and sys.argv[1] != '-') else None
outto = sys.argv[2] if len(sys.argv)>2 else ("nursery.snp" if infrom is None else "creche.snp")

outname = outto

N = 10
time0 = 0
mass = 1e-7
bhmass = 1
outendtime = 100
outtimestep = 1.0/64
gyropts = "kmax=9 eps=0.001"
pos0 = numpy.array( [10,0,0] )
dpos = numpy.array( [0.3, 0.3, 0] )
vel0 = numpy.array( [-.2,.04,0] )

outstem = outname.replace('.snp','')
for trash in outname, f"{outstem}.full.snp":
    if os.path.exists(trash):
        os.unlink(trash)

gyropts = "kmax=9 eps=0.001" if infrom is None else "kmax=6 eps=0.005"

insert = "" if infrom is None else f" tee /tmp/blah.snp | gyrfalcON {gyropts} tstop=0.03125 startout=f lastout=t in=- out=- logfile=/dev/null | tee /tmp/blahgyr.snp | snapstack in1=- in2={infrom} out=- |"

tabtos = os.popen(f"tee /tmp/blah | tabtos in=- out=- header=nbody,ndim,time block1=mass,pos,vel | {insert}  gyrfalcON logfile={outstem}.glog in=- out=- {gyropts} step={outtimestep} tstop={outendtime} give=mxvap | tee {outstem}.full.snp | snapmask in=- select=1:{N} out={outname}; snapprint in={outname} options=x,y,z,i,t,etot,vx,vy,vz > {outstem}.speck", "w")

print(f"{N+1 if infrom is None else N} 3 {time0}", file=tabtos)


for i in range(N):
    frac = i / (N-1)
    pos = pos0 + frac*dpos
    vel = vel0.copy()
    vel[1] *= frac
    mymass = 2*mass if i==0 else mass
    print(f"{mymass:g} {pos[0]} {pos[1]} {pos[2]} {vel[0]} {vel[1]} {vel[2]}", file=tabtos)


if infrom is None:
    print(f"{bhmass:g} 0 0 0  0 0 0", file=tabtos)

tabtos.close()
print("Wrote to ", outname)
