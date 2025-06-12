#! /usr/bin/env python3

import sys, os
import numpy

sys.path.append('../scripts')

import bgeo
import sdbio

every = 1
stepmax = 9999999
rscale = 1
orbs = []
sdbout = None
outbase = 0
outstem = None
sdbstem = None
heartid = None

def Usage():
    print(f"""Usage: {sys.argv[0]}  [-e everyNth] [-orbs id0,id1,...] [-trackbh] [-o out.bgeo] [-bgeoobase outbasenum] nemofile""")
    sys.exit(1)

ii = 1
while ii<len(sys.argv) and sys.argv[ii][0] == '-' and len(sys.argv[ii]) > 1:
    opt = sys.argv[ii]; ii += 1
    if opt == '-e':
        every = int( sys.argv[ii] ); ii += 1
    elif opt == '-rscale':
        rscale = float( sys.argv[ii] ); ii += 1
    elif opt.startswith('-orb'):
        ss = sys.argv[ii].replace(',',' ').split(); ii += 1
        orbs.extend( [ int(s) for s in ss ] ) 
    elif opt == '-o':
        outstem = sys.argv[ii]; ii += 1
    elif opt == '-bgeobase':
        outbase = int( sys.argv[ii] ); ii += 1
    elif opt == '-sdbdump':
        sdbstem = sys.argv[ii]; ii += 1
    elif opt == '-stepmax':
        stepmax = int( sys.argv[ii] ); ii += 1
    elif opt == '-trackbh':
        heartid = -1        # Doing -trackbh this way assumes that the black hole is the LAST particle in the source.  If it were the first, we'd set heartid = 0
    elif opt == '-heart':
        heartid = int( sys.argv[ii] ); ii += 1
    else:
        print("Unknown option: ", opt)
        Usage()

if len(sys.argv) != ii+1:
    Usage()

nemoin = sys.argv[ii]

cmd = f"snapprint in='{nemoin}' options=x,y,z,i,m,etot header=t"

cmdf = os.popen(cmd, 'r')

rr = []
ptss = []
time = -1 # dummy

stepno = 0
while stepno <= stepmax:
    line = cmdf.readline()
    if line == '':
        break

    ss = line.split()
    if len(ss) != 2:
        raise ValueError("Expected <nbodies> <timeval> -- what's " + line)
    nbodies, time = int(ss[0]), float(ss[1])
    #print(f"# {nbodies=} {time=}", end="", flush=True)
    pts = numpy.empty( (nbodies, 3+3) )
    for i in range(nbodies):
        line = cmdf.readline()
        ss = line.split()
        pts[i] = [float(s) for s in ss]
    #print("")
    
    if heartid is not None:     # re-center to location of -heart <N>'th particle (e.g. -heart -1 if black hole is appended).  Otherwise assumes center is at (0,0,0).
        pts[:, 0:3] -= pts[heartid, 0:3]

    if every > 1:
        pts = pts[::every]
        onbodies = len(pts)
    else:
        onbodies = nbodies
    #print(f"# {onbodies=}")

    r = numpy.sqrt( numpy.sum( numpy.square(pts[:,0:3]), axis=1 ) )
    ptss.append( pts[:,0:6] )
    ixx = pts[:, 3]

    rr.append( r )

    stepno += 1

nsteps = stepno

print(f"# got {nsteps} timesteps ending at {time=:g}")

ptss = numpy.array( ptss )
rr = numpy.array( rr )

if True:
    nbodies = len(ptss)
    mass = ptss[0,:,4] * nbodies
    minmass = mass[mass>0].min()
    mass = numpy.where(mass>0, mass, minmass)   # replace any NaNs, 0, etc. with minimum positive mass
    lum = mass ** 2.5
    mag = -0.921 * numpy.log(lum)

if sdbstem is not None:
    sdbstem = sdbstem.replace('.sdb','')
    sdborbits = f"{sdbstem}.orbits.sdb"
    sdbw = sdbio.SDBWriter( sdborbits )
    timerange = numpy.arange( ptss.shape[0] )
    
    for seqno in orbs: ## range( ptss.shape[1] ):
        etot = ptss[:,seqno,5]
        sdbw.writepcles( ptss[:,seqno,0:3], num=seqno, radius=mass[seqno], mag=mag[seqno], opacity=timerange, dxyz=etot[:,None] )
    sdbw.close()

    speckf = open(f"{sdbstem}.speck", "w")
    for itime, pts in enumerate(ptss):
        sdbout = f"{sdbstem}.{itime:04d}.sdb"
        sdbw = sdbio.SDBWriter( sdbout )
        etot = pts[:, 5]
        sdbw.writepcles( pts[:, 0:3], num=numpy.arange(0, len(pts)), radius=mass, mag=mag, opacity=itime, dxyz=etot[:,None] )
        sdbw.close()

        print(f"sdb -t {itime} {sdbout}", file=speckf)


