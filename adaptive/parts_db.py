from parts_function import PartsFunction
import zmq
import pickle

class PartsDB:
    NET_INFO = 'tcp://127.0.0.1:3400'
    NOT_FOUND_ERROR = b'NotFoundError'
    

    __partsInfo = {
        # parts name & engine input port    :   [input port,    function]
        'partsD'                            :   ['D', PartsFunction.funcD],
    }

    @staticmethod
    def main():
        socket = PartsDB.__initSocet()
        PartsDB.__recv(socket)

    @staticmethod
    def getParts(socket: zmq.Socket, partsName: str) -> tuple[str, list] | None:
        socket.send_multipart([partsName.encode()])
        reply = socket.recv_multipart()
        if PartsDB.NOT_FOUND_ERROR not in reply:
            return tuple([reply[0].decode(), pickle.loads(reply[1])])
        else:
            return None

    # private static method
    @staticmethod
    def __initSocet() -> zmq.Socket:
        context = zmq.Context()
        socket = context.socket(zmq.ROUTER)
        socket.bind(PartsDB.NET_INFO)
        print('소켓이 바인드 됐습니다.')

        return socket

    @staticmethod
    def __recv(socket: zmq.Socket):
        while True:
            userID, parts = socket.recv_multipart()[:2]
            print(parts)

            foundParts = [PartsDB.NOT_FOUND_ERROR]
            try:
                foundParts = [parts, pickle.dumps(PartsDB.__partsInfo[parts.decode()])]
            except KeyError:
                pass
            finally:
                print(f'db send! {foundParts}')
                socket.send_multipart([userID, *foundParts])
                

if __name__ == '__main__':
    PartsDB.main()