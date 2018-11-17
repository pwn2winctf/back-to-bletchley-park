import sys
import qiskit as qi
import matplotlib.pyplot as plt
from qiskit.tools.visualization import circuit_drawer
from qiskit import Aer
import time

#from qiskit import QuantumProgram
#qp = QuantumProgram()

prog =  qi.load_qasm_file(sys.argv[1])
#circuit_drawer(prog).show()

backend = Aer.get_backend('qasm_simulator')

# Job is async
job = qi.execute(prog, backend, shots=1)

#The block below is not necessary
#It is just way to make sure things are still running
init_status = job.status()
i=0
while True:
    time.sleep(10)
    print(job.status(), i)
    i=i+1
    if init_status != job.status():
        break


#This call blocks waiting for the job completion
#But it will always have completed (or crashed)
result = job.result()

print(result.get_counts(prog))
