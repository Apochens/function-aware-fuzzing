"""Seed for FTP"""
from seed.arg import FileDescriptorArg, BooleanArg, StringArg, NumberArg, CallableArg
from seed.fn import Fn
from seed import Seed
from utils import PATH_DUMMY



# Create the dummy file temp.txt
PATH_DUMMY.mkdir(exist_ok=True)
dummy_file = PATH_DUMMY.joinpath('temp.txt')
dummy_file.write_text("Hello")


def __simple_callback(data) -> None:
    return


SEED = Seed([
    Fn('login', [StringArg('webadmin'), StringArg('ubuntu')]),

    Fn("set_pasv", [BooleanArg(False)]),

    Fn("pwd"),
    Fn("mkd", [StringArg("test")]),

    Fn("cwd", [StringArg("test")]),

    Fn("storbinary", [StringArg("STOR temp1.txt"), FileDescriptorArg(dummy_file)]),
    Fn("storbinary", [StringArg("APPE temp1.txt"), FileDescriptorArg(dummy_file)]),

    Fn("storlines", [StringArg("STOR temp2.txt"), FileDescriptorArg(dummy_file)]),
    Fn("storlines", [StringArg("APPE temp2.txt"), FileDescriptorArg(dummy_file)]),

    Fn("rename", [StringArg("temp2.txt"), StringArg("test.txt")]),

    Fn("retrbinary", [StringArg("RETR test.txt"), CallableArg(__simple_callback), NumberArg(8192), NumberArg(0)]),
    Fn("retrbinary", [StringArg("LIST"), CallableArg(__simple_callback)]),
    Fn("retrbinary", [StringArg("NLST"), CallableArg(__simple_callback)]),

    Fn("retrlines", [StringArg("RETR temp1.txt"), CallableArg(__simple_callback)]),
    Fn("retrlines", [StringArg("LIST"), CallableArg(__simple_callback)]),
    Fn("retrlines", [StringArg("NLST"), CallableArg(__simple_callback)]),

    Fn("size", [StringArg("test.txt")]),   # Request the size of the file named filename on the server.
    Fn("dir"),

    Fn("nlst"),
    Fn("mlsd"),

    Fn("delete", [StringArg("temp1.txt")]),
    Fn("delete", [StringArg("test.txt")]),

    Fn("cwd", [StringArg("..")]),
    Fn("rmd", [StringArg("test")]),

    # Fn("abort"]),
    
    # Fn("close"]),
    Fn("quit", is_last=True),
])