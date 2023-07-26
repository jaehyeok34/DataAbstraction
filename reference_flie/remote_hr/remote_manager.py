from pyevsim import Infinite, SystemSimulator
from remote_receiver import RemoteReceiver
from process_handler import ProcessHandler
from ip import find_my_internal_ip

import csv
import random
import zmq

context = zmq.Context()
worker = context.socket(zmq.DEALER)
# worker.setsockopt_string(zmq.IDENTITY, find_my_internal_ip())
worker.setsockopt_string(zmq.IDENTITY, str(random.randint(0, 8000)))
worker.setsockopt(zmq.RCVTIMEO, 0)
worker.connect("tcp://localhost:5555")
# worker.connect("tcp://172.17.138.178:5555")

file_path = ".\\remote_hr\\process_info.csv"

process_list = []

with open(file_path, 'r') as csvfile :
    reader = csv.reader(csvfile)
    
    for line in reader :
        process_list.append(line)
    
    del process_list[0]

ss = SystemSimulator()
engine = ss.register_engine("engine", "VIRTUAL_TIME", 1)
engine.insert_input_port("connect")
engine.insert_input_port("start")
    
rr = RemoteReceiver(0, Infinite, 'remote_receiver' ,"engine", worker, process_list)
engine.register_entity(rr)
ph = ProcessHandler(0, Infinite, 'process_handler', "engine", process_list)
engine.register_entity(ph)


# pex = PEx(0, Infinite, 'pex', "engine")
# engine.register_entity(pex)

engine.coupling_relation(None, "connect", rr, "connect")
engine.coupling_relation(rr, "recv2hand", ph, "recv2hand")
engine.insert_external_event("connect", None)

# engine.coupling_relation(None, "start", pex, "start")
# engine.insert_external_event("start", None)

engine.simulate()
    






