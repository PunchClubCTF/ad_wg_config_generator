import ipaddress
from .WGKeyManagement import WGKeyManagement
from .Conf import Conf

class Member(WGKeyManagement, Conf):
    def __init__(self, name, ip):
        WGKeyManagement.__init__(self)
        Conf.__init__(self)
        self.name = name
        self.ip = ip
        self._private_key = None
        self._public_key = None

    def __str__(self):
        return f"Member(Name: {self.name}, IP: {self.ip})"

class MemberFactory:
    def __init__(self, users_subnet, team_name, num_members=5):
        self.network = ipaddress.IPv4Network(users_subnet)
        self.team_name = team_name
        self.num_members = num_members
        self._current_ip_index = 1  # Start from .1 in the subnet

    def create_members(self):
        """Creates a list of team members with sequential IPs from the users subnet."""
        members = []
        network_prefix = str(self.network.network_address).rsplit('.', 1)[0]
        
        for i in range(self.num_members):
            member_ip = f"{network_prefix}.{self._current_ip_index}"
            member_name = f"{self.team_name}_{i+1}"
            members.append(Member(name=member_name, ip=member_ip))
            self._current_ip_index += 1
            
        return members
