from enum import Enum
import traceback
from typing import Callable


class Codec:
    @staticmethod
    def encode(param) -> list[bytes] | bool:
        try:
            return Codec.__getFunctionTable()[type(param).__name__](param)
        except KeyError:
            traceback.print_exc()
            print(f"EncodingError: '{type(param).__name__}' 형식은 부호화를 지원하지 않습니다.")
    

    @staticmethod
    def decode(param: list[bytes]) -> list[str]:
         return [part.decode() for part in param]
    

    # private method
    @staticmethod
    def __getFunctionTable() -> (
        Callable[[int], list[bytes]] | 
        Callable[[list[bytes]]]
    ):
        return {
            int.__name__        :       Codec.__encodeInt,
            bool.__name__       :       Codec.__encodeBool,
            str.__name__        :       Codec.__encodeString,
            list.__name__       :       Codec.__encodeList,
        }

    ## encode
    @staticmethod
    def __encodeInt(param: int) -> list[bytes]:
        return [type(param).__name__.encode(), param.to_bytes()]      # [b'자료형', b'값']의 형태로 반환
    
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
            retValue.extend(Codec.__getFunctionTable()[type(item).__name__](item))
        
        return retValue
    
    ## decode
    @staticmethod
    def __decodeInt(param: )
         

    @staticmethod
    def test(param: list) -> list[bytes]:
        Codec.__encodeList(param)
    

    

