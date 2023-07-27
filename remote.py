import zmq
from codec import Codec


def remote():
    context = zmq.Context()
    router_socket = context.socket(zmq.ROUTER)
    router_socket.bind("tcp://127.0.0.1:3400")
    print("서버가 시작되었습니다.")

    identity, _ = router_socket.recv_multipart()
    print(f"dealer 연결: {identity}")

    while True:
        datas = input('명령 입력 > ')
        router_socket.send_multipart([identity] + Codec.encode(datas))
        
        
if __name__ == "__main__":
    remote()


