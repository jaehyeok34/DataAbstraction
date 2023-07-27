from enum import Enum

class Codec:
    # static field
    commands = ['run', 'stop', ]

    # method
    @staticmethod
    def encode(datas: str) -> list[bytes]:
        return [part.encode() for part in datas.split()]


    @staticmethod
    def decode(datas: list[bytes]) -> list[str]:
        return [part.decode() for part in datas]
