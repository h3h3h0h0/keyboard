import mp as mp


class KeyInterface:
    #initialization using a i2c, device address list, info etc.
    def __init__(self, i2c, mp, ch, kpc, cl, kl):
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

        #checking for all devices present
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