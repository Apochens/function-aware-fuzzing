import logging
from enum import Enum

from seed import Seed
from exception import SeedNotFound


logger = logging.getLogger("fazz.protocol")


class Protocol(Enum):
    FTP = 959
    SMTP = 5321
    DNS = 1034
    DICOM = None

    @classmethod
    def new(cls, protocol: str) -> "Protocol":
        if protocol == 'ftp':
            return cls.FTP
        if protocol == 'smtp':
            return cls.SMTP
        if protocol == 'dns':
            return cls.DNS
        if protocol == 'dicom':
            return cls.DICOM
        raise Exception("No such protocol")



def new_seed(protocol: Protocol) -> Seed:
    """Construct the corresponding seed"""
    SEED = None

    if protocol == Protocol.FTP:
        from protocol.ftp import SEED
    if protocol == Protocol.SMTP:
        from protocol.smtp import SEED
    if protocol == Protocol.DNS:
        from protocol.dns import SEED
    if protocol == Protocol.DICOM:
        from protocol.dicom import SEED
    
    if SEED is None:
        raise SeedNotFound(f"No seed found for {protocol.name}")
    
    if SEED.len() == 0:
        logger.warning("The initial seed has no api call.")

    logger.debug(f"Use {protocol.name} seed")
    return SEED