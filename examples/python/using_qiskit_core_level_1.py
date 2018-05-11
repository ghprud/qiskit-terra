# -*- coding: utf-8 -*-

# Copyright 2018 IBM RESEARCH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

"""
Example showing how to use QISKit at level 1 (intermediate).

In QISKit 0.6 we will be working on a pass manager for level 2+ users

Note: if you have only cloned the QISKit repository but not
used `pip install`, the examples only work from the root directory.
"""

import pprint

# Import the QISKit modules
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, QISKitError, QuantumJob
from qiskit.wrapper import available_backends, compile, register, get_backend

try:
    import Qconfig
    register(Qconfig.APItoken, Qconfig.config['url'])
except:
    print("""WARNING: There's no connection with the API for remote backends.
             Have you initialized a Qconfig.py file with your personal token?
             For now, there's only access to local simulator backends...""")


def lowest_pending_jobs():
    """Returns the backend with lowest pending jobs."""
    list_of_backends = available_backends(
        {'local': False, 'simulator': False})
    device_status = [get_backend(backend).status
                     for backend in list_of_backends]

    best = min([x for x in device_status if x['available'] is True],
               key=lambda x: x['pending_jobs'])
    return best['name']


try:
    # Create a Quantum and Classical Register and giving a name.
    qubit_reg = QuantumRegister(2, name='q')
    clbit_reg = ClassicalRegister(2, name='c')

    # Making first circuit: bell state
    qc1 = QuantumCircuit(qubit_reg, clbit_reg, name="bell")
    qc1.h(qubit_reg[0])
    qc1.cx(qubit_reg[0], qubit_reg[1])
    qc1.measure(qubit_reg, clbit_reg)

    # Making another circuit: superpositions
    qc2 = QuantumCircuit(qubit_reg, clbit_reg, name="superposition")
    qc2.h(qubit_reg)
    qc2.measure(qubit_reg, clbit_reg)

    # Setting up the backend
    print("(Local Backends)")
    for backend_name in available_backends({'local': True}):
        backend = get_backend(backend_name)
        print(backend.status)
    my_backend_name = 'local_qasm_simulator'
    my_backend = get_backend(my_backend_name)
    print("(Local QASM Simulator configuration) ")
    pprint.pprint(my_backend.configuration)
    print("(Local QASM Simulator calibration) ")
    pprint.pprint(my_backend.calibration)
    print("(Local QASM Simulator parameters) ")
    pprint.pprint(my_backend.parameters)


    # Compiling the job
    qobj = compile([qc1, qc2], my_backend)
    # I think we need to make a qobj into a class

    # Runing the job
    sim_result = my_backend.run(QuantumJob(qobj, preformatted=True))
    # ideally
    #   1. we need to make the run take as the input a qobj
    #   2. we need to make the run return a job object
    #
    # job = my_backend.run(qobj)
    # sim_result=job.retrieve
    # the job is a new object that runs when it does and i dont wait for it to
    # finish and can get results later
    # other job methods
    # job.cancel -- use to abort the job
    # job.status   -- the status of the job

    # Show the results
    print("simulation: ", sim_result)
    print(sim_result.get_counts(qc1))
    print(sim_result.get_counts(qc2))

    # Compile and run the Quantum Program on a real device backend
    # See a list of available remote backends
    try:
        print("\n(Remote Backends)")
        for backend_name in available_backends({'local': False}):
            backend = get_backend(backend_name)
            s = backend.status
            print(s)

        # select least busy available device and execute.
        best_device = lowest_pending_jobs()
        print("Running on current least busy device: ", best_device)

        my_backend = get_backend(best_device)

        print("(with Configuration) ")
        pprint.pprint(my_backend.configuration)
        print("(with calibration) ")
        pprint.pprint(my_backend.calibration)
        print("(with parameters) ")
        pprint.pprint(my_backend.parameters)

        # Compiling the job
        # I want to make it so the compile is only done once and the needing
        # a backend is optional
        qobj = compile([qc1, qc2], backend=my_backend, shots=1024, max_credits=10)
        # I think we need to make a qobj into a class

        # Runing the job
        q_job = QuantumJob(qobj, preformatted=True, resources={
            'max_credits': qobj['config']['max_credits']})

        exp_result = my_backend.run(q_job)
        # ideally
        #   1. we need to make the run take as the input a qobj
        #   2. we need to make the run return a job object
        #
        # job = my_backend.run(qobj, run_config)
        # sim_result=job.retrieve
        # the job is a new object that runs when it does and i dont wait for it
        # to finish and can get results later
        # other job methods
        # job.cancel -- use to abort the job
        # job.status   -- the status of the job

        # Show the results
        print("experiment: ", exp_result)
        print(exp_result.get_counts(qc1))
        print(exp_result.get_counts(qc2))
    except:
        print("All devices are currently unavailable.")

except QISKitError as ex:
    print('There was an error in the circuit!. Error = {}'.format(ex))