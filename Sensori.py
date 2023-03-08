#Programma per termometro MCP9808
from utime import sleep_ms

class MCP9808 :
    reg_temp=0x05#indirizzo registro temperatura
    def __init__ (self, bus, ind) :
        self.bus=bus
        self.ind=ind
    def temperatura(self):
        lettura=self.bus.readfrom_mem (self.ind, self.reg_temp, 2)
        msb=lettura[0] & 0x1F
        #le flag occupano i primi 3 bit del primo byte, non mi interessano, per cui uso msb in cui scrivo gli altri 5 bit
        if (msb & 0x10) == 0x10 :
            #Temperatura minore di 0, aggiungo 256 perché il bit di segno viene interpretato come -(256+t)
            temperatura= 256 - (msb*16 + lettura[1]/16)
        else :
            temperatura= (msb*16 + lettura[1]/16)
        return temperatura
