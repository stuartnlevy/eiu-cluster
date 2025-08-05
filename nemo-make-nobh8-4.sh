rm -f nemotoy/gold.snp nemotoy/gold8-4_15k_3x.snp
mkplummer seed=1745450495 out=nemotoy/gold15k.snp nbody=15000 mfrac=0.995 massname='n(m)' massexpr='pow(m,p)' masspars=p,-1.5 massrange=.1,1
/usr/bin/time gyrfalcON in=nemotoy/gold15k.snp step=0.0208333333 tstop=42 out=- logfile=nemotoy/glog3x kmax=6 eps=0.1 give=mxva | \
    addprop in=- out=- add=key value=i | \
    addgravity in=- out=nemotoy/gold8-4_15k_3x.snp

ls -l nemotoy/gold8-4_15k_3x.snp
