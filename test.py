from abc import ABC, abstractmethod

class tmp(ABC):
    @abstractmethod
    def printf(self):
        pass


class rngus(tmp):
    def printf(self, value):
        print(value)

    def printf(self):
        print('b')



rr = rngus()
rr.printf('a')