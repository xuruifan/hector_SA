import sys
N = int(sys.argv[1])
def PE_def(i, j):
    return "%PE_{}_{}".format(i, j)
IR = """module {
  hec.design @systolic_array {
    hec.component @PE(%A_in: f32, %C_in: f32) -> (%A_out: f32, %C_out: f32) {interface="wrapped", style="dummy"} {}
"""
IR += "    hec.component @PE_line(%A: f32, "
for i in range(N):
    IR += "%C_in{}: f32, ".format(i)
IR = IR[:-2] + ") -> ("
for i in range(N):
    IR += "%C_out{}: f32, ".format(i)
IR = IR[:-2] + ") {interface=\"wrapped\", style=\"handshake\"} {\n"
for i in range(N):
    PE = "%PE_{}".format(i)
    IR += "      {}.A_in, {}.C_in, {}.A_out, {}.C_out = hec.instance \"{}\" @PE: f32, f32, f32, f32\n".format(PE, PE, PE, PE, PE[1:])
IR += "      hec.graph {\n"
for i in range(N):
    IR += "        hec.assign {} = {} : f32 -> f32\n".format("%PE_{}.A_in".format(i), "%PE_{}.A_out".format(i-1) if i>0 else "%A")
    IR += "        hec.assign {} = {} : f32 -> f32\n".format("%PE_{}.C_in".format(i), "%C_in{}".format(i))
    IR += "        hec.assign {} = {} : f32 -> f32\n".format("%C_out{}".format(i), "%PE_{}.C_out".format(i))
IR += "      }\n    }\n"

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
    PE_line = "%Line_{}".format(i)
    args = ["A"]
    for j in range(N):
        args.append("C_in{}".format(j))
    for j in range(N):
        args.append("C_out{}".format(j))
    ports = ""
    for arg in args:
        ports += PE_line + "." + arg + ", "
    IR += "      {} = hec.instance \"{}\" @PE_line : {}\n".format(ports[:-2], PE_line[1:], ("f32, "*len(args))[:-2])
IR += "      hec.graph {\n"
for i in range(N):
    IR += "        hec.assign {} = {} : f32 -> f32\n".format("%Line_{}.A".format(i), "%A{}".format(i))
for i in range(N):
    PE_line = "%Line_{}".format(i)
    last_line = "%Line_{}".format(i-1)
    for j in range(N):
        IR += "        hec.assign {} = {} : f32 -> f32\n".format(PE_line + ".C_in{}".format(j),  last_line + ".C_out{}".format(j) if i>0 else "%C_in" + str(j))
for j in range(N):
    Line = "%Line_{}".format(N-1)
    IR += "        hec.assign {} = {} : f32 -> f32\n".format("%C_out" + str(j), Line + ".C_out{}".format(j))
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
    TEST += "  connection(A({}), main.var{})\n".format(i, i+2*N+1)

for i in range(N):
    TEST += "  connection(C_in({}), main.var{})\n".format(i, N+i+2*N+1)

for i in range(N):
    TEST += "  connection_inverse(C_out({}), main.var{})\n".format(i, 2*N+i+2*N+1)
TEST += "}\n"
scala = open("wrapper.scala", "w")
scala.write(TEST)
