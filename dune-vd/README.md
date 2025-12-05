
```bash
fhicl-dump detsim_dunevd10kt_1x8x6_3view_30deg_notpcsigproc.fcl >& tmp.fcl

lar -n 1 -c tmp.fcl -s g4_vd_ar39.root --no-output >& tmp.log
lar -n 1 -c detsim.fcl -s g4_vd_ar39.root --no-output >& tmp.log
```