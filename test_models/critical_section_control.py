from pyevsim import SystemSimulator, BehaviorModelExecutor, SysMessage
from pyevsim.definition import *
import zmq
import datetime
import threading
import numpy as np
import cv2

# MsgRecv에서 전달 받은 값을 토대로 정보 전송
class MsgSend(BehaviorModelExecutor):
    STATE_WAIT = "Wait"             # 모델 상태(대기)
    STATE_GENERATE = "Generate"     # 모델 상태(실행)

    NUM_OF_REMOTE = 2               # 연결 될 remote의 수
    
    MODE_WRITE  =   0               # 임계 구역에서 수신 list에 값을 쓸 때를 의미
    MODE_READ   =   1               # 임계 구역에서 수신 list에 값을 읽을 때를 의미

    def __init__(self, instance_time, destruct_time, name, engine_name, router: zmq.Socket):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        # 모델 상태 추가
        self.insert_state(MsgSend.STATE_WAIT, Infinite)
        self.insert_state(MsgSend.STATE_GENERATE, 1)

        self.insert_input_port("start")         # 모델의 입력 포트 설정
        self.init_state(MsgSend.STATE_WAIT)     # 모델의 처음 상태 설정

        self.router = router                    # zmq 통신을 위한 router 소켓 객체 생성    
        self.remote_manages = {}                # 연결된 remote의 identity:state 값 저장
        self.recv_datas = []                    # remote로 부터 받은 값들 저장
        self.image_num = 1                      # 여러 이미지의 이름을 달리하기 위한 데이터(임시)
        self.lock = threading.Lock()            # 임계 구역 진입을 위한 Lock 객체

        # 수신 전용 thread 객체 생성 및 실행(수신 비동기화)
        self.recv_thread = threading.Thread(target=self.recvData)
        self.recv_thread.start()

    def ext_trans(self, port, msg):
        print("---- program started ----")
        self.init_state(MsgSend.STATE_GENERATE) # output callback을 위한 상태 천이


    def output(self):
        '''
            • 송신 루틴 진행
        '''
        self.init_state(MsgSend.STATE_WAIT)     # 모델의 상태를 Wait으로 변경

        # 송신 루틴
        if self.recv_datas:     # 수신 받은 data가 존재할 경우
            print("---- receive data ----")
            recv_data_list = self.criticalSection(mode = MsgSend.MODE_READ)
            
            # 비동기로 수신해 오기 때문에, 송신 루틴을 처리하는 과정에서도
            # 지속적으로 수신 데이터가 쌓이므로 list의 형태로 관리
            for recv_data in recv_data_list:
                remote_identity = recv_data[0]  # 수신 받은 데이터의 첫번째 값은 항상 identity 값
                datas = recv_data[1:]           # multipart 형식으로 받아오기 때문에 하나 이상의 값임

                print(f'from: {remote_identity}, data: {datas}')

                # 수신 종류
                # CONNECTED: SPAWN 전송 및 remote_manages에 identity:state 저장
                # READY: 해당 remote에 상태값을 READY로 변경 후 모든 remote가 연결 및 READY 상태임을 확인
                #        모두 READY상태일 경우, START 전송
                # else: 이미지 수신 관련
                if b"CONNECTED" in datas:
                    self.router.send_multipart([remote_identity, "SPAWN".encode()])
                    self.remote_manages[remote_identity] = "CONNECTED"

                elif b"READY" in datas:
                    self.remote_manages[remote_identity] = "READY"

                    # n개의 remote가 모두 연결됐고, 모두 Ready 상태일 경우.
                    # 상태에는 CONNECTED와 READY가 존재하는데, 
                    # CONNECTED가 values 값에 없다는 뜻은 모두 READY 상태임을 의미
                    if ((len(self.remote_manages) == MsgSend.NUM_OF_REMOTE) and 
                        ("CONNECTED" not in self.remote_manages.values())
                    ):
                        # 모든 remote에게 START 전달
                        for remote in self.remote_manages:
                            self.router.send_multipart([remote, "START".encode()])

                # 무엇을 의미하는 지 몰라서 일단은 PASS 시킴
                # TODO: TERMINATED 상태에 대한 처리 필요
                elif b"TERMINATED" in datas:
                    print("end...")
                    pass

                # TODO: Image 수신 루틴
                # remote에서 이미지를 전송할 때, 반드시 "send" 문자열과 image를 같은 배열로 전달해야 함
                # 즉, [b"상태값", b"image encode string..."]의 형태가 되도록
                else:           
                    # datas의 0번째 index에 "상태값"이 들어가 있으므로 이를 제외한 나머지 부분이 실제 image 코드
                    for data in datas[1:]:
                        save_path = f"C:\\Users\\user\\Desktop\\ALPDF\\dog{self.image_num}.jpg"     # 본인 PC에 저장하고자 하는 경로\\image파일 이름.확장자
                        self.image_num += 1                                                         # 여러개의 이미지의 이름을 달리 하기 위해

                        img = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
                        cv2.imwrite(save_path, img)

                # self.recv_datas.pop(0)   # 처리한 메시지(상태) 제거
                # print(self.remote_manages)


    def int_trans(self) -> None:
        '''
            • output callback을 위한 상태 천이(Wait -> Generate)
        '''
        self.init_state(MsgSend.STATE_GENERATE)
        

    def recvData(self) -> None:     
        '''
            • 수신 전용 thread의 callback method \n
            • 블로킹 방식으로 데이터 수신
        '''
        while True:
            print("recieve start...")
            # self.recv_datas.append(self.router.recv_multipart())

            recv_datas = self.router.recv_multipart()
            self.criticalSection(
                mode = MsgSend.MODE_WRITE, 
                write_datas = recv_datas
            )

    def criticalSection(self, mode, write_datas = None) -> None | list:
        self.lock.acquire()     # lock 획득

        try:
            if mode == MsgSend.MODE_WRITE:
                self.recv_datas.append(write_datas)
                return

            elif mode == MsgSend.MODE_READ:
                new_list = list(self.recv_datas)
                self.recv_datas.clear()
                return new_list
        finally:
            self.lock.release() # lock 해제


if __name__ == "__main__":
    ss = SystemSimulator()                                                  # 엔진 객체 생성

    context = zmq.Context()                                                 # zmq context 생성
    router = context.socket(zmq.ROUTER)                                     # router소켓 생성
    router.bind("tcp://127.0.0.1:5555")                                     # router 소켓 바인딩

    ss.register_engine("first", "VIRTUAL_TIME", 1)                          # 엔진 생성
    ss.get_engine("first").insert_input_port("start")                       # 엔진에 포트 추가

    gen = MsgSend(0, Infinite, "Gen", "first", router)                      # 모델 생성 및 수신 전용 thread 생성 및 실행
    ss.get_engine("first").register_entity(gen)                             # 엔진에 모델 추가

    ss.get_engine("first").coupling_relation(None, "start", gen, "start")   # 모델의 포트 연동(엔진과 연동)

    ss.get_engine("first").insert_external_event("start", None)             # 모델 실행을 위한 event 입력
    ss.get_engine("first").simulate()                                       # 모델 실행

    