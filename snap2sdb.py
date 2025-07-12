#! /usr/bin/env python3

import sys, os
import numpy
import time

sys.path.append('../scripts')

import sdbio

as_type = 'sdb'
every = 1
rscale = 1
heart = None

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
    elif opt == '-trackbh':
        heart = -1
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

class NemoSnapReader:

    def __init__(self, snapfile, tempdir='/dev/shm'):
        self.snapfile = snapfile
        self.timelist = None
        self.tempdir = tempdir

    def times(self):
        if self.timelist is None:
            self.timelist = []
            with os.popen(f"snapmask in={nemoin} select=1 out=- | snapprint in=- header=t", "r") as indexf:
                while True:
                    ss = indexf.readline().split() # nstars timestep
                    if len(ss) != 2:
                        break
                    self.timelist.append( float(ss[1]) )
                    indexf.readline() # ignore the single star data selected by select=1
            self.timelist = numpy.array( self.timelist )
        return self.timelist

    fieldnames = "x,y,z,key,m,vx,vy,vz"

    def readtime(self, t, dtype=float):
        nfields = len( self.fieldnames.split(',') )
        with os.popen(f"snapprint in={nemoin} times={t} header=f options={self.fieldnames} 2>/dev/null") as brickf:
            brick = numpy.loadtxt(brickf).reshape( -1, nfields )
        return brick


nemor = NemoSnapReader( nemoin )
t0 = time.time()
times = nemor.times()
t1 = time.time()
print(f"# Found {len(times)} times in {(t1-t0)*1000:.0f} ms")

tprev = t1
for stepno, ttime in enumerate(times):

    pts = nemor.readtime(ttime)

    if heart is not None:
        pts[:, 0:3] -= pts[heart, 0:3]

    if every > 1:
        pts = pts[::every]

    nbodies = len(pts)

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
        bg = bgeo.BGeoPolyWriter( outname, points=rscale*pts[:, 0:3], pointattrnames=attrnames, pointattrs=attrs, detailattrnames=["rscale","everyNth","mtotal","time"], detailattrs=[rscale, every, mass.sum(), ttime] )
        if stepno == 0:
            r = rscale*numpy.sqrt( numpy.sum( numpy.square( pts[:,0:3] ), axis=1 ) )
            print(f"wrote {len(pts)} points, rmax {r.max():g} rmean {r.mean():g} stddev {r.std():g} mass {mass.min():g} .. {mass.max():g} mean {mass.mean():g} to {outname}")

    if stepno % 10 == 0:
        t2 = time.time()
        print("%04d " % (stepno), end="", flush=True)
        ##print("%04d(%dms) " % (stepno, (t2-t1)*1000/10), end="", flush=True)
        t1 = t2

    stepno += 1

print("")
