from pyevsim import SystemSimulator, BehaviorModelExecutor, SysMessage
from pyevsim.definition import *
import zmq
import random
import time
import threading

# remote에서 값 전달 받음
class MsgRecv (BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name, router: zmq.Socket):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)

        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Receive", 1)
                      
        self.insert_input_port("recv_start")
        self.insert_output_port("recv_result")

        self.router = router

        self.recv_thread = None
        self.recv_data = []
        self.dealers = []

    def recvData(self):
        while True:
            print("recieve...")
            self.recv_data.append(self.router.recv_multipart())
            print(f"{self.recv_data}")

    def ext_trans(self, port, msg):
        print(f"Recv: ext_trans({port}, {msg})")
        self.init_state("Receive")
        

    def output(self):
        self._cur_state = "Wait" 
        if self.recv_thread is None:
            print("create worker thread...")
            self.recv_thread = threading.Thread(target=self.recvData)
            self.recv_thread.start()

        # print("output function is running...")
        if self.recv_data:
            for recv_data in self.recv_data:
                dealer_identity = recv_data[0]
                datas = recv_data[1:]

                if dealer_identity not in self.dealers:
                    self.dealers.append(dealer_identity)

                for dealer in self.dealers:
                    self.router.send_multipart([dealer, *datas])
            
                self.recv_data.pop()

    def int_trans(self):
        self._cur_state = "Receive"
        pass


if __name__ == "__main__":
    ss = SystemSimulator()

    context = zmq.Context()
    router = context.socket(zmq.ROUTER)
    router.bind("tcp://127.0.0.1:5454")

    ss.register_engine("first", "VIRTUAL_TIME", 1)
    ss.get_engine("first").insert_input_port("recv_start")

    proc = MsgRecv(0, Infinite, "Proc", "first", router)
    ss.get_engine("first").register_entity(proc)

    ss.get_engine("first").coupling_relation(None, "recv_start", proc, "recv_start")
    ss.get_engine("first").insert_external_event("recv_start", None)
    ss.get_engine("first").simulate()



    