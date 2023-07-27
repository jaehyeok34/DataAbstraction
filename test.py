class tmp:
    def __init__(self, data) -> None:
        self.__data = data

    @property
    def data(self):
        return self.data
    
    @data.setter
    def data(self, data):
        if data > 10:
            self.data = data
            print('입력')


tmp(11)