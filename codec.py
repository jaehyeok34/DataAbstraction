from enum import Enum
from typing import Union

class Codec:
    # static field
    class Commands(Enum):
        run = 'start'
        stop = 'stop'

        def values() -> list[bytes]:
            return [command.value for command in list(Codec.Commands)]

    # method
    @staticmethod
    def encode(datas: str) -> Union[list[bytes], bool]:
        parts = datas.split()
        command = parts[0]

        if command not in Codec.Commands.values():
            print('failed: 존재하지 않는 명령입니다.')
            return False
        else:
            return [part.encode() for part in parts]


    @staticmethod
    def decode(datas: list[bytes]) -> list[str]:
         return [part.decode() for part in datas]
