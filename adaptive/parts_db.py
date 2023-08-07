import zmq

class PartsDB:
    names = [
        'partsD',
        'partsE',
    ]
    @staticmethod
    def main():
        socket = PartsDB.__initSocet()
        PartsDB.__recv(socket)

    @staticmethod
    def __initSocet() -> zmq.Socket:
        context = zmq.Context()
        socket = context.socket(zmq.ROUTER)
        socket.bind('tcp://127.0.0.1:3400')
        print('소켓이 바인드 됐습니다.')

        return socket

    @staticmethod
    def __recv(socket: zmq.Socket):
        while True:
            reply = socket.recv_multipart()

            for item in reply:
                msg = 'NotFoundError'
                if item.decode() in PartsDB.names:
                    msg = item

                print('db send!')
                socket.send_multipart([reply[0], item])
                

if __name__ == '__main__':
    PartsDB.main()