from enum import Enum

class Commands(Enum):
    run = b'run'
    stop = b'stop'

    def values() -> list[bytes]:
        return [command.value for command in list(Commands)]