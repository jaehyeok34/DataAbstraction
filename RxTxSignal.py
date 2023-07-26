'''
2023. 06. 07
remote, cotrol 사이에서 주고받는 신호(상태)를 정의
'''

class RxTxSignal:
    CONNECTED = b"CONNECTED"    # 연결 시도, (remote -> control)
    SPAWN = b"SPAWN"            # 연결 확인(승인), (control -> remote)
    READY = b"READY"            # process 실행 가능 상태, (remote -> control)
    START = b"START"            # 모든 remote가 process 실행 가능 상태, (control -> remote)
    IMAGE = b"IMAGE"            # 이미지 파일 전송, (remote -> control)