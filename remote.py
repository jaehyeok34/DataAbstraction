import zmq
import threading
import time
import cv2
import os

'''
2023. 06. 07
thread_pool_control.py와 함께 실행하는 파일
특정 주기(대략 0초 미만)마다 자동으로 thread_pool_control에 있는 router 소켓에게
CONNECTED 메시지를 전송함
'''

lock = threading.Lock()

def recv_data():
    while True:
        ####################### 정상적인 receive #########################
        datas = dealer_socket.recv_multipart()     # 데이터 수신

        # Router가 정상 종료 확인 했을 때
        if b"exit" in datas:
            break

        print(f"received: {', '.join(data.decode() for data in datas)}")

        #################### 에러 테스트 용 1 ##############################
        # try:
        #     dealer_socket.send_multipart(["CONNECTED".encode()])
        #     print("worker thread: send!")
        #     time.sleep(0.03)
        # except KeyboardInterrupt:
        #     return

        # except Exception as e:
        #     print(f"Error: {e}")

        #################### 에러 테스트 용 1 ##############################
        # dealer_socket.send_multipart(["CONNECTED".encode()])
        # print("worker thread: send!")
        # time.sleep(0.01)


def send_data():
    while True:
        try:
        #     datas = input()      
        #     datas = datas.split(" ")

        #     # 정상 종료 요청을 했을 경우    
        #     if "exit" in datas:   
        #         break

        #     if "send" in datas:
        #         path = "C:\\Users\\user\\Desktop\\DS_week_6\\dog.jpg"
        #         img = cv2.imread(path)
        #         _, img_str = cv2.imencode(".jpg", img)
        #         print(type(img_str))
        #         dealer_socket.send_multipart(["send".encode(), img_str, img_str])
        #     else:
        #         dealer_socket.send_multipart([data.encode() for data in datas])
            dealer_socket.send_multipart(["CONNECTED".encode()])
            print("main thread: send!")
            time.sleep(0.03)

        except KeyboardInterrupt:
            return
        
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    context = zmq.Context()
    dealer_socket = context.socket(zmq.DEALER)
    dealer_socket.setsockopt(
       zmq.IDENTITY, 
       input("Enter your ID > ").encode()
    )
    dealer_socket.connect("tcp://localhost:5555")

    recv_thread = threading.Thread(target=recv_data)
    recv_thread.daemon = True
    recv_thread.start()     # 수신 전용 thread 시작
    send_data()             # 송신 시작

    recv_thread.join()      # 수신 전용 thread 종료 대기
    dealer_socket.close()   # Dealer 소켓 닫기
    context.term()          # context 반환