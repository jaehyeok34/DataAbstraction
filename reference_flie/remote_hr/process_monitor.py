from pyevsim import BehaviorModelExecutor, SystemSimulator, Infinite, SysMessage
import subprocess as sp
import os, signal, cv2
import psutil

class ProcessMonitor(BehaviorModelExecutor) :
    # 필요한 기능 :
        # 1. 핸들러한테 받은 정보를 토대로 서브프로세스 만들기
        # 2. 만든 서브프로세스의 pid를 리시버한테 보내기
        # 3. 리시버한테 start가 오면, 서브프로세스를 종료시키기

    def __init__(self, instance_time, destruct_time, name, engine_name, process_info) :
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("pid_send", 1)
        self.insert_state("Signal_in", 2)
        self.insert_state("After_start", 1)

        # self.insert_output_port("ack")
        # self.insert_input_port("start")
        # self.insert_input_port("process_init")
        self.insert_input_port("hand2mon")
        self.insert_input_port("recv2mon")
        self.insert_output_port("mon2recv")

        self.process = None
        self.process_info = process_info

        
    def ext_trans(self, port, msg):
        # print(self.get_name()," : ", self.get_cur_state())
        if port == "recv2mon" :
            if msg.retrieve()[0] == "start" :
                os.kill(self.process.pid, signal.SIGTERM)
                print(f"{self.process.pid} is terminated")
                self._cur_state = "After_start"

        # 핸들러한테 받은 정보를 토대로 서브프로세스 만들기
        if port == "hand2mon" :
            # print(self.process_info)
            self.process = sp.Popen(['python','-m',self.process_info[1]])
            print(self.get_name(), " : ", self.process.pid)
            self._cur_state = "pid_send"
            
        return None
    
    def output(self):
        if self._cur_state == "pid_send" :
            msg = SysMessage(self.get_name(), "mon2recv")
            msg.insert(["generated_pid", self.process.pid])
            return msg

        elif self._cur_state == "Signal_in" :
            # print(self.get_name()," : ", self.get_cur_state())
            if psutil.pid_exists(self.process.pid) :
                
                result_code = self.process.poll()
                # result_return = self.process.communicate()
                if result_code != None :
                    print(f"result_return : {result_code}")
                    msg = SysMessage(self.get_name(), "mon2recv")
                    msg.insert(['terminated',self.process.pid])
                    return msg
                else :
                    pass
            else :
                self._cur_state = "Wait"
        
        elif self._cur_state == "After_start" :
            msg = SysMessage(self.get_name(), "mon2recv")
            msg.insert(['terminated', self.process.pid])
            self._cur_state = "Wait"
            return msg

    
    def int_trans(self):
        if self._cur_state == "Signal_in" :
            # print(self._cur_state)
            self._cur_state = "Signal_in"
        elif self._cur_state == "pid_send" :
            self._cur_state = "Signal_in"
    