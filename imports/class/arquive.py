#encoding=utf-8
class Arquive:
    def __init__(self, file):
        self.__file = file
        
    def load(self):
        arq = open(self.__file, 'r+')
        string = arq.read()
        arq.close()
        return string
        
    def save(self, string):
        arq = open(self.__file, 'w+')
        arq.write(string)
        arq.close()
        
    def append(self, string):
        arq = open(self.__file, 'a+')
        arq.write(string)
        arq.close()