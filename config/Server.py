import ipaddress
from .WGKeyManagement import WGKeyManagement
from .Conf import Conf

class Server(WGKeyManagement, Conf):
    def __init__(self, name: str, external_ip: str, internal_ip: str, internal_subnet: str, port: int):
        WGKeyManagement.__init__(self)
        Conf.__init__(self)
        self.name = name
        self.external_ip = external_ip
        self.internal_ip = internal_ip
        self.internal_subnet = internal_subnet
        self.port = port

    def __str__(self):
        return (f"Server(Name: {self.name}, External IP: {self.external_ip}, "
                f"Internal IP: {self.internal_ip}, Internal Subnet: {self.internal_subnet}, Port: {self.port})")


class ServerBuilder:
    def __init__(self):
        self._name = "server"
        self._external_ip = ""
        self._internal_ip = ""
        self._internal_subnet = ""
        self._port = 52000

    def set_name(self, name: str):
        self._name = name
        return self

    def set_external_ip(self, external_ip: str):
        self._external_ip = external_ip
        return self

    def set_internal_ip(self, internal_ip: str):
        self._internal_ip = internal_ip
        return self

    def set_internal_subnet(self, internal_subnet: str):
        self._internal_subnet = internal_subnet
        return self
    
    def set_port(self, port: int):
        self._port = port
        return self

    def build(self) -> Server:
        return Server(
            name=self._name,
            external_ip=self._external_ip,
            internal_ip=self._internal_ip,
            internal_subnet=self._internal_subnet,
            port=self._port
        )
