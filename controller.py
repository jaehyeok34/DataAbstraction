import zmq
from codec import Codec

def controller(dealer_id: str):
    context = zmq.Context()
    dealer_socket = context.socket(zmq.DEALER)
    dealer_socket.setsockopt(zmq.IDENTITY, soctketID.encode())
    dealer_socket.connect("tcp://localhost:3400")
    print(f"dealer {soctketID}가 시작되었습니다.")
    dealer_socket.send_multipart(['connected'.encode()])

    while True:
        command, datas = Codec.decode(dealer_socket.recv_multipart())
        print(f'command: {command}, datas: {datas}')

        if command in Codec.commands:
            print(f'프로그램을 {command} 합니다.')



if __name__ == "__main__":
    soctketID = input("클라이언트 ID를 입력하세요: ")
    controller(soctketID)


