# hector_SA

change ```val n``` in ```hector_template/playground/dynamic/src/test.scala/TestSystolic```

```sh
python3 generate.py 8
hector-opt hec.mlir --dump-chisel > systolic_array.scala
```
move ```wrapper.scala``` and ```systolic_array.scala``` into ```hector_template/playground/dynamic/src/```

1. Generate Verilog
```sh
mill playground.dynamic.runMain Elaborate
```

2. Simulation
```sh
mill playground.dynamic.runMain Elaborate
```

3. Synthesis
First change MulFBase and AddSubFBase into MulFIP and AddSubFIP in ```hector_template/playground/dynamic/src/systolic.scala/PE```
Part configuration can be configured in ```hector_template/playground/src/TclGen.scala```
```sh
mill playground.dynamic.runMain ipGenerator
```
