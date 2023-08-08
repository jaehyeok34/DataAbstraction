from parts_function import PartsFunction
import zmq
import pickle
import threading
import time

class PartsDB:
    NET_INFO = 'tcp://127.0.0.1:3400'
    NOT_FOUND_ERROR = b'NotFoundError'
    

    __partsInfo = {
        # parts name & engine input port    :   [input port,    function]
        '*'                            :   ['MUL', PartsFunction.mul],
    }

    @staticmethod
    def main() -> None:
        socket = PartsDB.__initSocet()
        PartsDB.__printCurrentDB()
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
    def __recv(socket: zmq.Socket) -> None:
        while True:
            userID, parts = socket.recv_multipart()[:2]
            print()
            print(f'request: get "{parts.decode()}" parts')

            foundParts = [PartsDB.NOT_FOUND_ERROR]
            try:
                foundParts = [parts, pickle.dumps(PartsDB.__partsInfo[parts.decode()])]
            except KeyError:
                pass
            finally:
                print(f'response: {foundParts[0].decode()}')
                socket.send_multipart([userID, *foundParts])

    @staticmethod
    def __printCurrentDB() -> None:
        print(f'current DB instance: {list(PartsDB.__partsInfo.keys())}')
                
    def addInstance() -> None:
        time.sleep(10)
        print()
        print('Add "/" parts to DB')
        PartsDB.__partsInfo['/'] = ['DIV', PartsFunction.div]
        PartsDB.__printCurrentDB()

if __name__ == '__main__':
    t = threading.Thread(target=PartsDB.addInstance)
    t.start()
    PartsDB.main()