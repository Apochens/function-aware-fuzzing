import logging

from seed import Seed
from utils import Protocol


logger = logging.getLogger("fazz.corpus")


def new_seed(protocol: Protocol) -> Seed:
    """Construct the corresponding seed"""
    SEED = None

    if protocol == Protocol.FTP:
        from corpus.ftp import SEED
    if protocol == Protocol.SMTP:
        from corpus.smtp import SEED
    if protocol == Protocol.DNS:
        from corpus.dns import SEED
    
    if SEED is None:
        raise Exception(f"No seed found for {protocol.name}")
    
    if len(SEED) == 0:
        logger.warning("The initial seed has no api call.")

    logger.debug(f"Use {protocol.name} seed")
    return Seed(SEED)