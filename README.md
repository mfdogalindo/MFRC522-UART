MFRC522-python
==============

A small class to interface with the NFC reader Module MFRC522 through UART

## Pins


| RC522| Device | 
|------|--------|
| SDA  |  TX  	| 
| MISO |  RX  	| 
| 3.3V |  3.3V 	| 
| GND  |  GND 	|

## Rework

If you have a chinese RC522 board, cut 3.3V wire to pin 32 and populate to GND

![alt tag](https://github.com/manuelgalindo/MFRC522-UART/raw/master/wiring.jpg)


##Usage
Import the class by importing MFRC522 in the top of your script. For more info see the examples.

##Thanks To
|--------------|------------------------------------------|
|Miguel Balboa | https://github.com/miguelbalboa/rfid     |
|MXGXW         | https://github.com/mxgxw/MFRC522-python  |
