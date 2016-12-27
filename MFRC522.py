#!/usr/bin/env python
# -*- coding: utf8 -*-

import serial
import signal
import time
import sys

class MFRC522:
  NRSTPD = 22
  
  MAX_LEN = 16
  
  PCD_IDLE       = 0x00
  PCD_MEM        = 0x01
  PCD_RNDID      = 0x02
  PCD_CALCCRC    = 0x03
  PCD_TRANSMIT   = 0x04
  PCD_AUTHENT    = 0x0E
  PCD_RECEIVE    = 0x08
  PCD_TRANSCEIVE = 0x0C
  PCD_RESETPHASE = 0x0F
 
  
  PICC_REQA      = 0x26
  PICC_WUPA      = 0x52
  PICC_ANTICOLL  = 0x93
  PICC_SElECTTAG = 0x93
  PICC_AUTHENT1A = 0x60
  PICC_AUTHENT1B = 0x61
  PICC_READ      = 0x30
  PICC_WRITE     = 0xA0
  PICC_DECREMENT = 0xC0
  PICC_INCREMENT = 0xC1
  PICC_RESTORE   = 0xC2
  PICC_TRANSFER  = 0xB0
  PICC_HALT      = 0x50
  
  MI_OK       = 0
  MI_NOTAGERR = 1
  MI_ERR      = 2
  

  CommandReg     = 0x01
  CommIEnReg     = 0x02
  DivlEnReg      = 0x03
  CommIrqReg     = 0x04
  DivIrqReg      = 0x05
  ErrorReg       = 0x06
  Status1Reg     = 0x07
  Status2Reg     = 0x08
  FIFODataReg    = 0x09
  FIFOLevelReg   = 0x0A
  WaterLevelReg  = 0x0B
  ControlReg     = 0x0C
  BitFramingReg  = 0x0D
  CollReg        = 0x0E
    
  ModeReg        = 0x11
  TxModeReg      = 0x12
  RxModeReg      = 0x13
  TxControlReg   = 0x14
  TxASKReg       = 0x15
  TxSelReg       = 0x16
  RxSelReg       = 0x17
  RxThresholdReg = 0x18
  DemodReg       = 0x19

  MifareTxReg    = 0x1C
  MifarerxReg    = 0x1D

  SerialSpeedReg = 0x1F

  CRCResultRegM     = 0x21
  CRCResultRegL     = 0x22

  ModWidthReg       = 0x24

  RFCfgReg          = 0x26
  GsNReg            = 0x27
  CWGsPReg          = 0x28
  ModGsPReg         = 0x29
  TModeReg          = 0x2A
  TPrescalerReg     = 0x2B
  TReloadRegH       = 0x2C
  TReloadRegL       = 0x2D
  TCounterValueRegH = 0x2E
  TCounterValueRegL = 0x2F
  
  TestSel1Reg     = 0x31
  TestSel2Reg     = 0x32
  TestPinEnReg    = 0x33
  TestPinValueReg = 0x34
  TestBusReg      = 0x35
  AutoTestReg     = 0x36
  VersionReg      = 0x37
  AnalogTestReg   = 0x38
  TestDAC1Reg     = 0x39
  TestDAC2Reg     = 0x3A
  TestADCReg      = 0x3B

    
  serNum = []
  
  def __init__(self, dev='/dev/ttyUSB0'):
    self.ser = serial.Serial(port=dev,baudrate=9600)
    self.reset(spd=1);  
    #self.performSelfTest() 
    self.writeRegister(self.TModeReg, 0x80)
    self.writeRegister(self.TPrescalerReg, 0xA9)
    self.writeRegister(self.TReloadRegH, 0x03)
    self.writeRegister(self.TReloadRegL, 0xE8)  
    self.writeRegister(self.TxASKReg, 0x40)
    self.writeRegister(self.ModeReg, 0x3D)
    self.writeRegister(self.TestPinEnReg, 0x00)
    self.antennaOn()
  
  def reset(self, spd=None):
    if not self.writeRegister(self.CommandReg, self.PCD_RESETPHASE):
      self.ser.baudrate=1228800
      self.writeRegister(self.CommandReg, self.PCD_RESETPHASE)
      self.ser.baudrate=9600
      time.sleep(0.05)
    self.writeRegister(self.SerialSpeedReg, 0x15)
    self.ser.baudrate=1228800 



  def writeRegister(self, addr, val, size=None):
    if size is None:
      count = 0
      while True:
        self.ser.flushInput()
        self.ser.write(chr(addr&0x7F))
        self.ser.write(chr(val))
        tmp = ord(self.ser.read(1))   
        if(tmp == addr):      
          return True
        count+=1
        if(count > 10):
          print ("Error de escritura en: "+ hex(addr))
          return False  
    else:       
      self.ser.flushInput()
      for txBytes in range (0, size):
        self.ser.write(chr(addr&0x7F))
        tmp = ord(self.ser.read(1))
        if(tmp == addr):
          self.ser.write(chr(val[txBytes]))
        else:
          print ("Error de escritura en bloque")
          return False
          
      return True    

  def readRegister(self, addr):
    self.ser.flushInput()
    self.ser.write(chr(addr|0x80))
    val = self.ser.read(1)
    return ord(val)

  
  def setBitMask(self, reg, mask):
    tmp = self.readRegister(reg)
    self.writeRegister(reg, tmp | mask)
    
  def clearBitMask(self, reg, mask):
    tmp = self.readRegister(reg);
    self.writeRegister(reg, tmp & (~mask))
  
  def antennaOn(self):
    temp = self.readRegister(self.TxControlReg)
    if(~(temp & 0x03)):
      self.setBitMask(self.TxControlReg, 0x03)
  
  def antennaOff(self):
    self.clearBitMask(self.TxControlReg, 0x03)

  def getAntennaGain(self):
    return self.readRegister((self.RFCfgReg) & (0x07<<4))

  def setAntennaGain(self, mask):
    if (self.GetAntennaGain() != mask): 						
      self.ClearRegisterBitMask(self.RFCfgReg, (0x07<<4))		
      self.SetRegisterBitMask(self.RFCfgReg, mask & (0x07<<4))
	
  
  def MFRC522_ToCard(self,command,sendData):
    backData = []
    backLen = 0
    status = self.MI_ERR
    irqEn = 0x00
    waitIRq = 0x00
    lastBits = None
    n = 0
    i = 0
    
    if command == self.PCD_AUTHENT:
      irqEn = 0x12
      waitIRq = 0x10
    if command == self.PCD_TRANSCEIVE:
      irqEn = 0x77
      waitIRq = 0x30
    
    self.writeRegister(self.CommIEnReg, irqEn|0x80)
    self.clearBitMask(self.CommIrqReg, 0x80)
    self.setBitMask(self.FIFOLevelReg, 0x80)
    
    self.writeRegister(self.CommandReg, self.PCD_IDLE);  
    
    while(i<len(sendData)):
      self.writeRegister(self.FIFODataReg, sendData[i])
      i = i+1
    
    self.writeRegister(self.CommandReg, command)
      
    if command == self.PCD_TRANSCEIVE:
      self.setBitMask(self.BitFramingReg, 0x80)
    
    i = 100
    while True:
      n = self.readRegister(self.CommIrqReg)
      i = i - 1
      if ~((i!=0) and ~(n&0x01) and ~(n&waitIRq)):
        break
    
    self.clearBitMask(self.BitFramingReg, 0x80)
  
    if i != 0:
      if (self.readRegister(self.ErrorReg) & 0x1B)==0x00:
        status = self.MI_OK

        if n & irqEn & 0x01:
          status = self.MI_NOTAGERR
      
        if command == self.PCD_TRANSCEIVE:
          n = self.readRegister(self.FIFOLevelReg)
          lastBits = self.readRegister(self.ControlReg) & 0x07
          if lastBits != 0:
            backLen = (n-1)*8 + lastBits
          else:
            backLen = n*8
          
          if n == 0:
            n = 1
          if n > self.MAX_LEN:
            n = self.MAX_LEN
    
          i = 0
          while i<n:
            backData.append(self.readRegister(self.FIFODataReg))
            i = i + 1;
      else:
        status = self.MI_ERR

    return (status,backData,backLen)
  
  
  def MFRC522_Request(self, reqMode):
    status = None
    backBits = None
    TagType = []
    
    self.writeRegister(self.BitFramingReg, 0x07)
    
    TagType.append(reqMode);
    (status,backData,backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, TagType)
  
    if ((status != self.MI_OK) | (backBits != 0x10)):
      status = self.MI_ERR
      
    return (status,backBits)
  
  
  def MFRC522_Anticoll(self):
    backData = []
    serNumCheck = 0
    
    serNum = []
  
    self.writeRegister(self.BitFramingReg, 0x00)
    
    serNum.append(self.PICC_ANTICOLL)
    serNum.append(0x20)
    
    (status,backData,backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE,serNum)
    
    if(status == self.MI_OK):
      i = 0
      if len(backData)==5:
        while i<4:
          serNumCheck = serNumCheck ^ backData[i]
          i = i + 1
        if serNumCheck != backData[i]:
          status = self.MI_ERR
      else:
        status = self.MI_ERR
  
    return (status,backData)
  
  def CalulateCRC(self, pIndata):
    self.clearBitMask(self.DivIrqReg, 0x04)
    self.setBitMask(self.FIFOLevelReg, 0x80);
    i = 0
    while i<len(pIndata):
      self.writeRegister(self.FIFODataReg, pIndata[i])
      i = i + 1
    self.writeRegister(self.CommandReg, self.PCD_CALCCRC)
    i = 0xFF
    while True:
      n = self.readRegister(self.DivIrqReg)
      i = i - 1
      if not ((i != 0) and not (n&0x04)):
        break
    self.writeRegister(self.CommandReg, self.PCD_IDLE)
    pOutData = []
    pOutData.append(self.readRegister(self.CRCResultRegL))
    pOutData.append(self.readRegister(self.CRCResultRegM))
    return pOutData
  
  def MFRC522_SelectTag(self, serNum):
    backData = []
    buf = []
    buf.append(self.PICC_SElECTTAG)
    buf.append(0x70)
    i = 0
    while i<5:
      buf.append(serNum[i])
      i = i + 1
    pOut = self.CalulateCRC(buf)
    buf.append(pOut[0])
    buf.append(pOut[1])
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buf)
    
    if (status == self.MI_OK) and (backLen == 0x18):
      #print ("Size: " + str(backData[0]))
      return    backData[0]
    else:
      return 0
  
  def MFRC522_Auth(self, authMode, BlockAddr, Sectorkey, serNum):
    buff = []

    # First byte should be the authMode (A or B)
    buff.append(authMode)

    # Second byte is the trailerBlock (usually 7)
    buff.append(BlockAddr)

    # Now we need to append the authKey which usually is 6 bytes of 0xFF
    i = 0
    while(i < len(Sectorkey)):
      buff.append(Sectorkey[i])
      i = i + 1
    i = 0

    # Next we append the first 4 bytes of the UID
    while(i < 4):
      buff.append(serNum[i])
      i = i +1

    # Now we start the authentication itself
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_AUTHENT,buff)

    # Check if an error occurred
    if not(status == self.MI_OK):
      print ("AUTH ERROR!!")
    if not (self.readRegister(self.Status2Reg) & 0x08) != 0:
      print ("AUTH ERROR(status2reg & 0x08) != 0")

    # Return the status
    return status
  
  def MFRC522_StopCrypto1(self):
    self.clearBitMask(self.Status2Reg, 0x08)

  def MFRC522_Read(self, blockAddr):
    recvData = []
    recvData.append(self.PICC_READ)
    recvData.append(blockAddr)
    pOut = self.CalulateCRC(recvData)
    recvData.append(pOut[0])
    recvData.append(pOut[1])
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, recvData)
    if not(status == self.MI_OK):
      print ("Error while reading!")
    i = 0
    if len(backData) == 16:
      msg = {}
      msg[0] = blockAddr
      msg[1] = backData
      return msg
  
  def MFRC522_Write(self, blockAddr, writeData):
    buff = []
    buff.append(self.PICC_WRITE)
    buff.append(blockAddr)
    crc = self.CalulateCRC(buff)
    buff.append(crc[0])
    buff.append(crc[1])
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buff)
    if not(status == self.MI_OK) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
        status = self.MI_ERR
    
    print (str(backLen)+" backdata &0x0F == 0x0A "+str(backData[0]&0x0F))
    if status == self.MI_OK:
        i = 0
        buf = []
        while i < 16:
            buf.append(writeData[i])
            i = i + 1
        crc = self.CalulateCRC(buf)
        buf.append(crc[0])
        buf.append(crc[1])
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE,buf)
        if not(status == self.MI_OK) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
            print ("Error while writing")
        if status == self.MI_OK:
            print ("Data written")

  def MFRC522_DumpClassic1K(self, key, uid):
    i = 0
    while i < 64:
        status = self.MFRC522_Auth(self.PICC_AUTHENT1A, i, key, uid)
        # Check if authenticated
        if status == self.MI_OK:
            self.MFRC522_Read(i)
        else:
            print ("Authentication error")
        i = i+1



