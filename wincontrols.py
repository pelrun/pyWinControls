# %%
import hid
import struct

# %%
class WinControls(object):
    def __init__(self):
        self._openHid()
        self.resetConfig()
        self.readConfig()

    def _openHid(self):
        for dev in hid.enumerate(vid=0x2f24):
            if dev['usage_page'] == 0xff00:
                self.device = hid.Device(path=dev['path'])
                break
        if not self.device:
            raise Exception()

    def _cdata(self,index):
        return bytes(struct.pack("<H",index)) + self._config[index<<4:(index+1)<<4]

    def _checksum(self):
        return sum(self._config)

    def _parse(self, response):
        return struct.unpack_from("<8xBHH11xII", response)

    def _waitReady(self, id):
        self._response = None
        while self._response is None or self._response[8] != 0xaa:
            self._response = self.sendReq(id)

    def resetConfig(self):
        self._config = bytearray()
        self.loaded = False

    def sendReq(self,id,data=None):
        result = bytearray([0x01, 0xa5, id, 0x5a, id^0xFF, 00])

        if (data):
            result.extend(data)
        result.extend(bytearray(33-len(result)))

        self.device.send_feature_report(bytes(result))

        if (id != 0x21 and id != 0x23): # writes don't have replies
            return self.device.get_input_report(1,65)

    def readConfig(self):
        self._waitReady(0x10)

        self.resetConfig()

        for addr in range(4):
            self._config.extend(self.sendReq(0x11,[addr]))

        self._response = self.sendReq(0x12)
        if self._parse(self._response)[3] == self._checksum():
            self.loaded = True

    def writeConfig(self):
        if not self.loaded:
            # Don't write a blank config!
            raise Exception()

        self._waitReady(0x20)

        for block in range(8):
            self.sendReq(0x21,self._cdata(block))

        self._response = self.sendReq(0x22)
        if self._parse(self._response)[3] == self._checksum():
            # valid checksum so commit config
            self.sendReq(0x23)
            return True
        else:
            return False


# %% [markdown]
# Reports:
# 0x10: version check/ready for read
# 0x11: read config memory
# 0x12: get config memory checksum
#
# 0x20: version check/ready for write
# 0x21: write config memory
# 0x22: get checksum
# 0x23: commit config
#
# Notes for reply format (except for responses to 0x11/0x21)
#
# byte at 8 == 0xaa when hardware is ready (keep reading until true)
# uint16's at 10 and 12, fw version numbers. Wincontrols renders as X510K504 (gamepad/keyboard modes?)
#
# uint16 at 24: simple checksum
#

# %%
wc = WinControls()

wc.readConfig()

# %%
for x in range(8):
  print(wc._cdata(x))


