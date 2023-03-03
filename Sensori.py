#Programma per termometro MCP9808, igrometro AHT10 e barometro BMP280
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

class BMP280 :
    reg_temp=(0xFA, 0xFB, 0xFC) #indirizzo tempratura barometro
    reg_press=(0xF7, 0xF8, 0xF9)#indirizzo pressione barometro
    reg_calib_T=((0x89,0x88),(0x8B,0x8A),(0x8D,0x8C))
    #cosatanti calibrazioen temperatura barometro
    reg_calib_P=((0x8F,0x8E),(0x91,0x90),(0x93,0x92),(0x95,0x94),(0x97,0x96),(0x99,0x98),(0x9B,0x9A),(0x9D,0x9C),(0x9F,0x9E))
    #calibrazione pressione barometro

    def __init__ (self, bus, ind) :
        self.ind=ind
        self.bus=bus
        #Legge le costatni di calibrazione dai registri del barometro
        calib_T=[]
        calib_P=[]
        for i in range(len(self.reg_calib_T)) :
            val=bus.readfrom_mem(self.ind,self.reg_calib_T[i][0],2)
            #val.append(bus.readfrom_mem(self.ind,self.reg_calib_T[i][1],1))
            calib_T.append(int.from_bytes(val,'big'))
        for i in range(len(self.reg_calib_P)) :
            val=bus.readfrom_mem(self.ind,self.reg_calib_P[i][0],2)
            #val[1]=bus.readfrom_mem(self.ind,self.reg_calib_P[i][1],1)
            calib_P.append(int.from_bytes(val, 'big'))
        self.calT=tuple(calib_T)
        self.calP=tuple(calib_P)


    def __misura (self) :
        self.bus.writeto_mem(self.ind, 0xF4, b'0xB5')
        #L'invio di questo byte attiva il sensore
        sleep_ms(100)
        #Occorre aggiornare subito t_fine, usato sia da temperatura che da pressione
        #val=[0,0,0]
        #adcT=0
        #for i in range(len(val)):
        #    val[i]=self.bus.readfrom_mem(self.ind,self.reg_temp[i],1)
        val=self.bus.readfrom_mem(self.ind,self.reg_temp[0],3)
        adcT=int.from_bytes(val, 'big')>>4
        var1=(((adcT>>3)-(self.calT[0]<<1))*self.calT[1])>>11
        var2=(((((adcT>>4)-self.calT[0])*((adcT>>4)-self.calT[0]))>>12)*self.calT[2])>>14
        self.t_fine=var1+var2

    def temperatura (self) :
        #Calcola la temperatura del barometro, con relative correzioni
        self.__misura()
        T=(self.t_fine*5 +128)>>8
        return T/100

    def pressione (self) :
        #Calcola la pressione
        self.__misura()
        #val=[0,0,0]
        #for i in range(len(self.reg_press)) :
        #    val[i]=bus.readfrom_mem(self.ind,self.reg_press[i],1)
        val=self.bus.readfrom_mem(self.ind,self.reg_press[0],3)
        adcP=int.from_bytes(val, 'big')>>4
        var1=self.t_fine-128000
        var2=var1*var1*self.calP[5]
        var2=var2+((var1*self.calP[4])<<17)
        var2=var2+(self.calP[3]<<35)
        var1=((var1*var1*self.calP[2])>>8)+((var1*self.calP[1])<<12)
        var1=(((1<<47)+var1)*self.calP[0])>>33
        if var1==0 :
            return 0
        p=1048576-adcP
        p=(((p<<31)-var2)*3125)//var1
        var1=(self.calP[8]*(p>>13)*(p>>13))>>25
        var2=(self.calP[7]*p)>>19
        p=((p+var1+var2)>>8)+(self.calP[6]<<4)
        return p/25600