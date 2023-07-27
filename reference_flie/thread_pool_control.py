from pyevsim import SystemSimulator, BehaviorModelExecutor
from pyevsim.definition import *
import zmq
import numpy as np
import cv2
from RxTxSignal import RxTxSignal
from concurrent import futures
import threading
import os
import time

'''
2023. 06. 07
control.py 구조를 확장한 control.

구조 변경 및 확장
1. single thread로 진행하던 데이터(메시지) 처리를 multi thread로 진행 하도록 확장(thread pool 사용)
2. 엔진의 모델이(output()) blocking 방식으로 receive 진행하도록 변경
3. 데이터를 recevie 했을 시, thread pool에 데이터 처리 요청하도록 변경
4. self.pool_size개의 thread가 데이터를 동시에 처리
5. threading.Lock을 이용해 여러 thread가 router 소켓에 동시 접근하는 것을 제한(zmq 권장 사항)
'''


# MsgRecv에서 전달 받은 값을 토대로 정보 전송
class MsgReceiver(BehaviorModelExecutor):
    STATE_EXECUTE = "Execute"       # 모델 상태: 실행
    STATE_TERMINATE = "Terminate"   # 모델 상태: 종료

    NUM_OF_REMOTE = 1               # 연결 될 remote의 수

    INPUT_PORT = "start"            # MsgReceiver의 input port name

    APPEND_MODE = "append"          # 데이터 처리 요청
    DELETE_MODE = "delete"          # 데이터 삭제 요청(데이터 처리 완료 후)


    def __init__(self, instance_time, destruct_time, name, engine_name, router: zmq.Socket):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        # 모델 상태 추가
        self.insert_state(MsgReceiver.STATE_EXECUTE, 1000)
        self.insert_state(MsgReceiver.STATE_TERMINATE)

        self.insert_input_port(MsgReceiver.INPUT_PORT)  # 모델 입력 포트 설정
        self.init_state(MsgReceiver.STATE_TERMINATE)    # 모델 초기 상태 설정

        self.router = router                            # zmq 통신을 위한 router 소켓 객체 생성    
        self.remote_manages = {}                        # 연결된 remote의 identity:state 값 저장
        self.image_num = 1                              # 여러 이미지의 이름을 달리하기 위한 데이터(임시)

        self.socket_lock = threading.Lock()             
        self.thread_pool_lock = threading.Lock()        # 

        self.pool_size = 3
        self.thread_pool = futures.ThreadPoolExecutor(max_workers=self.pool_size)
        self.thread_works = {
            RxTxSignal.CONNECTED    :   self.sendSpawn,
            RxTxSignal.READY        :   self.sendStart,
            RxTxSignal.IMAGE        :   self.saveImage
        }
        self.future_dict = {}


    def sendSpawn(self, remote_identity, msg):       # CONNECTED를 수신 받았을 때 호출
        if self.remote_manages.get(remote_identity) is None:
            self.remote_manages[remote_identity] = RxTxSignal.CONNECTED

        self.router.send_multipart([remote_identity, RxTxSignal.SPAWN])


    def sendStart(self, remote_identity, msg):       # READY를 수신 받았을 때 호출
        self.remote_manages[remote_identity] = RxTxSignal.READY

        if ((len(self.remote_manages) == MsgReceiver.NUM_OF_REMOTE) and 
            (RxTxSignal.CONNECTED not in self.remote_manages.values())
        ):
            for remote in self.remote_manages:
                self.router.send_multipart([remote, RxTxSignal.START])


    def saveImage(self, remote_identity, msg):       # IMAGE를 수신 받았을 때 호출
        pass


    def modifyFutureDict(self, mode, args: tuple):
        '''
        modify(dictionary, futures.Future)
        '''
        self.thread_pool_lock.acquire()
        try:
            if mode == MsgReceiver.APPEND_MODE:
                self.future_dict[args[0]] = args[1]

            elif mode == MsgReceiver.DELETE_MODE:
                del self.future_dict[args[0]]
                print("remaining ", end = "")

            print(f"future_dict: {self.future_dict}, count: {len(self.future_dict)}")
        
        except KeyError:
            print("keyError: 해당 future가 존재하지 않음")
            os._exit(0)

        except Exception as e:
            print(f"처리되지 않은 예외: {e}")
            os._exit(0)

        finally:
            self.thread_pool_lock.release()
            pass

    def ext_trans(self, port, msg):
        print("model execute...")
        self.init_state(MsgReceiver.STATE_EXECUTE)      # output() 호출을 위한 상태 천이


    def output(self):
        recv_data = self.router.recv_multipart()
        remote_identity = recv_data[0]
        datas = recv_data[1:]

        future = self.thread_pool.submit(self.thread_works[datas[0]], remote_identity, datas)
        self.modifyFutureDict(MsgReceiver.APPEND_MODE, (future, datas[0]))
        future.add_done_callback(lambda future: self.modifyFutureDict(MsgReceiver.DELETE_MODE, (future, )))

    
    def int_trans(self) -> None:
        self.init_state(MsgReceiver.STATE_EXECUTE)


if __name__ == "__main__":
    # zmq socket 생성
    context = zmq.Context()                                                     # zmq context 생성
    router = context.socket(zmq.ROUTER)                                         # router소켓 생성
    router.bind("tcp://127.0.0.1:5555")                                         # router 소켓 바인딩

    # engine/model 생성
    engine_name = "first"
    engine_input_port = "start"
    engine = SystemSimulator.register_engine(engine_name, "VIRTUAL_TIME", 1)    # 엔진 생성
    receiver_model = MsgReceiver(0, Infinite, "receiver", engine_name, router)  # 모델 생성

    # engine 설정
    engine.insert_input_port(engine_input_port)                                 # 엔진 입력 포트 추가
    engine.register_entity(receiver_model)                                      # 엔진에 모델 추가
    engine.coupling_relation(                                                   # 입력 포트 연결(엔진 -> 모델)
        None, engine_input_port, 
        receiver_model, MsgReceiver.INPUT_PORT
    )

    # engine 실행
    engine.insert_external_event(engine_input_port, None)                       # 엔진 입력 포트에 event 전달
    engine.simulate()                                                           # 엔진 실행
    