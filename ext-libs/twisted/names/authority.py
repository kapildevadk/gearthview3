# -*- test-case-name: twisted.names.test.test_names -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Authoritative resolvers.
"""

import time
import argparse
import pathlib
import zonefile
import collections
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple
from enum import Enum
from twisted.names import dns, common
from twisted.internet import defer
from twisted.python import failure
from twisted.python.compat import execfile


class RecordType(Enum):
    A = 1
    NS = 2
    MD = 3
    MF = 4
    CNAME = 5
    SOA = 6
    MB = 7
    MG = 8
    MR = 9
    NULL = 10
    WKS = 11
    PTR = 12
    HINFO = 13
    MINFO = 14
    MX = 15
    TXT = 16
    RP = 17
    AFSDB = 18
    X25 = 19
    ISDN = 20
    RT = 21
    NSAP = 22
    NSAPPTR = 23
    SIG = 24
    KEY = 25
    PX = 26
    GPOS = 27
    AAAA = 28
    LOC = 29
    NXT = 30
    EID = 31
    NIMLOC = 32
    SRV = 33
    ATMA = 34
    NAPTR = 35
    KX = 36
    CERT = 37
    A6 = 38
    DNAME = 39
    SINK = 40
    OPT = 41
    APL = 65535


class RecordClass(Enum):
    IN = 1
    CS = 2
    CH = 3
    HS = 4


class RRHeader(NamedTuple):
    name: str
    type: RecordType
    cls: RecordClass
    ttl: int
    payload: dns.RR
    auth: bool


class LookupCacherMixin:
    _cache: Dict[Tuple[str, type, RecordType], defer.Deferred]

    def _lookup(self, name: str, cls: type,
                 type: RecordType, timeout: int = 10) -> defer.Deferred:
        if self._cache is None:
            self._cache = {}
            self._meth = super()._lookup

        cache_key = (name, cls, type)
        if cache_key in self._cache:
            return self._cache[cache_key]
        else:
            r = self._meth(name, cls, type, timeout)
            self._cache[cache_key] = r
            return r


class FileAuthority(LookupCacherMixin, common.ResolverBase):
    """An Authority that is loaded from a file."""

    soa: Optional[Tuple[str, dns.SOA]]
    records: Dict[str, List[dns.RR]]

    def __init__(self, filename: pathlib.Path):
        if not filename.is_file():
            raise FileNotFoundError(f"File '{filename}' not found")

        common.ResolverBase.__init__(self)
        self.loadFile(filename)
        self._cache = {}

    def loadFile(self, filename: pathlib.Path):
        with filename.open() as f:
            zone = zonefile.ZoneFile(f)
            self.records = collections.defaultdict(list)
            for rr in zone:
                if isinstance(rr.rdata, dns.SOA):
                    self.soa = (rr.name, rr.rdata)
                self.records[rr.name.lower()].append(rr)


class PySourceAuthority(FileAuthority):
    """A FileAuthority that is built up from Python source code."""

    def loadFile(self, filename: pathlib.Path):
        g, l = self.setupConfigNamespace(), {}
        execfile(str(filename), g, l)
        if not l.get('zone'):
            raise ValueError("No zone defined in " + str(filename))

        self.records = {}
        for rr in l['zone']:
            if isinstance(rr[1], dns.SOA):
                self.soa = rr
            self.records.setdefault(rr[0].lower(), []).append(rr[1])


    def wrapRecord(self, type: RecordType) -> Callable[[str, Any], Tuple[str, dns.RR]]:
        return lambda name, *arg, **kw: (name, type(*arg, **kw))


    def setupConfigNamespace(self) -> Dict[str, Callable[[int, str, str], None]]:
        r = {}
        items = dns.__dict__.keys()
        for record in [x for x in items if x.startswith('Record_')]:
            type = getattr(dns, record)
            f = self.wrapRecord(type)
            r[record[len('Record_'):]] = f
        return r


class BindAuthority(FileAuthority):
    """An Authority
