import socket

def find_my_internal_ip() :

    socket_open = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_open.connect(('www.google.co.kr', 443))

    print(socket_open.getsockname()[0])
    return socket_open.getsockname()[0]