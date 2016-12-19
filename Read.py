#!/usr/bin/env python
# -*- coding: utf8 -*-


import MFRC522
import signal

continue_reading = True
SECTORS_TOREAD = 8
sector_now = 0

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    exit()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQA)

        
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        # Print UID
        #print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
    
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, sector_now, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            data = MIFAREReader.MFRC522_Read(sector_now)
            #print data
            print "Sector["+str(data[0])+"]" + ''.join([str(chr(x)) for x in data[1]])
            MIFAREReader.MFRC522_StopCrypto1()
            sector_now+=1
        else:
            print "Authentication error"
    
    if sector_now > SECTORS_TOREAD:
        sector_now=0