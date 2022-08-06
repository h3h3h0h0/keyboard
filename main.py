from machine import I2C
from keyinterface import KeyInterface

#layout
deviceNum = 4 #4 8-channel multiplexers each driving 32 keys (4 addresses per pin)
channelNum = 8 #8 channel multiplexers
keysPerChannel = 4 #4 individual key addresses per channel

numKeys = 104 #standard full-size keyboard

#address lookups
channelList = []
keyList = []

#resolution of sensors
resolution = 0

#create I2C in fast mode
i2c = I2C(freq=400000)

#initialize the actual interface
KI = KeyInterface(i2c, deviceNum, channelNum, keysPerChannel, channelList, keyList, numKeys)

