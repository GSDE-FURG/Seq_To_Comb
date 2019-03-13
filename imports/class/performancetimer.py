#encoding=utf-8
import datetime
"""---Performance Timer---
Para criar um timer basta iniciar uma instancia.
EX:
    temporizador1 = TIMERN()

seus parametros são:
loops => quantos loops num while o timer fez
average => a média de vários testes em um loop
timespent => tempo percorrido de um evento de começar e um de terminar
save1 => dado como tempo do evento de começar

Utilizar as funções Pstarttimer() e Pstoptimer() para fazer um temporizador simples.
EX:
    temporizador1 = TIMERN()
    temporizador1.Pstarttimer()
    #codigo do programa#
    temporizador1.Pstoptimer()
    print(temporizador1.timespent)

Na tela vai aparecer o tempo que demorou para o código rodar.

Função restarttime() utilizada para reiniciar totalmente a instancia.
Função show_time() mostra o average se tem, se não, mostra timespent.
Para loops, podese usar as funções loopend() e averagetime() para ver o tempo médio de cada loop.
EX:
    temporizador1 = TIMERN()
    a=0
    while a<10000:
        temporizador1.Pstarttimer()
        #codigo do programa#
        temporizador1.Pstoptimer()
        temporizador1.loopend()
        temporizador1.averagetime()
        temporizador1.show_time()

IMPORTANTE ESTAR ASSIM:
        temporizador1.Pstoptimer()
        temporizador1.loopend()
        temporizador1.averagetime()
        
Na tela vai retornar a média do tempo de completar um loop no while.
Por ser uma classe pode criar vários temporizadores differentes ao mesmo tempo.
"""
        
class TIMERN:
    def __init__(self, loops = 0, average = [],timespent = 0,save1 = -1):
        self.loops = 0
        self.average = []
        self.timespent = 0
        self.save1 = -1
    def Pstarttimer(self):
        self.save1 = str(datetime.datetime.now()).split(":")
        try:
            self.save1 = [self.save1[1],self.save1[2].split(".")[0],self.save1[2].split(".")[1]]
        except:
            print(self.save1)
            pass
    def Pstoptimer(self):
        if self.save1 == -1:
            print("Esqueceu Pstarttimer()")
        else:
            self.timespent = str(datetime.datetime.now()).split(":")
            try:
                self.timespent = [self.timespent[1],self.timespent[2].split(".")[0],self.timespent[2].split(".")[1]]
            except:
                print(self.timespent)
                pass
            aa=(int(self.timespent[0])) - (int(self.save1[0]))
            bb=(int(self.timespent[1])) - (int(self.save1[1]))
            cc=(int(self.timespent[2])) - (int(self.save1[2]))
            if cc<0:
                cc = cc + 1000000
                bb = bb - 1
            if bb<0:
                bb = bb + 60
                aa = aa - 1
            if (aa<0 or aa>60):
                print("Programa demorou mais de uma hora ou deu erro.")
            self.timespent = [aa,bb,cc]
            self.save1 = -1
    def restarttime(self):
        self.timespent = 0
        self.average = []
        self.timespent = 0
        self.save1 = -1
    def loopend(self):
        self.loops = self.loops + 1
        if self.loops > 9000000000000000000:
            self.loops = 1
            self.average = []
            #reinicia o calculo de média para nao dar overflow/erro
    def averagetime(self):
        if self.loops == 0 or self.timespent == 0:
            print("Esqueceu alguma coisa...")
        else:
            if len(self.average) <= 1:
                self.average = [int(self.timespent[0]),self.timespent[1],self.timespent[2]]
            else:
                self.average = [(int((int(self.timespent[0]) + (self.average[0] * (self.loops - 1)))/self.loops)),
                                (int((int(self.timespent[1]) + (self.average[1] * (self.loops - 1)))/self.loops)),
                                (int((int(self.timespent[2]) + (self.average[2] * (self.loops - 1)))/self.loops))]
                if self.average[2]>= 1000000:
                    self.average[2] = self.average[2] - 1000000
                    self.average[1] = self.average[1] + 1
                if self.average[1] >= 60:
                    self.average[1] = self.average[1] - 60
                    self.average[0] = self.average[0] + 1
    def show_time(self):
        if len(self.average) <= 1:
            print(str(self.timespent[0]) + " min, " + str(self.timespent[1]) + " seg, " + str(self.timespent[2]) + " microseg.")
        else:
            print(str(self.average[0]) + " min, " + str(self.average[1]) + " seg, " + str(self.average[2]) + " microseg.")
