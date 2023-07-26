import zmq
import threading
import time
import os
import sys
from concurrent import futures
import random

'''
2023. 06. 07
send_large_file_test.py와 동일한 동작을 하지만, 임계 구역 설정이 없는 버전

보내는 데이터의 크기가 작으면 임계 구역 설정 버전에 비해 성능이 조금 좋거나 비슷함
반대로 데이터 크기가 클 수록 오히려 임계 구역 설정 버전의 성능이 압도적으로 좋아짐
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
    global thread_pool

    # while True:
    for i in range(1, 6):
        try:
            print(f"{i}번째 작업 요청")
            # future = thread_pool.submit(sendLargeFile, random.randint(10, 20), i)
            future = thread_pool.submit(sendLargeFile, 10, i)
            # future.add_done_callback(lambda future: print(f"No.{future.result()} send complated!: {future.done()}"))
            future.add_done_callback(done)

        except KeyboardInterrupt:
            print("Error: KeyboardInterrupt occour")
            return
        
def done(future: futures.Future):
    global end, event, processing_count

    if processing_count == 5:
        end = time.perf_counter()
        event.set()
    
    print(f"No.{future.result()} send complated!")
    processing_count += 1

def sendLargeFile(size, number):
    global dealer_socket, socket_lock

    # socket_lock.acquire()
    print(f"No.{number} file size: {size}")
    try:
        file_path = "C:\\Users\\User\\Desktop\\족보\\test_file.zip"
        with open(file_path, "rb") as file:
            data = file.read()

            start_time = time.perf_counter()
            print(f"No.{number} send start")
            dealer_socket.send_multipart([data * size])
            end_time = time.perf_counter()
            print(f"No.{number} send complated")
            print(f"No.{number} duration: {end_time - start_time}")
            return number

    except FileNotFoundError:
        print("file not found")

    finally:
        # socket_lock.release()
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

    