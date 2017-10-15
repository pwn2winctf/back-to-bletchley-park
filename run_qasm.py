import sys
from qiskit import QuantumProgram
qp = QuantumProgram()
name = qp.load_qasm_file(sys.argv[1])
result = qp.execute(name, shots=1)
print(result.get_counts(name))
