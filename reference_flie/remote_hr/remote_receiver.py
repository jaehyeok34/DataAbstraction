from pyevsim import BehaviorModelExecutor, SystemSimulator, Infinite, SysMessage
import zmq
import os, cv2


class RemoteReceiver(BehaviorModelExecutor) :
    # 필요한 기능
        # 1. 커넥션한테 소켓 받기
        # 2. 소켓을 받으면 외부입력에 대해 받을 준비
        # 3. 모니터로부터 뭔가 오는것도 받기 (pid 같은거)
        # 아마 대부분의 정보를 리시버가 받고있을 것

    def __init__(self, instance_time, destruct_time, name, engine_name, socket: zmq.Socket, process_list) :
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Check_input", 1)
        self.insert_state("Send_img", 1)

        self.insert_input_port("connect")
        self.insert_input_port("mon2recv")
        self.insert_output_port("recv2mon")
        self.insert_output_port("recv2hand")

        self.socket = socket
        self.process_list = process_list
        self.pids = []

    def ext_trans(self, port, msg):
        if port == "connect" :
            print("Try to connect...")
            self.socket.send_string("CONNECTED")
            self._cur_state = "Check_input"

        if port == "mon2recv" :
            get_msg = msg.retrieve()[0]

            if get_msg[0] == 'generated_pid' :
                self.pids.append(get_msg[1])
                print(self.pids)

                if len(self.process_list) == len(set(self.pids)) :
                    self.socket.send_multipart(["READY".encode()])
                    self._cur_state = "Check_input"

                # else : self._cur_state = "Wait"
            
            elif get_msg[0] == 'terminated' :
                self.socket.send_multipart(["TERMINATED".encode(), str(get_msg[1]).encode()])
                self._cur_state = "Send_img"
                # print(get_msg)


    def output(self):
        if self._cur_state == "Check_input" :
            try :
                recv_item = self.socket.recv_multipart(flags=zmq.NOBLOCK)
                in_item = recv_item[0].decode()
                print("receive item : ", in_item)

                if in_item == "SPAWN" :
                    print("Spawn receieved")
                    msg = SysMessage(self.get_name(), "recv2hand")
                    msg.insert(None)
                    return msg
                
                elif in_item == "START" :
                    msg = SysMessage(self.get_name(), "recv2mon")
                    msg.insert("start")
                    self._cur_state = "Send_img"
                    return msg
            except zmq.Again as e :
                pass
                
        elif self._cur_state == "Send_img" :
            print(self.get_name(), " : Send image!")
            ################### 이미지 송신 코드 ###################
            path = "C:\\Users\\User\\Desktop\\HelloWorld\\cat.png" # 이미지 파일이 있는 경로 설정
            img = cv2.imread(path)
            _, img_str = cv2.imencode(".png", img)

            # 이미지를 전송할 때는 반드시 [b"상태", b"이미지 인코드 문자열", ...] 형태로 전달 해야함
            # 즉, 가장 앞에 하나의 상태 문자열이 추가 되어 있어야지 control에서 처리 가능함(두 개면 처리 안됨)
            self.socket.send_multipart(["IMAGE".encode(), img_str])
            #######################################################

            self._cur_state = "Wait"
            

    def int_trans(self):
        if self._cur_state == "Check_input" :
            self._cur_state = "Check_input"
    