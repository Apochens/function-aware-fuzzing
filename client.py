from typing import Optional

from utils import Protocol, Addr


class Client:

    @classmethod
    def new(cls, protocol: Protocol, addr: Addr) -> object:
        """Construct the client with the established connection to server"""
        client: Optional[object] = None

        if protocol == Protocol.FTP: 
            from ftplib import FTP
            client = FTP()
            client.connect(host=addr[0], port=addr[1])

        if protocol == Protocol.SMTP:
            from smtplib import SMTP
            client = SMTP()
            client.connect(host=addr[0], port=addr[1])
        
        if protocol == Protocol.DNS:
            try:
                from dns.resolver import Resolver
            except ModuleNotFoundError:
                raise Exception("Module not found: dnspython")
            client = Resolver(configure=False)  # prevent it from reading /etc/resolve.conf
            client.nameservers = [addr[0]]
            client.port = addr[1]
        
        if client is None:
            raise Exception(f"No such client for given protocol: {protocol.name}")

        return client