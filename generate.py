import sys
N = int(sys.argv[1])
def PE_def(i, j):
    return "%PE_{}_{}".format(str(i), str(j))
IR = """module {
  hec.design @systolic_array {
    hec.component @PE(%A_in: f32, %C_in: f32) -> (%A_out: f32, %C_out: f32) {interface="wrapped", style="dummy"} {}
"""
IR += "    hec.component @main("
for i in range(N):
    IR += "%A" + str(i) + ": f32, "
for i in range(N):
    IR += "%C_in" + str(i) + ": f32, "
IR = IR[:-2] + ") -> ("
for i in range(N):
    IR += "%C_out" + str(i) + ": f32, "
IR = IR[:-2] + ") {interface=\"wrapped\", style=\"handshake\"} {\n"
for i in range(N):
    for j in range(N):
        PE = PE_def(i, j)
        IR += "      {}.A_in, {}.C_in, {}.A_out, {}.C_out = hec.instance \"{}\" @PE: f32, f32, f32, f32\n".format(PE, PE, PE, PE, PE[1:])
IR += "      hec.graph {\n"
for i in range(N):
    for j in range(N):
        PE = PE_def(i, j)
        IR += "        hec.assign {} = {} : f32 -> f32\n".format(PE + ".A_in", PE_def(i, j-1) + ".A_out" if j>0 else "%A" + str(i))
        IR += "        hec.assign {} = {} : f32 -> f32\n".format(PE + ".C_in", PE_def(i-1, j) + ".C_out" if i>0 else "%C_in" + str(j))
for j in range(N):
    PE = PE_def(N-1, j)
    IR += "        hec.assign {} = {} : f32 -> f32\n".format("%C_out" + str(j), PE + ".C_out")
IR += "      }\n    }\n  }\n}\n"
hec_ir = open("hec.mlir", "w")
hec_ir.write(IR)

TEST = """import chisel3._
import chisel3.util._
import chisel3.tester._
import chisel3.experimental.BundleLiterals
import utest._
import chisel3.experimental._
import hls._

class Wrapper extends MultiIOModule with dynamicDelay {\n"""
TEST +="  val n = {}\n".format(N)
TEST += """  val A = IO(Flipped(Vec(n, DecoupledIO(UInt(32.W)))))
  val C_in = IO(Flipped(Vec(n, DecoupledIO(UInt(32.W)))))
  val C_out = IO(Vec(n, DecoupledIO(UInt(32.W))))

  val main = Module(new systolic_array)
  main.finish := true.B
"""

for i in range(N):
    TEST += "  connection(A({}), main.var{})\n".format(i, i)

for i in range(N):
    TEST += "  connection(C_in({}), main.var{})\n".format(i, N+i)

for i in range(N):
    TEST += "  connection_inverse(C_out({}), main.var{})\n".format(i, 2*N+i)
TEST += "}\n"
scala = open("wrapper.scala", "w")
scala.write(TEST)
