"""Seed for FTP"""
from pathlib import Path
from arg import FileDescriptorArg, BooleanArg, StringArg, NumberArg, CallableArg


# Create the dummy file temp.txt
dummy_file = Path("./dummy/temp.txt")
dummy_file.parent.mkdir(exist_ok=True)
dummy_file.write_text("Hello")


def __simple_callback(data) -> None:
    return


SEED = [
    ['login', StringArg('webadmin'), StringArg('ubuntu')],

    ["set_pasv", BooleanArg(False)],

    ["pwd"],
    ["mkd", StringArg("test")],

    ["cwd", StringArg("test")],

    ["storbinary", StringArg("STOR temp1.txt"), FileDescriptorArg("./dummy/temp.txt")],
    ["storbinary", StringArg("APPE temp1.txt"), FileDescriptorArg("./dummy/temp.txt")],

    ["storlines", StringArg("STOR temp2.txt"), FileDescriptorArg("./dummy/temp.txt")],
    ["storlines", StringArg("APPE temp2.txt"), FileDescriptorArg("./dummy/temp.txt")],

    ["rename", StringArg("temp2.txt"), StringArg("test.txt")],

    ["retrbinary", StringArg("RETR test.txt"), CallableArg(__simple_callback), NumberArg(8192), NumberArg(0)],
    ["retrbinary", StringArg("LIST"), CallableArg(__simple_callback)],
    ["retrbinary", StringArg("NLST"), CallableArg(__simple_callback)],

    ["retrlines", StringArg("RETR temp1.txt"), CallableArg(__simple_callback)],
    ["retrlines", StringArg("LIST"), CallableArg(__simple_callback)],
    ["retrlines", StringArg("NLST"), CallableArg(__simple_callback)],

    ["size", StringArg("test.txt")],   # Request the size of the file named filename on the server.
    ["dir"],

    ["nlst"],
    ["mlsd"],

    ["delete", StringArg("temp1.txt")],
    ["delete", StringArg("test.txt")],

    ["cwd", StringArg("..")],
    ["rmd", StringArg("test")],

    # ["abort"],
    
    # ["close"],
    ["quit"],
]