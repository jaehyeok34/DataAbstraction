import zmq

def dealer(dealer_id: str):
    context = zmq.Context()
    dealer_socket = context.socket(zmq.DEALER)
    dealer_socket.setsockopt(zmq.IDENTITY, dealerID.encode())
    dealer_socket.connect("tcp://localhost:3400")

    print(f"클라이언트 {dealerID}가 시작되었습니다.")

    while True:
        message = input("메시지를 입력하세요 (또는 '종료' 입력): ")
        if message.lower() == "종료":
            break

        dealer_socket.send_multipart([message.encode()])
        reply = dealer_socket.recv_multipart()
        print(f"클라이언트 {dealerID}에서 서버로부터 응답 받음: {reply[0].decode()}")

if __name__ == "__main__":
    dealerID = input("클라이언트 ID를 입력하세요: ")
    dealer(dealerID)


