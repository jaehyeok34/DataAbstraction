import zmq
import threading
import time

def recv_data():
    while True:
        datas = dealer_socket.recv_multipart()     # 데이터 수신

        # Router가 정상 종료 확인 했을 때
        if b"exit" in datas:
            break

        print(f"received: {', '.join(data.decode() for data in datas)}")

def send_data():
    while True:
      datas = input()      
      datas = datas.split(" ")
      dealer_socket.send_multipart([data.encode() for data in datas])   # 데이터 송신

      # 정상 종료 요청을 했을 경우
      if "exit" in datas:   
          break


if __name__ == "__main__":
    context = zmq.Context()
    dealer_socket = context.socket(zmq.DEALER)
    dealer_socket.setsockopt(
       zmq.IDENTITY, 
       input("Enter your ID > ").encode()
    )
    dealer_socket.connect("tcp://localhost:5454")

    recv_thread = threading.Thread(target=recv_data)

    recv_thread.start()     # 수신 전용 thread 시작
    send_data()             # 송신 시작

    recv_thread.join()      # 수신 전용 thread 종료 대기
    dealer_socket.close()   # Dealer 소켓 닫기
    context.term()          # context 반환