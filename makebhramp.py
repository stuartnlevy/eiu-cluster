#! /usr/bin/env python3

import sys, os
import numpy

Ngrowsteps=48
FullBHMass=1.0
growdt = 0.0625
runmoretime = 5

BHramp = "nemotoy/grow"
BHfmt = f"{BHramp}/BHramp.%04d.snp"

seedinput = [ "nemotoy/woolext001.snp", "nemotoy/justbh.snp" ]
####

if not os.path.isdir(BHramp):
    os.makedirs(BHramp)
os.system(f"rm -f {BHramp}/*.snp")

nstars = seedtime = None
with os.popen(f"tsf {seedinput[0]}", "r") as tsff:
    for line in tsff.readlines():
        if 'int Nobj' in line:
            nstars = int( line.split()[2] )
        if 'double Time' in line:
            seedtime = float( line.split()[2] )
            break

if nstars is None or seedtime is None:
    raise ValueError(f"Couldn't detect number of stars and timestep in {seedinput[0]} with tsf ...")

seed = f"{BHramp}/BHramp.sd.snp"
os.system(f"snapstack zerocm=t in1={seedinput[0]} in2={seedinput[1]} out=- | snapmass in=- mass='(i=={nstars}) ? 0 : m' out={seed}")
 
prev = seed
prevtime = seedtime
for rampstep in range(Ngrowsteps):
    outname = BHfmt % rampstep
    seedtime = seedtime + growdt
    os.system(f"snapmass in={prev} mass='(i=={nstars})? {rampstep*FullBHMass/Ngrowsteps} : m' out=- | gyrfalcON in=- startout=f step={growdt} tstop={seedtime} logfile={BHramp}/glog{rampstep:04d} kmax=6 eps=0.1 give=mxvap out={outname}")

    prev = outname
    prevtime = seedtime


outname = f"{BHramp}/BHramp.more.snp"
os.system(f"gyrfalcON in={prev} startout=f step={growdt} tstop={prevtime+runmoretime} logfile={BHramp}/glogmore kmax=6 eps=0.1 give=mxvap out={outname}")
