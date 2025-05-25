mkdir -p nemotoy

rm -f nemotoy/cotton.snp nemotoy/wool.snp

mkplummer out=nemotoy/cotton.snp seed=1745450495 nbody=30000 massname='n(m)' massexpr='pow(m,p)' masspars=p,-1.5 massrange=.01,1
/usr/bin/time gyrfalcON in=nemotoy/cotton.snp step=0.0625 tstop=30 out=- logfile=nemotoy/glog kmax=6 eps=0.1 give=mxva | addprop in=- out=- add=key value=i | addgravity in=- out=nemotoy/wool.snp

