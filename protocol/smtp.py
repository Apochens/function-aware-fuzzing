"""Seed for SMTP"""
from seed.arg import StringArg
from seed.fn import Fn
from seed import Seed

SEED = Seed([
    Fn("noop"),
    Fn("help"),

    Fn("helo"),
    Fn("ehlo"),

    Fn("expn", [StringArg("ubuntu")]),
    Fn("rset"),

    Fn("mail", [StringArg("ubuntu@ubuntu")]),
    Fn("rcpt", [StringArg("ubuntu@ubuntu")]),
    Fn("data", [StringArg("hello")]),

    Fn("docmd", [StringArg("BDAT")]),

    Fn('quit', is_last=True)
])