#!/usr/bin/env python3

import struct

from .config import *
from . import hid

class WinControls(object):

    _fields = [
        # left stick
        Key(16,'lu'),
        Key(18,'ld'),
        Key(20,'ll'),
        Key(22,'lr'),

        # dpad
        Key(0,'du'),
        Key(2,'dd'),
        Key(4,'dl'),
        Key(6,'dr'),

        # ABXY
        Key(8,'a'),
        Key(10,'b'),
        Key(12,'x'),
        Key(14,'y'),

        # shoulder buttons
        Key(34,'l1'),
        Key(36,'r1'),

        Key(38,'l2'),
        Key(40,'r2'),

        # stick clicks
        Key(24,'l3'),
        Key(26,'r3'),

        # macro keys
        Key(50,'l41'),
        Key(52,'l42'),
        Key(54,'l43'),
        Key(56,'l44'),

        Key(58,'r41'),
        Key(60,'r42'),
        Key(62,'r43'),
        Key(64,'r44'),

        Rumble(66,'rumble'),
        LedMode(68,'ledmode'),
        Colour(69,'colour'),

        # deadzone and centering
        Signed(72,'ldead'),
        Signed(73,'lcent'),
        Signed(74,'rdead'),
        Signed(75,'rcent'),

        # macro delays
        Millis(80,'l4delay1'),
        Millis(82,'l4delay2'),
        Millis(84,'l4delay3'),
        Millis(86,'l4delay4'),
        Millis(88,'r4delay1'),
        Millis(90,'r4delay2'),
        Millis(92,'r4delay3'),
        Millis(94,'r4delay4'),
    ]

    def __init__(self, read=True):
        self.field = {f.name: f for f in self._fields}

        self._openHid()
        self.loaded = False
        if read:
            self.readConfig()

    def _openHid(self):
        for dev in hid.enumerate(vid=0x2f24):
            if dev['usage_page'] == 0xff00:
                #print(dev['path'])
                self.device = hid.Device(path=dev['path'])
                break
        if not self.device:
            raise RuntimeError("Unable to open GPD controller device")

    def _cdata(self, configRaw: bytearray, index):
        return bytes(struct.pack("<H",index)) + configRaw[index<<4:(index+1)<<4]

    def _checksum(self, configRaw: bytearray):
        return sum(configRaw)

    def _parseConfig(self, configRaw: bytearray):
        for field in self._fields:
            field.decode(configRaw)
        self.loaded = True

    def _generateConfig(self):
        if not self.loaded:
            raise RuntimeError("No config loaded")

        configRaw = bytearray(256)
        for field in self._fields:
            field.apply(configRaw)
        return configRaw

    def _parseResponse(self, response):
        info = struct.unpack_from("<8xBBBBB11xII", response)
        return {
            'ready': info[0],
            'firmware': f"X{info[1]:x}{info[2]:02x}K{info[3]:x}{info[4]:02x}",
            'checksum': info[5]
        }

    def _checkDevice(self):
        supported = ['X510K504', 'X408K407']
        info = self._parseResponse(self._response)
        if info['firmware'] not in supported:
            raise RuntimeError(f"Unsupported firmware version: {info['firmware']}")

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
        self.loaded = False

        self._waitReady(0x10)

        configRaw = bytearray()
        for addr in range(4):
            configRaw.extend(self._sendReq(0x11,[addr]))

        self._response = self._sendReq(0x12)
        if self._parseResponse(self._response)['checksum'] == self._checksum(configRaw):
            self._parseConfig(configRaw)
        else:
            raise RuntimeError("Checksum error reading config")

    def writeConfig(self):
        configRaw = self._generateConfig()

        self._waitReady(0x20)

        for block in range(8):
            self._sendReq(0x21,self._cdata(block))

        self._response = self._sendReq(0x22)
        if self._parseResponse(self._response)[3] == self._checksum(configRaw):
            # valid checksum so commit config
            self._sendReq(0x23)
        else:
            raise RuntimeError("Checksum error writing config")

    def setConfig(self, config):
        for line in config.split("\n"):
            if line == "" or line.startswith("#"):
                continue
            if "=" not in line:
                raise RuntimeError("Invalid config line: %s" % line)

            key, value = line.split("=")

            key = key.strip().lower()

            if not key in self.field:
                raise RuntimeError("Invalid config key: %s" % key)

            self.field[key].set(value)

    def dump(self):
        return "\n".join(map(str, self._fields))
