from pyevsim import SystemSimulator, BehaviorModelExecutor, SysMessage
from pyevsim.definition import *
import zmq
import random
import time

# MsgRecv에서 전달 받은 값을 토대로 정보 전송
class MsgSend(BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name, router: zmq.Socket):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Generate", 10000)

        self.insert_input_port("start")
        self.insert_input_port("recv")

        self.router = router
        self.remote_manages = [] # START보내기 위해 remote 확인 값

    def ext_trans(self,port, msg):
        ret = msg.retrieve() 
        dealer_identity = None
        data = None

        if ret[0] is not None:
            dealer_identity = ret[0][0]
            data = ret[0][1:]

        if dealer_identity not in dealers:
            dealers.append(dealer_identity)

        print(f"Send: ext_trans({port}, {data})")
        self._cur_state = "Generate"
        

    def output(self):
        message = ["hi".encode(), "hello".encode(), "good".encode()]
        for dealer in dealers:
            if dealer is not None:
                self.router.send_multipart([dealer, random.choice(message)])
        
        time.sleep(3)


    def int_trans(self):
        pass


# remote에서 값 전달 받음
class MsgRecv (BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name, router: zmq.Socket):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)

        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Receive", 100)
                      
        self.insert_input_port("recv_start")
        self.insert_output_port("recv_result")

        self.router = router


    # recv 모델은 항상 내부천이 하면서 zmq로 데이터 받아오기
    # output의 msg에 zmq로 받아온 데이터를 send 모델에게 넘겨주기
    # int_trans는 굳이 뭐 넣을 필요 없음
    def ext_trans(self,port, msg):
        print(f"Recv: ext_trans({port}, {msg})")
        self._cur_state = "Receive"
        

    def output(self):
        self._cur_state = "Wait"
        try:
            recv_data = self.router.recv_multipart(flags=zmq.NOBLOCK)

            msg = SysMessage(self.get_name(), "recv_result")
            msg.insert(recv_data)

            return msg
        
        except zmq.Again as e:
            pass



    def int_trans(self):
        self._cur_state = "Receive"


if __name__ == "__main__":
    dealers = []

    ss = SystemSimulator()

    context = zmq.Context()
    router = context.socket(zmq.ROUTER)
    router.setsockopt(zmq.RCVTIMEO, 0)
    router.bind("tcp://127.0.0.1:5454")


    ss.register_engine("first", "VIRTUAL_TIME", 1)
    ss.get_engine("first").insert_input_port("start")
    ss.get_engine("first").insert_input_port("recv_start")


    gen = MsgSend(0, Infinite, "Gen", "first", router)
    ss.get_engine("first").register_entity(gen)

    proc = MsgRecv(0, Infinite, "Proc", "first", router)
    ss.get_engine("first").register_entity(proc)

    ss.get_engine("first").coupling_relation(None, "start", gen, "start")
    ss.get_engine("first").coupling_relation(None, "recv_start", proc, "recv_start")
    ss.get_engine("first").coupling_relation(proc, "recv_result", gen, "recv")

    ss.get_engine("first").insert_external_event("start", None)
    ss.get_engine("first").insert_external_event("recv_start", None)
    ss.get_engine("first").simulate()



    
