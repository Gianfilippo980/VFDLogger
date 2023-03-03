from machine import Pin
from utime import sleep_ms

class orologio :
    griglie= (2, 6, 8, 11, 15)
    segmenti= (3,4,5,7,9,10,12,13,14)
    """
    I segmenti sono:
        14			
    13		12		3
        4
    5		7		9
        10
    """
    #quindi le 10 cifre sono:
    cifre=(0b001101111, 0b100110100, 0b111011101, 0b110111101, 0b110110110, 0b110111011, 0b111111011, 0b100110101, 0b111111111, 0b110111111)

    #inizializzo
    def __init__ (self):
        self.gr=[]
        self.seg=[]
        for i in range(len(self.griglie)):
            self.gr.append(Pin(self.griglie[i], Pin.OUT))
        for i in range(len(self.segmenti)):
            self.seg.append(Pin(self.segmenti[i], Pin.OUT))

    def orario (self, ora):
        #global ora
        #ora è una lista di 5 cifre, quella centrale sono i due punti (0,1)
        for j in range(10):
        #è inutile cambiare l'ora per ogni ciclo, rischia solo di abbassare la luminosità
            for i in range(len(self.griglie)):
                #imposto i segmenti
                cifra=self.cifre[ora[i]]
                for s in range(len(self.segmenti)):
                    self.seg[len(self.segmenti)-(s+1)].value(not((cifra>>s)&1))
                #accendo la griglia i
                self.gr[i].value(0)
                sleep_ms(3)
                self.gr[i].value(1)