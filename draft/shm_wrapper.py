import sysv_ipc
import ctypes.util
import sys, os
import subprocess


SHM_ENV_VAR = "__AFL_SHM_ID"
MAP_SIZE = (1 << 16)

def check(bt):
    a = ctypes.string_at(bt, MAP_SIZE)
    j = 0
    for i in a:
        if i != 0:
            j += 1
    print('{} hits'.format(j))


def start_server() -> subprocess.Popen:
    server_path = "/home/linuxbrew/afl-lightftp/Source/Release/"
    os.chdir(server_path)
    lightftp_server = "./fftp"

    proc = subprocess.Popen([lightftp_server], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=True)
    if not proc:
        raise Exception("Server down!")

    return proc


def stop_server(proc: subprocess.Popen) -> int:
    proc.communicate('q'.encode())
    return proc.wait()


def setup_shm():
    """
    create an `AFL`-style shared memery with C `shmget`, and map it into the current process's memory,
    returning the pointer of that area.
    """
    libc_path = ctypes.util.find_library("c")
    if not libc_path:
        sys.exit("cannot find libc")

    libc = ctypes.CDLL(libc_path)
    if not libc:
        sys.exit("cannot load libc")

    shmget = libc.shmget
    shmat = libc.shmat
    shmat.restype = ctypes.c_void_p
    shmat.argtypes = (ctypes.c_int, ctypes.c_void_p, ctypes.c_int)

    shmid = shmget(sysv_ipc.IPC_PRIVATE, MAP_SIZE, sysv_ipc.IPC_CREAT | sysv_ipc.IPC_EXCL | 0o600)
    os.environ[SHM_ENV_VAR] = str(shmid)

    if shmid < 0:
        sys.exit("cannot get shared memory segment with key %d" % (sysv_ipc.IPC_PRIVATE))

    shmptr = shmat(shmid, None, 0)
    if shmptr == 0 or shmptr== -1:
        sys.exit("cannot attach shared memory segment with id %d" % (shmid))

    return shmptr


if __name__ == "__main__":

    trace_bits = setup_shm()

    ctypes.memset(trace_bits, 0, MAP_SIZE)

    print("test...")
    stop_server(start_server())
    print("end...")

    check(trace_bits)
