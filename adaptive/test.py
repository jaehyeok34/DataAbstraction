# # # ################ partsDB 테스트 용도 ################
# # # # import zmq
# # # # import threading

# # # # def main():
# # # #     while True:
# # # #         reply = socket.recv_multipart()
# # # #         print(reply)

# # # # def sender():
# # # #     while True:
# # # #         msg = input('> ').encode()
# # # #         socket.send_multipart([msg])
        

# # # # context = zmq.Context()
# # # # socket = context.socket(zmq.DEALER)
# # # # socket.setsockopt_string(zmq.IDENTITY, 'jang')
# # # # socket.connect('tcp://127.0.0.1:3400')
# # # # socket.send_multipart([b'connected'])
# # # # print('소켓이 연결됐습니다.')

# # # # td = threading.Thread(target=sender)
# # # # td.start()
# # # # main()
# # # #########################################################

# # # ################ evsim 모델 추가 테스트 ##################
# # # # from pyevsim import BehaviorModelExecutor, SystemSimulator
# # # # from pyevsim.definition import Infinite
# # # # import time
# # # # import threading

# # # # class md(BehaviorModelExecutor):
# # # #     def __init__(
# # # #             self, 
# # # #             instantiate_time=..., 
# # # #             destruct_time=..., 
# # # #             name=".", 
# # # #             engine_name="default"
# # # #     ) -> None:
# # # #         super().__init__(instantiate_time, destruct_time, name, engine_name)
# # # #         self.inPort = 'input'
# # # #         self.outPort = 'output'

# # # #         self.insert_state('ex', 1000)
# # # #         self.init_state('t')

# # # #         self.insert_input_port(self.inPort)
# # # #         self.init_state('t')

# # # #     def ext_trans(self, port, msg):
# # # #         print('model execute')
# # # #         self.init_state('ex')

# # # #     def int_trans(self):
# # # #         self.init_state('ex')

# # # #     def output(self):
# # # #         print(self.get_name())
# # # #         time.sleep(2)
        



# # # # def tmp():
# # # #     msg = input('> ')
# # # #     if msg == 'add':
# # # #         engine.insert_external_event(engineInputPort, None)



# # # # if __name__ == '__main__':
# # # #     engineName = 'engine'
# # # #     engineInputPort = 'start'
# # # #     engine = SystemSimulator.register_engine(engineName, "VIRTUAL_TIME", 1)
# # # #     model = md(0, Infinite, "c", engineName)
# # # #     model2 = md(0, Infinite, "h", engineName)

# # # #     ## engine 설정
# # # #     engine.insert_input_port(engineInputPort)
# # # #     engine.register_entity(model2)
# # # #     engine.coupling_relation(
# # # #     None,   engineInputPort, 
# # # #     model2,  model2.inPort
# # # #     )

# # # #     t = threading.Thread(target=tmp)
# # # #     t.start()

# # # #     ## engine 실행
# # # #     engine.simulate()
# # # #############################################################################

# # # ############### sub/pub 테스트 #############
# # # # import threading
# # # # import zmq
# # # # import time

# # # # def pub():
# # # #     context = zmq.Context()
# # # #     socket = context.socket(zmq.PUB)
# # # #     socket.bind('tcp://127.0.0.1:3333')

# # # #     while True:
# # # #         msg = b'test'
# # # #         socket.send_multipart([msg])
# # # #         time.sleep(2)

# # # # def sub():
# # # #     context = zmq.Context()
# # # #     socket = context.socket(zmq.SUB)
# # # #     socket.connect('tcp://127.0.0.1:3333')

# # # #     print(f'sub 연결 완료')
    
# # # #     while True:
# # # #         reply = socket.recv_multipart()
# # # #         print(reply)


# # # # t1 = threading.Thread(target=sub)
# # # # t2 = threading.Thread(target=sub)
# # # # t1.start()
# # # # t2.start()

# # # # pub()
# # # ###################################################
# # # import pickle
# # # from pyevsim import BehaviorModelExecutor
# # # from pyevsim.definition import Infinite

# # # from pyevsim import BehaviorModelExecutor, SysMessage
# # # from pyevsim.definition import Infinite
# # # import time

# # # class Parts(BehaviorModelExecutor):
# # #     # private static field
# # #     __executed      =   'executed'
# # #     __terminated    =   'terminated'

# # #     def __init__(
# # #         self, 
# # #         inputPort   :   str,
# # #         callback    :   callable,
# # #         instantiate_time        =   ..., 
# # #         destruct_time           =   ...,
# # #         name                    =   ".",
# # #         engine_name             =   "default",
# # #     ):
# # #         super().__init__(
# # #             instantiate_time, 
# # #             destruct_time, 
# # #             name, 
# # #             engine_name
# # #         )
# # #         self.__callback = callback
        
# # #         self.insert_state(Parts.__executed, 1000)
# # #         self.insert_state(Parts.__terminated)
# # #         self.insert_input_port(inputPort)

# # #         self.init_state(Parts.__terminated)

# # #     def int_trans(self):
# # #         self.init_state(Parts.__terminated)

# # #     def ext_trans(self, port, msg: SysMessage):
# # #         x, y = msg.retrieve()[0][:2]
# # #         print(f'{msg.retrieve()[0]} 처리 결과: {self.__callback(x, y)}')
# # #         self.init_state(Parts.__executed)

# # #     def output(self):
# # #         print(f'{self.get_name()} parts 종료')

# # # # if 'partsD' in list(tmp.keys()):
# # # #         print(pickle.dumps(tmp['partsD']))

# # # def summ(x, y):
# # #     return x + y

# # # pp = Parts('none', summ, Infinite, 'none', 'none')

# # # p = pickle.dumps(pp)
# # # print(p)


# # from parts_function import PartsFunction
# # import pickle
# # import zmq
# # import threading
# # import time

# # def main():
# #     contextt = zmq.Context()
# #     sockett = contextt.socket(zmq.ROUTER)
# #     sockett.bind('tcp://127.0.0.1:3400')

# #     while True:
# #         reply = sockett.recv_multipart()
# #         # print(reply)
# #         print(pickle.loads(reply[1])([10, 20]))

# # def sender():
# #     socket = context.socket(zmq.DEALER)
# #     socket.setsockopt_string(zmq.IDENTITY, 'jang')
# #     socket.connect('tcp://127.0.0.1:3400')
# #     print('소켓이 연결됐습니다.')
# #     while True:
# #         # msg = input('> ').encode()
# #         socket.send_multipart([p])
# #         time.sleep(1)
# #         print('재전송')
        

# # context = zmq.Context()



# # p = pickle.dumps(PartsFunction.funcA)
# # td = threading.Thread(target=sender)
# # td.start()
# # main()

# import pickle
# from parts_function import PartsFunction

# partsInfo = {
#     # model name & engine input port    :   [input port,    function]
#     'partsD'                            :   ['D', PartsFunction.funcD],
#     'partsE'                            :   ['D', PartsFunction.funcA],
# }

# p = pickle.dumps(partsInfo)

# def tmp(d: dict):
#     print(list(d.items()))
    
# tmp(pickle.loads(p))

# l = [3]
# q = [1 , 2]

# m = ['a', 'c', False, [1, 2]]

# print(type(tuple(m)))
# a, c, f, n = tuple(m)
# print(a)
# print(c)
# print(f)
# print(n)

# def t():
#     return None

# s, d = t()
# print(s)

print(str(10))