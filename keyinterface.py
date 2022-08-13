from machine import I2C

#interfacing directly with the digital hall effect sensor's outputs
class DigitalHallInterface:
    #initialization using a i2c, device address list, info etc.
    def __init__(self, i2c, mp, ch, kpc, cl, kl, br, nk):
        #initialization of some variables describing the structure
        self.i2c = i2c
        self.multiplexers = mp
        self.channels = ch
        self.keysPerChannel = kpc

        #selected device variables
        self.selMP = 0 #which multiplexer is currently selected, just uses mpList for lookup
        self.selCH = 0 #channel number of multiplexer, uses cl for lookup on what to transmit
        self.selK = 0 #which device (key) on the channel, uses kl for lookup on addresses

        #cl and kl
        self.channelList = cl
        self.keyList = kl

        #sensor resolution (bits)
        self.bitResolution = br

        #number of keys (some multiplexers might not have a full set)
        self.numKeys = nk

        #checking for all multiplexers
        self.mpList = self.i2c.scan()
        if len(self.mpList) != self.multiplexers: raise Exception("Incorrect number of multiplexers present!") #count the amount of discovered multiplexers
        self.disableAll()


    #disable ALL multiplexers
    def disableAll(self):
        for mup in self.mpList:
            self.disableMP(mup)

    #disable multiplexer with a certain address by writing 0 (i.e. no channel selection)
    def disableMP(self, address):
        self.i2c.writeTo(address, 0)

    #select which key to read from
    def select(self, m, c, k):
        if m < 0 or m >= self.multiplexers or c < 0 or c >= self.channels or k < 0 or k >= self.keysPerChannel: return #bound check

        if m != self.selMP: #if we switch multiplexers, we have to reselect everything
            #disable old multiplexer, update currently selected one
            self.disableMP(self.mpList[self.selMP])
            self.selMP = m

            #update channel on currently selected multiplexer
            self.i2c.writeTo(self.mpList[self.selMP], self.channelList[c])
            self.selCH = c

            #update selected key (the same addresses on each channel, so no need to communicate with anything)
            self.selK = k
        else: #pretty much the above but no need to disable a multiplexer
            # update channel on currently selected multiplexer
            if c != self.selCH: self.i2c.writeTo(self.mpList[self.selMP], self.channelList[c]) #don't need to change channel if we are still selecting the same
            self.selCH = c

            # update selected key (the same addresses on each channel, so no need to communicate with anything)
            self.selK = k

    #read from currently selected key
    def read(self):
        return self.i2c.readFrom(self.keyList[self.selK], self.bitResolution)

    #write to currently selected key (for settings changes)
    def write(self, data):
        self.i2c.writeto(self.keyList[self.selK], data)

    #select the immediate next key
    def selectNext(self):
        #temp variables
        m = self.selMP
        c = self.selCH
        k = self.selK

        #increment key position
        k += 1

        #rolling over channel position
        if k >= self.keysPerChannel:
            k = 0
            c += 1

        #rolling over multiplexer position
        if c >= self.channels:
            c = 0
            m += 1

        #reaching last possible key
        if m >= self.multiplexers:
            m = 0

        #select with updated values
        self.select(m, c, k)

    #read all key values and return as array
    def readAll(self):
        temp = []

        #insurance, disable everything first
        self.disableAll()

        #start from first key and sequentially read
        self.select(0, 0, 0)
        for i in range(self.numKeys):
            temp.append(self.read())
            self.selectNext()

        #reset to beginning
        self.select(0, 0, 0)

        return temp

    #read a custom group of keys (e.g. WASD)
    def readGroup(self, positions):
        temp = []

        #for each position select then read
        for pos in positions:
            self.select(pos[0], pos[1], pos[2])
            temp.append(self.read())

        #return to beginning
        self.select(0, 0, 0)

        return temp

#for using the max7360 controller
class M7360Interface:
    def __init__(self, i2c, con, ca, kl):
        #i2c instance and num of controllers
        self.i2c = i2c
        self.controllers = con

        #lookups
        self.contAdd = ca
        self.keyList = kl

    def read(self, c): #returns an array with 2 elements: key code and whether it was pressed or released
        if c >= self.controllers or c < 0: return

        data = self.i2c.readFrom(self.contAdd(c), 8)

        em = data&(0b10000000) #leftmost bit is "empty flag"
        re = data&(0b01000000) #second leftmost bit is "release flag"

        key = int(data&(0b00111111)) #the other 6 bits contain the key number (0-63)

        if key == 62 or key == 63: #the special cases are handled by key values 62 and 63
            if not em: #this bit should be on for ALL normal key 62/63 presses
                if re:
                    if key == 63: return [-1, 0] #the overflow condition
                    else: return [-1, 0] #dont understand the register table for this condition
                else:
                    if key == 63: return #return nothing because empty
                    else: return #dont understand the table for this condition
            else:
                return [key, int(re)] #normal operation
        else:
            return [key, int(re)] #normal operation

