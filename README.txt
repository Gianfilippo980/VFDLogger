LOGGER DEI PARAMETRI AMBIENTALI

Pregasi svuotare periodicamente questa microSD: il dispositivo NON è in grado di cancellare i file se la scheda è piena. Comunque dovrebbero occorrere anni perché ciò avvenga.

Anche se non ho misurato un assorbimento di più di 0,5 A, è possibile che ci siano dei picchi imprevisti. Raccomando di alimentare con un alimentatore a 5 V da 1 A o più (standard USB).
È possibile avere alimentazione contemporaneamente dalla porta di alimentazione e da quella del microcnontrollore: un diodo Schottky fa sì che solo una delle due alimentazioni venga utilizzata.

La misura avviene ogni minuto (variabile "peiodo" del "main").
Sensori:	Nomi:		Accuratezze:
- Barometro 	BMP280		±1 hPa
- Termometro	MCP9808		±0.5 °C (typ. ±0.25 °C)
- Igromtro 	AHT10		±3 % (typ. ±2 %)

Anche se gli altri due sensori sono equipaggiati con un termometro, la Bosh raccomanda di considerare la sua misura solo per calibrare l'a lettura del barometro, perché influenzata dal riscaldamento del sensore stesso. E ho preferito utilizzare il termometro della Microchip perché l'AHT10 è un sensore di marca meno pregiata.

L'apparato si sincronizza automaticamente con il GPS (se prende) ed è impostato per il fuso orario UTC+1. Se il segnale del GPS dovesse essere intermittente, è possibile che il tempo ambbia un ritardo, non superiore al periodo di interrogazione dei sensori (che coincide con il periodo di lettura dei dati dal GPS).

Si possono ricevere i log in tempo reale anche collegando un computer alla porta micro-USB tipo B che si trova sul microcontrollore, si vede una porta seriale (COMx) a cui ci si puù connettere con un emulatore di terminale (come HTerm), oltre a selezionare la porta, si deve impostare il Baud a 115200, 8 bit, 1 stop, no parità ed è necessario ATTIVARE IL DTR. Il dispositivo non invierà segnali se non riceve il segnale DTR. Il formato dei log è:

Anno; Mese; Giorno; Ora; Minuto; Secondo; Temperatura (°C); Pressione (hPa); Unidità Relativa (%)  

02/03/2023		Giacinto Boccia