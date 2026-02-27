
```bash
fhicl-dump detsim_dunevd10kt_1x8x6_3view_30deg_notpcsigproc.fcl >& tmp.fcl

lar -n 1 -c tmp.fcl -s g4_vd_ar39.root --no-output >& tmp.log
lar -n 1 -c detsim.fcl -s g4_vd_ar39.root --no-output >& tmp.log
```

```bash
lar -n 1 -c detsim.fcl -s g4_vd_radiols.root --no-output >& tmp.log
lar -n 1 -c tmp.fcl -s g4_vd_radiols.root --no-output >& tmp.log
```

```bash
wire-cell -l stdout -L debug -c wct-sim-fans.jsonnet -C Nbit=14 -C elecGain=14
```