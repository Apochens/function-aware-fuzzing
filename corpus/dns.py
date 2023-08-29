"""Seed for DNS"""
from dns.rdatatype import RdataType
from dns.rdataclass import RdataClass


from seed.arg import StringArg, EnumArg
from seed.fn import Fn
from seed import Seed


SEED = Seed([
    Fn("resolve", [StringArg("test.com"), EnumArg(RdataType.A), EnumArg(RdataClass.IN)])
])