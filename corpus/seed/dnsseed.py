"""Seed for DNS"""
from dns.rdatatype import RdataType
from dns.rdataclass import RdataClass


from arg import StringArg, EnumArg


SEED = [
    ["resovle", StringArg("test.com"), EnumArg(RdataType.A), EnumArg(RdataClass.IN)]
]