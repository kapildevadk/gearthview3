# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""Test cases for the NMEA GPS protocol"""

import StringIO
from unittest.mock import Mock
from itertools import zip_longest

import twisted.trial
from twisted.trial import unittest
from twisted.internet import reactor, protocol
from twisted.python import reflect

from twisted.protocols.gps import nmea

class StringIOWithNoClose(StringIO.StringIO):
    def close(self):
        pass

class ResultHarvester:
    def __init__(self):
        self.results = []

    def __call__(self, *args):
        self.results.append(args)

    def performTest(self, function, *args, **kwargs):
        l = len(self.results)
        try:
            function(*args, **kwargs)
        except Exception as e:
            self.results.append(e)
        if l == len(self.results):
            self.results.append(NotImplementedError())

class NMEATester(nmea.NMEAReceiver):
    ignore_invalid_sentence: int = 0
    ignore_checksum_mismatch: int = 0
    ignore_unknown_sentencetypes: int = 0
    convert_dates_before_y2k: bool = True

    def connectionMade(self):
        self.result_harvester = ResultHarvester()
        for fn in reflect.prefixedMethodNames(self.__class__, 'decode_'):
            setattr(self, 'handle_' + fn, self.result_harvester)

class NMEAReceiverTestCase(unittest.TestCase):
    messages: list = [
        # fix - signal acquired
        "$GPGGA,231713.0,3910.413,N,07641.994,W,1,05,1.35,00044,M,-033,M,,*69",
        # fix - signal not acquired
        "$GPGGA,235947.000,0000.0000,N,00000.0000,E,0,00,0.0,0.0,M,,,,0000*00",
        # junk
        "lkjasdfkl!@#(*$!@(*#(ASDkfjasdfLMASDCVKAW!@#($)!(@#)(*",
        # fix - signal acquired (invalid checksum)
        "$GPGGA,231713.0,3910.413,N,07641.994,W,1,05,1.35,00044,M,-033,M,,*68",
        # invalid sentence
        "$GPGGX,231713.0,3910.413,N,07641.994,W,1,05,1.35,00044,M,-033,M,,*68",
        # position acquired
        "$GPGLL,4250.5589,S,14718.5084,E,092204.999,A*2D",
        # position not acquired
        "$GPGLL,0000.0000,N,00000.0000,E,235947.000,V*2D",
        # active satellites (no fix)
        "$GPGSA,A,1,,,,,,,,,,,,,0.0,0.0,0.0*30",
        # active satellites
        "$GPGSA,A,3,01,20,19,13,,,,,,,,,40.4,24.4,32.2*0A",
        # positiontime (no fix)
        "$GPRMC,235947.000,V,0000.0000,N,00000.0000,E,,,041299,,*1D",
        # positiontime
        "$GPRMC,092204.999,A,4250.5589,S,14718.5084,E,0.00,89.68,211200,,*25",
        # course over ground (no fix - not implemented)
        "$GPVTG,,T,,M,,N,,K*4E",
        # course over ground (not implemented)
        "$GPVTG,89.68,T,,M,0.00,N,0.0,K*5F",
    ]
    results: list = [
        (83833.0, 39.17355, -76.6999, nmea.POSFIX_SPS, 5, 1.35, (44.0, 'M'), (-33.0, 'M'), None),
        (86387.0, 0.0, 0.0, 0, 0, 0.0, (0.0, 'M'), None, None),
        nmea.InvalidSentence(),
        nmea.InvalidChecksum(),
        nmea.InvalidSentence(),
        (-42.842648333333337, 147.30847333333332, 3
