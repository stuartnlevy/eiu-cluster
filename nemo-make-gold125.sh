rm -f nemotoy/gold.snp nemotoy/gold125.snp
mkplummer seed=1745450495 out=nemotoy/gold.snp nbody=30000 massname='n(m)' massexpr='pow(m,p)' masspars=p,-1.5 massrange=.01,1
/usr/bin/time gyrfalcON in=nemotoy/gold.snp step=0.0625 tstop=125 out=- logfile=nemotoy/glog125 kmax=6 eps=0.1 give=mxva | \
    addprop in=- out=- add=key value=i | \
    addgravity in=- out=nemotoy/gold125.snp

ls -l nemotoy/gold125.snp
