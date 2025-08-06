#! /usr/bin/env python3

import sys, os
import numpy

r0, r1 = 0.04, 5.0
N = 20
dr = 0.18


ntightorbs = nlooseorbs = 0

ftnobh = "nemotoy/gold8-4_15k_6x.snp", "10.0"
ftwithbh = "nemotoy/bh8-4_15k_6x.snp", "10.0"

def Usage():
    print("""Usage: shelltest.py [-rr r0,r1] [-N nshells] [-bh|-nobh] [-orbs Ntightorbs,Nlooseorbs]""")
    sys.exit(1)

def printgrid(snpfile, r0, r1, N, orbs):

    if not os.path.exists(snpfile):
        raise ValueError("shelltest.py: Can't find file " + snpfile)

    ropts = " ".join([f"-r {rmid:g},{rmid*0.12:g}" for rmid in numpy.logspace( numpy.log10(r0), numpy.log10(r1), num=N )])
    sorbs = "" if orbs is None else f"-orbs {orbs}"
    with os.popen(f"set -x; ./snapshell.py -t {times} {ropts} {sorbs} {snpfile}", "r") as gridf:
        first = True
        for line in gridf.readlines():
            if first:
                first = False
                line = "#" + line
            print(line, end='')

ii = 1
snpname, times = ftnobh
orbs = None

while ii < len(sys.argv):
    opt = sys.argv[ii]; ii += 1
    if opt == '-bh' or opt == '-withbh':
        snpname, times = ftwithbh
    elif opt == '-nobh':
        snpname, times = ftnobh
    elif opt == '-times':
        times = sys.argv[ii]; ii += 1
    elif opt == '-orbs':
        orbs = sys.argv[ii]; ii += 1
    elif opt == '-N' or opt == '-nshells':
        N = int( sys.argv[ii] ); ii += 1
    elif opt == '-rr':
        r0, r1 = [ float(s) for s in sys.argv[ii].split(',') ]; ii += 1
        
    else:
        raise ValueError("Usage: shelltest.py [-bh|-nobh] [-orbs NORBSPERSHELL]")


print(f"{snpname=}")
printgrid(snpname, r0, r1, N, orbs)
