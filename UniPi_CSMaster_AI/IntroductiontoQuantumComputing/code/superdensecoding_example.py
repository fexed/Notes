#!/usr/bin/env python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
from qiskit.visualization import plot_bloch_multivector, plot_histogram


sim = Aer.get_backend('aer_simulator')

q = QuantumRegister(2, "qreg")
c = ClassicalRegister(2, "creg")
qc = QuantumCircuit(q, c)
qc.h(0)
qc.cx(0,1)
qc.x(0)
qc.z(0)
qc.cx(0,1)
qc.h(0)
qc.measure(q[0], c[0])
qc.measure(q[1], c[1])
qc.draw(output='mpl')

qc.save_statevector()
state = sim.run(qc).result().get_statevector()
print(state)
job = execute(qc, sim, shots=1024)
counts = job.result().get_counts(qc)
print(counts)
