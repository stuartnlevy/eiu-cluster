#! /usr/bin/env python3

import sys, os
import numpy

import sdbio

as_type = 'sdb'
every = 1
rscale = 1

def Usage():
    print(f"""Usage: {sys.argv[0]} [-bgeo|-sdb] [-e everyNth]  nemofile  outstem""")
    sys.exit(1)

ii = 1
while ii<len(sys.argv) and sys.argv[ii][0] == '-':
    opt = sys.argv[ii]; ii += 1
    if opt == '-bgeo':
        as_type = 'bgeo'
    elif opt == '-sdb':
        as_type = 'sdb'
    elif opt == '-e':
        every = int( sys.argv[ii] ); ii += 1
    elif opt == '-rscale':
        rscale = float( sys.argv[ii] ); ii += 1
    else:
        print("Unknown option: ", opt)
        Usage()

if as_type == 'bgeo':
    sys.path.append('../gwave')
    import bgeo

if len(sys.argv) != ii+2:
    Usage()

nemoin = sys.argv[ii]
outstem = sys.argv[ii+1]

if '/' not in outstem:
    outstem += '/' + outstem

if not os.path.isdir( os.path.dirname(outstem) ):
    os.makedirs( os.path.dirname(outstem) )

cmd = f"snapprint in='{nemoin}' options=x,y,z,key,m,vx,vy,vz header=t"

cmdf = os.popen(cmd, 'r')

stepno = 0
while True:
    line = cmdf.readline()
    if line == '':
        break

    ss = line.split()
    if len(ss) != 2:
        raise ValueError("Expected <nbodies> <timeval> -- what's " + line)
    nbodies, time = int(ss[0]), float(ss[1])

    pts = numpy.empty( (nbodies, 3+1+4) )
    for i in range(nbodies):
        line = cmdf.readline()
        ss = line.split()
        pts[i] = [float(s) for s in ss]

    if every > 1:
        pts = pts[::every]
        onbodies = len(pts)
    else:
        onbodies = nbodies

    outname = outstem + (".%04d.%s" % (stepno, as_type))
    mass = pts[:,4] * nbodies
    minmass = mass[mass>0].min()
    mass = numpy.where(mass>0, mass, minmass)

    lum = mass ** 2.5
    mag = -0.921 * numpy.log(lum)

    if as_type == 'sdb':
        sd = sdbio.SDBWriter( outname )
        sd.writepcles( xyz=rscale*pts[:,0:3], num=pts[:,3], mag=mag, radius=mass, dxyz=pts[:,5:8], type=sd.ST_SPIKE )
        sd.close()

    elif as_type == 'bgeo':
        attrnames = ["mass", "lum", "mag"]

        attrs = numpy.stack( [ mass, lum, mag ], axis=1 )
        bg = bgeo.BGeoPolyWriter( outname, points=rscale*pts[:, 0:3], pointattrnames=attrnames, pointattrs=attrs, detailattrnames=["rscale","everyNth","mtotal"], detailattrs=[rscale, every, mass.sum()] )
        if stepno == 0:
            r = rscale*numpy.sqrt( numpy.sum( numpy.square( pts[:,0:3] ), axis=1 ) )
            print(f"wrote {len(pts)} points, rmax {r.max():g} rmean {r.mean():g} stddev {r.std():g} mass {mass.min():g} .. {mass.max():g} mean {mass.mean():g} to {outname}")

    if stepno % 10 == 0:
        print("%04d " % stepno, end="", flush=True)

    stepno += 1

print("")
