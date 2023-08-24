"""Seed for SMTP"""
from seed.arg import StringArg


SEED = [
    ["noop"],
    ["help"],

    ["helo"],
    ["ehlo"],

    ["expn", StringArg("ubuntu")],
    ["rset"],

    ["mail", StringArg("ubuntu@ubuntu")],
    ["rcpt", StringArg("ubuntu@ubuntu")],
    ["data", StringArg("hello")],

    ["docmd", StringArg("BDAT")],

    ['quit']
]