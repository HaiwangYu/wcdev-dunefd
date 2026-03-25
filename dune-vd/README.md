
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

single apa
```bash
lar -n 1 -c apa0.fcl -s g4_vd_ar39.root -o apa0.root >& apa0.log
lar -n 1 -c eventdump.fcl -s apa0.root | tee -a apa0.log
lar -n 1 -c apa1.fcl -s apa0.root -o apa1.root >& apa1.log
lar -n 1 -c eventdump.fcl -s apa1.root | tee -a apa1.log
```