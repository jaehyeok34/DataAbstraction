import zmq

def router():
    context = zmq.Context()
    router_socket = context.socket(zmq.ROUTER)
    router_socket.bind("tcp://127.0.0.1:3400")

    print("서버가 시작되었습니다.")

    while True:
        identity, message = router_socket.recv_multipart()
        print(f"서버에서 메시지 수신: {message.decode()}")

        reply = f"서버가 '{message.decode()}' 메시지를 받았습니다."
        router_socket.send_multipart([identity, reply.encode()])

if __name__ == "__main__":
    router()

