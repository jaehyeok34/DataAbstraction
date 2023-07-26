import zmq

def server():
    context = zmq.Context()
    router_socket = context.socket(zmq.ROUTER)
    router_socket.bind("tcp://*:5555")

    print("서버가 시작되었습니다.")

    while True:
        identity, message = router_socket.recv_multipart()
        print(f"서버에서 메시지 수신: {message.decode()}")

        reply = f"서버가 '{message.decode()}' 메시지를 받았습니다."
        router_socket.send_multipart([identity, reply.encode()])

def client(client_id):
    context = zmq.Context()
    dealer_socket = context.socket(zmq.DEALER)
    dealer_socket.setsockopt(zmq.IDENTITY, client_id.encode())
    dealer_socket.connect("tcp://localhost:5555")

    print(f"클라이언트 {client_id}가 시작되었습니다.")

    while True:
        message = input("메시지를 입력하세요 (또는 '종료' 입력): ")
        if message.lower() == "종료":
            break

        dealer_socket.send_string(message)
        reply = dealer_socket.recv_string()
        print(f"클라이언트 {client_id}에서 서버로부터 응답 받음: {reply}")

if __name__ == "__main__":
    server()

    client_id = input("클라이언트 ID를 입력하세요: ")
    client(client_id)


