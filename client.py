from typing import Dict, Callable
import logging

from utils import Protocol, Addr
from exception import ClientConnectFailed, ClientNotFound


logger = logging.getLogger("client")


class Client:
    """
    Build the connected client and return
    """
    timeout_connect = 5

    @classmethod
    def new(cls, protocol: Protocol, addr: Addr) -> object:
        """Construct the client with the established connection to server"""
        
        client_map: Dict[Protocol, Callable] = {
            Protocol.FTP: cls.ftpclient,
            Protocol.SMTP: cls.smtpclient,
            Protocol.DNS: cls.dnsclient,
        }
        
        if (client_builder := client_map.get(protocol, None)) is None:
            raise ClientNotFound(f"No such client for given protocol: {protocol.name}")

        logger.debug(f"Use {protocol.name} client")
        return client_builder(addr)
    
    @classmethod
    def ftpclient(cls, addr: Addr):
        from ftplib import FTP
        client = FTP()

        for i in range(0, cls.timeout_connect):
            try:
                client.connect(host=addr[0], port=addr[1])
            except:
                if i + 1 == cls.timeout_connect:
                    raise ClientConnectFailed(f"Connection failed after {cls.timeout_connect} times.")
                else:
                    logger.warning(f"FTP client failed to connect to server {i + 1} times.")
        return client
        
    @classmethod
    def smtpclient(cls, addr: Addr):
        from smtplib import SMTP
        client = SMTP()

        for i in range(0, cls.timeout_connect):
            try:
                client.connect(host=addr[0], port=addr[1])
            except:
                if i + 1 == cls.timeout_connect:
                    raise ClientConnectFailed(f"Connection failed after {cls.timeout_connect} times.")
                else:
                    logger.warning(f"FTP client failed to connect to server {i + 1} times.")
        return client

    @classmethod
    def dnsclient(cls, addr: Addr):
        try:
            from dns.resolver import Resolver
        except ModuleNotFoundError:
            raise Exception("Module not found: dnspython")
        
        client = Resolver(configure=False)  # prevent it from reading /etc/resolve.conf
        client.nameservers = [addr[0]]
        client.port = addr[1]
        return client