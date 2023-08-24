"""Seed for DNS"""
from dns.rdatatype import RdataType
from dns.rdataclass import RdataClass


from corpus.arg import StringArg, EnumArg


SEED = [
    ["resolve", StringArg("test.com"), EnumArg(RdataType.A), EnumArg(RdataClass.IN)]
]