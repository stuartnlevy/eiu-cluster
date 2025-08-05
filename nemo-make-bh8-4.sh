rm -f nemotoy/bh8-4_15k_seed.snp nemotoy/bh8-4_15k_m.snp nemotoy/bh8-4_15k_3x.snp

snapcenter times=0 one=t in=nemotoy/gold8-4_15k_3x.snp out=nemotoy/bh8-4_justbh.snp ;# cumbersome way to create 1 particle with m=1 at origin.

snaptrim times=0 in=nemotoy/gold8-4_15k_3x.snp out=- | snapmass in=- massname='n(m)' massexpr='pow(m,p)' masspars=p,-1.5  norm=0.0001 out=nemotoy/bh8-4_15k_m.snp
snapadd in=nemotoy/bh8-4_15k_m.snp,nemotoy/bh8-4_justbh.snp zerocm=t out=- | addgravity in=- out=- | snapvirial mscale=f rscale=f vscale=t virial=1.0 in=- out=nemotoy/bh8-4_15k_seed.snp 

ls -l nemotoy/bh8-4_15k_seed.snp

# This starts at time 50, so we want to calculate out to 50+125 = 175
# Use tighter choice of kmax and eps where there's a black hole - close approaches are much more important here than for a cluster with a less huge range of masses
/usr/bin/time gyrfalcON in=nemotoy/bh8-4_15k_seed.snp step=0.020833333 tstop=42 out=- logfile=nemotoy/bh8-4.gyr kmax=9 eps=0.001 give=mxva | \
    addprop in=- out=- add=key value=i | \
    addgravity in=- out=nemotoy/bh8-4_15k_3x.snp

ls -l nemotoy/bh8-4_15k_3x.snp
