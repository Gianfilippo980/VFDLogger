import machine
import _thread
import micropyGPS
import Orologio
import Sensori
import ahtx0
import time
import sdcard
import uos
import bmp280
from sys import stdout

ind_term=0x18			#indirizzo termometro
ind_bar=0x76			#indirizzo del barometro
ind_igro=0x38			#indirizzo igrometro
periodo=1				#Minuti di attesa fra le misurazioni
fuso_orario=1			#ore di differenza dall'UTC
uart0=machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))
i2c0=machine.I2C(0, scl=machine.Pin(21), sda=machine.Pin(20))
gps=micropyGPS.MicropyGPS(fuso_orario)
Display_ora=Orologio.orologio()
termometro=Sensori.MCP9808(i2c0, ind_term)
barometro=bmp280.BMP280(i2c0, ind_bar, 5)
#Il caso d'uso (terza varaibile) '5' corrisponde all'uso per la navogazione indoor (descritto nel datasheet, cui compete la massima risoluzione, e un filtraggio dei dati (il sensore effettua una media)
igrometro= ahtx0.AHT10(i2c0)
led_pico=machine.Pin(25, machine.Pin.OUT)
rtc=machine.RTC()

spi = machine.SPI(0, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB, sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(16))
cs = machine.Pin(17, machine.Pin.OUT)    

class Futaba:
    #Display VFD per i dati
    sleep=100
    def __init__ (self, uart):
        self.uart=uart
        self.prec="Giacinto Boccia 2023"
        self.uart.write(bytes([17]))
        #questo coamndo disabilita lo scorrimento
        time.sleep_ms(self.sleep)
        self.uart.write(bytes([20]))
        #questo comando nasconde il cursore
    def scrivi (self,nuovo):
        #voglio una stringa di 20 caratteri o meno
        for i in range(20-len(nuovo)):
            #aggiungo spazi per arrivare a 20
            if i%2==0:
                nuovo=" "+nuovo
            else:
                nuovo=nuovo+" "
        self.uart.write(bytes([13]))
        #questo coamndo riporta ad inizio riga
        time.sleep_ms(self.sleep)
        self.uart.write(self.prec)
        time.sleep_ms(self.sleep)
        self.uart.write(nuovo)
        self.prec=nuovo
        
def aggiungi_un_giorno(giorno, mese, anno):
    # definisci un dizionario con i giorni di ogni mese
    giorni_per_mese = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30,10:31 ,11:30 ,12:31}
    # controlla se l'anno ?? bisestile e aggiorna il dizionario
    if anno %4 ==0 and (anno %100 !=0 or anno %400 ==0):
        giorni_per_mese[2] =29
    # incrementa il giorno
    giorno +=1
    # controlla se il giorno supera i giorni del mese
    if giorno > giorni_per_mese[mese]:
        # azzera il giorno e incrementa il mese
        giorno =1
        mese +=1
        # controlla se il mese supera i mesi dell'anno
        if mese >12:
            # azzera il mese e incrementa l'anno
            mese =1
            anno +=1
    # restituisci la nuova data come una tupla
    return (anno,mese ,giorno)

#s=nmea.read()
#for c in s:
#    gps.update(c)
    #cos?? ho dato al decodificatore GPS una finta posizione e lui fa partire il tempo anche se non prende.

def mostra_ora ():
    while True:
        stamp=time.localtime()
        ora=[stamp[3]//10, stamp[3]%10, 1, stamp[4]//10, stamp[4]%10]
        Display_ora.orario(ora)
_thread.start_new_thread(mostra_ora, ())
#questa va in esecuzione nel secondo core

display=Futaba(uart0)
try:
    sd = sdcard.SDCard(spi, cs)
    vfs = uos.VfsFat(sd)
    uos.mount(vfs, "/sd")
except:
    display.scrivi("ERRORE SD!")
 
while True:
    led_pico.on()
    t_misura=time.time()
    temp=termometro.temperatura()
    press=barometro.pressure/100
    umidit??=igrometro.relative_humidity
    if press<1000:
        p_str=str(round(press))+" | "
    else:
        p_str=str(round(press))+"| "
        #se la pressione ?? pi?? di 1000, devo usare uno spazio in meno per essere entro i 30 caratteri nel caso in cui l'umidit?? sia il 100%
    riga=str(round(temp,2))+" | "+p_str+str(round(umidit??,2))
    #print(riga)
    display.scrivi(riga)    
    try:
        s=uart0.read().decode()
    except:
            s=""
    else:
        try:
            #al ricostruzione della data e ora ?? tutta un tentaivo
            for c in s:
                gps.update(c)
            ora=gps.timestamp
            #se non ha ricostruito alcun dato, il GPS restituisce 0-0-0, che causa un erroe nella funzione per il calcolo della data
            if ora[0]<fuso_orario :
                data=aggiungi_un_giorno(gps.date[0], gps.date[1], gps.date[2])
            else:
                data=gps.date
        except:
            s=""
        else:
            data_ora=(2000+data[2], data[1], data[0],0,ora[0], ora[1], int(ora[2]),0)
            #print(data_ora)
            try:
                rtc.datetime(data_ora)
            except:
                s=""
    stamp=time.localtime(t_misura)
    nome_file="/sd/"+str(stamp[2])+"-"+str(stamp[1])+"-"+str(stamp[0])+".csv"
    try:
        open(nome_file, "r")
        #verifico se il file esiste
    except:
        try:
            with open(nome_file, "a") as file:
                file.write("Anno; Mese; Giorno; Ora; Minuto; Secondo; Temperatura (??C); Pressione (hPa); Umidit?? Relativa (%)\r\n")
                #se il file non esiste ci scrivo una bella intestazione
        except:
            display.scrivi("ERRORE SD!")
    log=str(stamp[0])+"; "+str(stamp[1])+"; "+str(stamp[2])+"; "+str(stamp[3])+"; "+str(stamp[4])+"; "+str(stamp[5])+"; "+str(temp)+"; "+str(press)+"; "+str(umidit??)
    try:
        with open(nome_file, "a") as file:
            file.write(log+"\r\n")
            #adesso scrivo il log nel file
    except:
        display.scrivi("ERRORE SD!")
        display.scrivi(riga)
        #se ho problemi con la SD voglio che appaia la scritta ma comunque una delle due righe deve contenere i dati
    print(log)
    #il log viene inviato trmite seriale
    led_pico.off()
    time.sleep(periodo*60)