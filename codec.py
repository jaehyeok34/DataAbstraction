from enum import Enum
import traceback
from typing import Callable, Any


class Codec:
    # priavate field -----
    __ENCODE = 0        # function table mode
    __DECODE = 1        # function table mode
    __EDP = b'EDP'      # Encoding Data Point: 인코딩 데이터 시작점을 알리기 위한 더미 데이터

    # public static method -----
    @staticmethod
    def encode(param) -> list[bytes] | None:
        try:
            # [b'EDP', b'{type}', b'{data}']의 형태로 반환
            return [Codec.__EDP] + Codec.__getFunctionTable(Codec.__ENCODE)[type(param).__name__](param)
        except KeyError:
            # int, bool, string, list외에 type이 들어왔을 경우
            traceback.print_exc()
            print(f"EncodingError: '{type(param).__name__}' 형식은 부호화를 지원하지 않습니다.")
            return None
    

    @staticmethod
    def decode(param: list[bytes]) -> tuple:
        encoded = []                                # 인코딩된 데이터
        retValue = []                               # 반환값
        
        # EDP 탐색(EDP 이후 부터 인코딩된 데이터)
        for i in range(len(param)):
            if param[i] == Codec.__EDP:
                encoded = param[i + 1:]
                param = param[:i]
                break
        
        # 디코딩 진행
        for i in range(0, len(encoded) - 1, 2):
            try:
                retValue.append(Codec.__getFunctionTable(Codec.__DECODE)[encoded[i].decode()](encoded[i + 1]))
            # 디코딩을 지원하지 않는 타입(int, bool, string 지원)
            except KeyError:
                traceback.print_exc()
                print(f"EncodingError: '{type(encoded[i]).decode()}' 형식은 부호화를 지원하지 않습니다.")

        return tuple(param + retValue)
    

    # private method -----
    # type에 따른 인/디코딩 방식을 다르게 적용하기 위해, 각 기능을 제공하는 함수 테이블 반환(lookup table)
    @staticmethod
    def __getFunctionTable(mode: int) -> (
        Callable[[int], list[bytes]] | Callable[[list[bytes]], Any]
    ):
        table = [
            # index = 0: Encode Function table
            {
                int.__name__        :       Codec.__encodeInt,
                bool.__name__       :       Codec.__encodeBool,
                str.__name__        :       Codec.__encodeString,
                list.__name__       :       Codec.__encodeList,
            },
            # index = 1: Decode Function table
            {
                int.__name__        :       Codec.__decodeInt,
                bool.__name__       :       Codec.__decodeBool,
                str.__name__        :       Codec.__decodeString,
            }
        ]

        return table[mode]

    # 인코딩 함수: [b'{name of type}, b'{encoded data}'] 형태로 반환
    @staticmethod
    def __encodeInt(param: int) -> list[bytes]:
        return [type(param).__name__.encode(), param.to_bytes()]
    
    @staticmethod
    def __encodeBool(param: bool) -> list[bytes]:
        return [type(param).__name__.encode(), str(param).encode()]
    
    @staticmethod
    def __encodeString(param: str) -> list[bytes]:
        return [type(param).__name__.encode(), param.encode()]
    
    @staticmethod
    def __encodeList(param: list) -> list[bytes]:
        retValue = []
        for item in param:
            retValue.extend(Codec.__getFunctionTable(Codec.__ENCODE)[type(item).__name__](item))
        
        return retValue
    
    # 디코딩 함수
    @staticmethod
    def __decodeInt(param: bytes) -> int | None:
        try:
            return int.from_bytes(param)
        except TypeError:
            print(f"TypeError: '{param}' is not int type")
            return None
    
    @staticmethod
    def __decodeBool(param: bytes) -> bool | None:
        if param.decode() == str(True):
            return True
        elif param.decode() == str(False):
            return False
        else:
            print(f"TypeError: '{param.decode()}' is not boolean type")
            return None
        
    @staticmethod
    def __decodeString(param: bytes) -> str:
        return param.decode()