import zmq
import threading
import time
import os
import sys
from concurrent import futures
import random

'''
2023. 06. 07
용량이 큰 파일(대략 1GB 내외, binary)을 zmq 소켓을 통해 전송하며, thread pool 성능 테스트

특징
 - threading.Lock을 통해 임계 구역을 설정하여 하나의 소켓에 여러 thread가 동시 접근하는 것을 막음
 - 임계 구역 설정을 통해 소켓에 하나의 thread만 접근해서 send를 하기 때문에, 데이터 처리 속도가 빨라질수록 send가 밀리게 됨
 - 대신, 소켓 안정성이 보장되기 때문에 임계 구역 설정에 대한 고민이 필요
 - 데이터의 크기가 커질수록 임계 구역 설정이 없는 구조보다 더 높은 성능을 보임(데이터의 크기가 낮으면 성능이 비슷하거나 살짝 낮음)

진행 사항
 - 데이터 송신 안정성을 보장하고자 send_multipart()가 반환하는 MessageTracker 객체를 통해, 송신 완료 여부 확인
 - 일정 크기(약 2GB)이상이 되면, 송신 완료 여부를 확인하기 위한 wait()이 무한 blocking 됨
'''


def recvDatas():
    global dealer_socket

    print("receive start")
    while True:
        try:
            recv = dealer_socket.recv_multipart()
            print(f"received: {recv}")
        except zmq.error.ZMQError:
            print("Error: dealer_socket is closing")
            print("return")
            return


def main():
    global thread_pool, num_of_message

    # while True:
    for i in range(1, num_of_message + 1):
        try:
            print(f"{i}번째 작업 요청")
            # future = thread_pool.submit(sendLargeFile, random.randint(10, 20), i)
            future = thread_pool.submit(sendLargeFile, 8, i)
            # future.add_done_callback(lambda future: print(f"No.{future.result()} send complated!: {future.done()}"))
            future.add_done_callback(done)

        except KeyboardInterrupt:
            print("Error: KeyboardInterrupt occour")
            return
        
def done(future: futures.Future):
    global end, event, processing_count

    if processing_count == num_of_message:
        end = time.perf_counter()
        event.set()
    
    print(f"No.{future.result()} send complated!")
    processing_count += 1

def sendLargeFile(size, number):
    global dealer_socket, socket_lock

    socket_lock.acquire()
    print(f"No.{number} file size: {size}")
    try:
        file_path = "C:\\Users\\User\\Desktop\\족보\\test_file.zip"
        with open(file_path, "rb") as file:
            data = file.read()

            start_time = time.perf_counter()
            print(f"No.{number} send start")
            tracker = dealer_socket.send_multipart([data * size], copy=False, track=True)
            if isinstance(tracker, zmq.MessageTracker):
                try:
                    tracker.wait()
                except Exception as e:
                    print(e)
                    print(tracker.done)

                end_time = time.perf_counter()
                print(f"No.{number}send complate!")

            print(f"No.{number} duration: {end_time - start_time}")
            return number

    except FileNotFoundError:
        print("file not found")

    finally:
        socket_lock.release()
        pass


if __name__ == "__main__":
    # program initialization
    context = zmq.Context()
    dealer_socket = context.socket(zmq.DEALER)
    dealer_socket.connect("tcp://localhost:5555")

    recv_thread = threading.Thread(target=recvDatas)

    thread_pool = futures.ThreadPoolExecutor(max_workers=3)
    socket_lock = threading.Lock()

    event = threading.Event()

    processing_count = 1
    num_of_message = 1

    # program start
    recv_thread.start()
    start = time.perf_counter()
    end = 0
    main()
    
    event.wait()
    print(f"process running time; {end - start}")


    # program terminate routine
    # dealer_socket.close()    
    # context.term()

    # recv_thread.join()
    # print(f"recv_thread is alive?: {recv_thread.is_alive()}")

    # print("program terminated")

    