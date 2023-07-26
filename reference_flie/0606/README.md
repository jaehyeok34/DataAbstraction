# 구현 사항
1. control.py의 구조 변경
    - send, recv를 개별적인 모델로 구현하던 방식에서 하나의 모델에서 multi-thread를 통한 비동기 처리로 변경
    - 모델의 생성자에서 수신 전용 thread를 생성 및 실행 시키고, 송신 루틴은 모델의 output에서 처리함
    - 공유 변수(self.recv_datas, type: list)를 만들어 수신한 데이터를 저장하고, 송신 루틴에서 이를 읽어다가 처리함
    - self.remote_manages의 구조를 list에서 dictionary 형태로 변경(키:값 = identity:state, state는 CONNECTED와 READY가 있음)
    - 이미지를 수신하여 설정한 경로에 저장하는 기능 추가
    <img src = "control 구조 변경.jpg">

# 구현하지 않은 내용
1. pid 관련 내용
2. TERMINATED를 수신했을 때 처리

# 궁금한 사항
1. control이 pid를 받아서 무엇을 하려 했는가?
    - process 컨트롤은 이미 remote에서 하고 있고, 다 종료된 process의 id를 TERMINATED와 보내서 무엇을 하려 했는가?
    - 내가 생각한 TERMINATED 상태를 받았을 때는 process에서 작업이 끝나고, 
    데이터 전송까지 끝이나서 더 이상 remote가 유지될 필요가 없어서 remote를 종료시키고자 보낸 상태라고 생각했으며, 
    remote의 identity 값을 함께 전달하여 control에서 관리중인 remote_manages에서 제거시키려는 의도인 줄 알았음
2. remote에 구조
    - 시뮬레이션과 모델이 각각 몇개이며, 포트는 어떻게 연결되어 있는지 한 눈에 볼 수 있는 그림이 필요함!!!
    - 코드 보고 이해하기 힘듦...

# yj's f_control.py 리뷰
1. img_socket의 의도는?
    - image를 수신받기 위해 별도의 socket을 생성한 이유가 궁금함 영빈이의 예제 코드가 router/dealer 패턴이 아니라서 생성한 거??
    - 아니면, 중간에 만들었다가 삭제하지 않은 내용??
    - 진짜 image 수신을 위한 별도의 socket이었다면, img_socket 자체가 process에 bind 되어있지 않아서 사용 불가능하고
    - 이미 router가 먼저 recv를 하고 있기 때문에 img_socket이 recv할 기회를 뺏길 거임
2. MsgSend 모델에서 이미지를 전송 받았을 때 저장하는 부분이 else?
    - recv_data에 CONNECTED, READY 이외에도 TERMINATED와 IMAGE가 들어갈 수 있기 때문에 else로는 처리 불가 하므로 더 세분화 해야함.
3. MsgRecv 모델에서 recv 받는 데이터
    - 의도하기로는 주석 부분 밑에서 img_socket으로 recv 호출해서 이미지를 수신하고, msg에 넣어서 return 시키게끔 구현하라 한 거 같음(아님 말고)
    - 근데 애초에 recv가 non-blocking이기 때문에 recv가 2개 이상이 되면 어떤 recv가 수신 하는 지 예상 할 수 없음.
    - 맨 처음에 router가 호출하는 recv에서 이미지를 받을 수도 있는데, 현재 코드는 router는 무조건 pid를 받는 다는 형식으로 구현되어 있음(pid = ', '.join(data.decode() for data in datas))
    - 따라서, recv는 non-blocking일 수록 더더욱 하나여야만 하고, 어떠한 데이터를 받던 일단 MsgSend로 넘겨주고, MsgSend에서 전달받은 state에 따라 처리하도록 구현하는 게 맞다고 생각함