rrmins = []
rrmaxs = []

rae = {}

if outstem is None:
    for i in range(onbodies):
        rbodyi = rr[:, i]
        imins = 1 + numpy.argwhere( (rbodyi[:-2] > rbodyi[1:-1]) & (rbodyi[1:-1] < rbodyi[2:]) )[:,0]
        imaxs = 1 + numpy.argwhere( (rbodyi[:-2] < rbodyi[1:-1]) & (rbodyi[1:-1] > rbodyi[2:]) )[:,0]

        if len(imins) >= 2 and len(imaxs) >= 2:
            etotmax = ptss[:, i, 5].max()  # highest total-energy value for this particle's lifetime
            typrmin = rbodyi[imins].mean()
            typrmax = rbodyi[imaxs].mean()
            a = 0.5*(typrmax + typrmin)
            e = 0.5*(typrmax - typrmin) / a
            rae[i] = dict(isim=ixx[i], a=a, e=e, rmin=rbodyi.min(), rmax=rbodyi.max(), n=len(imins), etotmax=etotmax)

    print("# seq  isim     e             a         rmin     rmax        n etotmax")
    for i in sorted( rae.keys(), key=lambda i: rae[i]['e'], reverse=True ):
        rd = rae[i]
        print("%5d %5d %10.6f   %10g   %7.4f  %7.4f  %5d  %7.4f" % (i, rd['isim'], rd['e'], rd['a'], rd['rmin'], rd['rmax'], rd['n'], rd['etotmax']))

if outstem is not None:
    if outstem.endswith('/'):
        outstem += os.path.basename( os.path.dirname(outstem) )

    pointattrnames = [ "seqno", "special", "rmin", "rmax", "a", "ecc", "mass", "bigness", "etotmax" ]
    pointattrs = numpy.empty( (onbodies, len(pointattrnames)) )
    pointattrs[:,0] = numpy.arange(onbodies)  # attr0: point index in simulation
    pointattrs[:,1] = 0         # attr1: 0=ordinary point (not a special orbit)
    for seqno, orb in enumerate(orbs):
        pointattrs[ orb, 1 ] = seqno+1   #   >0 = special point (whose orbit is traced)
    rmin = rr.min( axis=0 )
    rmax = rr.max( axis=0 )
    a    = 0.5 * (rmax + rmin) # rough semimajor axis
    e    = 0.5 * (rmax - rmin) / a
    pointattrs[:,2] = rmin
    pointattrs[:,3] = rmax
    pointattrs[:,4] = a
    pointattrs[:,5] = e
    pointattrs[:,6] = mass                  # "mass"
    pointattrs[:,7] = (mass ** 0.5) * 0.005 # "bigness".   0.005 is a magic number, convenient for spacing of stars in "wool" cluster.
    pointattrs[:,8] = ptss[:,:,5].max(axis=0) # "etotmax"

    for stepno in range(nsteps):
        outfname = outstem + ".%04d.bgeo" % (stepno+outbase)

        _ = bgeo.BGeoPolyWriter( outfname, points=ptss[stepno,:,0:3], pointattrnames=pointattrnames, pointattrs=pointattrs )


    outfname = outstem + ".orbits.bgeo"

    #polys = [ ptss[:,i] for i in orbs ]
    polys = [ ptss[:,i,0:3] for i in orbs ]
    polyattrnames = pointattrnames
    polyattrs = pointattrs[orbs]

    pointattrnames = ["orbframe"]
    pointattrs = numpy.concatenate( [ outbase+numpy.arange(nsteps) for i in orbs ] ).reshape(-1,1)

    ## print(f"poly0: [{len(polys[0])}] dxs {[polys[0][1:,0]-polys[0][:-1,0]]}")
    # print("Writing %d curves, %d vertices to %s" % (len(polys), sum([len(pv) for pv in polys]), outfname))
    _ = bgeo.BGeoPolyWriter( outfname, polyattrnames=polyattrnames, polyattrs=polyattrs, as_curves=dict(degree=1,closed=False), polyverts=polys, pointattrnames=pointattrnames, pointattrs=pointattrs )
