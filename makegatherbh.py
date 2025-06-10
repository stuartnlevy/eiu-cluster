#! /usr/bin/env python3

import sys, os
import glob

BHramp = "nemotoy/grow"
BHgathered = "nemotoy/grow/bhall.snp"


os.system(f"rm -f {BHgathered}")

first = True

for piece in sorted( glob.glob(f"{BHramp}/BHramp.????.snp") ):
    if first:
        os.system(f"cp {piece} {BHgathered}")
        first = False
    else:
        os.system(f"set -x; snapmerge_a_dp in1={BHgathered} in2={piece}")
