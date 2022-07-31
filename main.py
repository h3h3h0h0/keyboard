from machine import I2C

#some reference values
deviceNum = 4 #4 8-channel multiplexers each driving 32 keys (4 addresses per pin)
channelNum = 8 #8 channel multiplexers
keysPerChannel = 4 #4 individual key addresses per channel

#create I2C in fast mode
#scans for multiplexers controlling the key sensors
i2c = I2C(freq=400000)

#main loop (the while condition will be changed later)
while True:
    #read each multiplexer
    for device in deviceList:

