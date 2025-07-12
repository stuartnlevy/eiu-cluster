#! /usr/bin/env python3

import sys, os
import numpy

Ngrowsteps=48
FullBHMass=1.5
stepdt = 0.0625
growdt = 0.25   # should be a whole multiple of stepdt
#runmoretime = 42
runmoretime = 4

BHramp = "nemotoy/grow"
BHfmt = f"{BHramp}/BHramp.%04d.snp"

seedinput = [ "nemotoy/wool+ext-end.snp", "nemotoy/justbh.snp" ]
####

if not os.path.isdir(BHramp):
    os.makedirs(BHramp)
os.system(f"rm -f {BHramp}/*.snp")

nstars = seedtime = None
with os.popen(f"tsf {seedinput[0]}", "r") as tsff:
    for line in tsff.readlines():
        if 'int Nobj' in line:
            nstars = int( line.split()[2] )
            if seedtime is not None:
                break
        if 'double Time' in line:
            seedtime = float( line.split()[2] )
            if nstars is not None:
                break

if nstars is None or seedtime is None:
    raise ValueError(f"Couldn't detect number of stars and timestep in {seedinput[0]} with tsf ...")

seed = f"{BHramp}/BHramp.sd.snp"
os.system(f"snapcenter in={seedinput[0]} times={seedtime} out=- | snapstack zerocm=f in1=- in2={seedinput[1]} out=- | snapmass in=- mass='(i=={nstars}) ? 0 : m' out={seed}")
 
prev = seed
prevtime = seedtime
for rampstep in range(Ngrowsteps):
    outname = BHfmt % rampstep
    seedtime = seedtime + growdt
    massnow = FullBHMass*(rampstep/Ngrowsteps)**2  # ramp up more gradually to final BH mass
    normmass = 1
    print(f"# {massnow=:g} {normmass=:g}")
    ##os.system(f"snapcenter in={prev} weight='i=={nstars}?1:0' out=- | snapmass in=- mass='(i=={nstars})? {massnow} : m' norm={massnow+1} out=- | gyrfalcON in=- startout=f step={growdt} tstop={seedtime} logfile={BHramp}/glog{rampstep:04d} kmax=6 eps=0.01 give=mxvap out={outname}")
    ##ok = os.system(f"snapcenter in={prev} times={prevtime} weight='(i<{nstars})' out=- | snapmask in=- select=0:{nstars-1} out=- | snapstack zerocm=f in1=- in2={seedinput[1]} out=- | snapmass in=- mass='(i=={nstars})? {massnow} : m' norm={normmass} out=- | gyrfalcON in=- startout=f step={stepdt} tstop={seedtime} logfile={BHramp}/glog{rampstep:04d} kmax=6 eps=0.01 give=mxvap out={outname}")
    # remove and re-add the BH at each timestep, so that it stays near the origin in r and v.
    ok = os.system(f"snapmask in={prev} times={prevtime} select=0:{nstars-1} out=- | snapstack zerocm=f in1=- in2={seedinput[1]} out=- | snapmass in=- mass='(i=={nstars})? {massnow} : m' norm={normmass} out=- | gyrfalcON in=- startout=f step={stepdt} tstop={seedtime} logfile={BHramp}/glog{rampstep:04d} kmax=6 eps=0.01 give=mxvap out={outname}")
    if ok != 0:
        print("# Exiting early at step", rampstep, "of", Ngrowsteps)
        sys.exit(1)

    prev = outname
    prevtime = seedtime


outname = f"{BHramp}/BHramp.more.snp"
os.system(f"snapcenter in={prev} times={prevtime} weight='(i=={nstars})?2*m:m' out=- |gyrfalcON in=- startout=f step={stepdt} tstop={prevtime+runmoretime} logfile={BHramp}/glogmore kmax=6 eps=0.01 give=mxvap out={outname}")
