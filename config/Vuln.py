class VulnConf:
    def __init__(self, external_ip, name, internal_ip):
        self.external_ip = external_ip
        self.name = name
        self.internal_ip = internal_ip

    def __str__(self):
        return (f"TeamConf(Name: {self.name}, External IP: {self.external_ip}, "
                f"Internal IP: {self.internal_ip})")

class VulnConfFactory:
    def __init__(self, internal_subnet='10.80.0.0/24'):
        self._current_internal_ip_octet = 1
        self.internal_subnet = internal_subnet

    def create_vuln(self, external_ip, name):
        """Create a team with an external IP and name, and assign an internal IP."""
        internal_ip = f"10.80.{self._current_internal_ip_octet}.2"
        self._current_internal_ip_octet += 1
        return VulnConf(external_ip=external_ip, name=name, internal_ip=internal_ip)
