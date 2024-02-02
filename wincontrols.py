# %%
import hid
import struct
import json


# %%
class WinControls(object):

    # Somewhat sane default config
    defaults={
        'left': [0x52,0x51,0x50,0x4f],
        'abxy': [0x4,0x5,0x1b,0x1c],
        'dpad': [0x1a,0x16,0x4,0x7],
        'clicks': [0x2c,0x28],
        'l4': [0,0,0,0],
        'l4delay': [0,0,0,300],
        'r4': [0,0,0,0],
        'r4delay': [0,0,0,300],
        'rumble': (2,),
        'leds': [0,0],
        'deadzone_l': [-8,-8],
        'deadzone_r': [-8,-8],
        'shoulder': [0xea,0xeb,0xec,0xed],
    }

    # Parsing information for binary data
    _configStruct = {
        'dpad': ("<HHHH",0),
        'abxy': ("<HHHH",8),
        'left': ("<HHHH",16),
        'clicks': ("<HH",24),
        'shoulder': ("<HHHH",34),
        'l4': ("<HHHH",50),
        'l4delay': ("<HHHH",80),
        'r4': ("<HHHH",58),
        'r4delay': ("<HHHH",88),
        'deadzone_l': ("<bb",72),
        'deadzone_r': ("<bb",74),
        'rumble': ("<H",66),
        'leds': ("<HH",68),
    }

    def __init__(self, read=True):
        self._openHid()
        self.resetConfig()
        if read:
            self.readConfig()

    def resetConfig(self):
        self._configRaw = bytearray(256)
        self.loaded = False

    def _openHid(self):
        for dev in hid.enumerate(vid=0x2f24):
            if dev['usage_page'] == 0xff00:
                #print(dev['path'])
                self.device = hid.Device(path=dev['path'])
                break
        if not self.device:
            raise RuntimeError("Unable to open GPD controller device")

    def _cdata(self,index):
        return bytes(struct.pack("<H",index)) + self._configRaw[index<<4:(index+1)<<4]

    def _checksum(self):
        return sum(self._configRaw)

    def _parseResponse(self, response):
        return struct.unpack_from("<8xBHH11xII", response)

    def _checkDevice(self):
        info = self._parseResponse(self._response)
        if info[1] != 0x1005 or info[2] != 0x0405:
            raise RuntimeError("Only GPD Win Mini X510K504 is currently supported")

    def _waitReady(self, id):
        self._response = None
        while self._response is None or self._response[8] != 0xaa:
            self._response = self._sendReq(id)
        self._checkDevice()

    def _sendReq(self,id,data=None):
        result = bytearray([0x01, 0xa5, id, 0x5a, id^0xFF, 00])

        if (data):
            result.extend(data)
        result.extend(bytearray(33-len(result)))

        self.device.send_feature_report(bytes(result))

        #print("Sent: %s" % result.hex())
        if (id != 0x21 and id != 0x23): # writes don't have replies
            result = self.device.get_input_report(1,65)
            #print("Recv: %s" % result.hex())
            return result

    def readConfig(self):
        self._waitReady(0x10)

        self.resetConfig()

        self._configRaw = bytearray()
        for addr in range(4):
            self._configRaw.extend(self._sendReq(0x11,[addr]))

        self._response = self._sendReq(0x12)
        if self._parseResponse(self._response)[3] == self._checksum():
            self.config = self._parseConfig()
            self.loaded = True
        else:
            raise RuntimeError("Checksum error reading config")

    def writeConfig(self, file=None, generate=False):
        if generate:
            self._genConfig()

        self._waitReady(0x20)

        for block in range(8):
            self._sendReq(0x21,self._cdata(block))

        self._response = self._sendReq(0x22)
        if self._parseResponse(self._response)[3] == self._checksum():
            # valid checksum so commit config
            self._sendReq(0x23)
        else:
            raise RuntimeError("Checksum error writing config")

    def setConfig(self, config):
        for key in config:
            if key in self.config:
                self.config[key] = config[key]
            else:
                raise KeyError("Invalid config key: %s" % key)
        return True

    def _parseConfig(self):
        def _unpack(structEntry):
            format, offset = structEntry
            return struct.unpack_from(format, self._configRaw, offset)

        return dict([(key,_unpack(self._configStruct[key])) for key in self._configStruct])

    def _genConfig(self):
        def _pack(structEntry, value):
            format, offset = structEntry
            struct.pack_into(format, self._configRaw, offset, *value)

        for key in self._configStruct:
            _pack(self._configStruct[key], self.config[key])



# %%
if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option("-s","--set",help="Read config from FILE",metavar="FILE")
    parser.add_option("-d","--dump",help="Dump config to FILE", metavar="FILE")
    parser.add_option("-r","--reset",action="store_true",help="Reset to defaults")

    (options,args)=parser.parse_args()

    wc = WinControls()

    if options.reset:
        wc.setConfig(wc.defaults)
        wc.writeConfig(generate=True)

    if wc.loaded and options.dump:
        with open(options.dump,"w") as wf:
            json.dump(wc.config,wf,indent=4)
    
    if options.set:
        with open(options.set, 'r') as f:
            newconfig = json.load(f)
        if wc.setConfig(newconfig):
            wc.writeConfig(generate=True)

    if not options.reset and not options.dump and not options.set:
        print(json.dumps(wc.config, indent=4))
