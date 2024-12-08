import ipaddress
from .Member import MemberFactory, Member
from .WGKeyManagement import WGKeyManagement
from .Conf import Conf

class Vuln(WGKeyManagement, Conf):
    def __init__(self, external_ip, name, internal_ip, internal_subnet, users_subnet, team_members):
        WGKeyManagement.__init__(self)
        Conf.__init__(self)
        self.external_ip = external_ip
        self.name = name
        self.internal_ip = internal_ip
        self.internal_subnet = internal_subnet
        self.users_subnet = users_subnet
        self.team_members = team_members
        # Create team members
        member_factory = MemberFactory(users_subnet=users_subnet, team_name=name, num_members=team_members)
        self.members = member_factory.create_members()

    def __str__(self):
        members_str = "\n    ".join(str(member) for member in self.members)
        return (f"Vuln(Name: {self.name}, External IP: {self.external_ip}, "
                f"Internal IP: {self.internal_ip}, Internal Subnet: {self.internal_subnet}, "
                f"Users Subnet: {self.users_subnet}\n"
                f"  Members:\n    {members_str})")


class VulnFactory:
    def __init__(self, internal_subnet='10.80.0.0/16', users_subnet='10.60.0.0/16', team_members=5):
        # Initialize the network and start iterating over the /24 subnets
        self.network = ipaddress.IPv4Network(internal_subnet)
        self.users_base_network = ipaddress.IPv4Network(users_subnet)
        self._current_subnet_iter = iter(self.network.subnets(new_prefix=24))  # Generate /24 subnets from the /16
        self._current_internal_ip_octet = 0  # Tracks the 'x' part of the subnet (e.g., 10.x.0.0/24)
        self._current_user_subnet_num = 1  # Start with 10.60.1.0/24
        self.team_members = team_members  # Number of users (vulnerabilities) to create

    def create_vuln(self, external_ip, name):
        """Creates a new Vuln with an available internal subnet and provided external IP and name."""
        # Get the next available /24 subnet
        current_subnet = next(self._current_subnet_iter)

        # Calculate the internal IP, which is always .2 in the x.y.z.2 format for each /24 subnet
        internal_ip = f"10.{current_subnet.network_address.packed[1]}.{self._current_internal_ip_octet + 1}.2"

        # The internal subnet is always .0/24 for the respective subnet
        internal_subnet = f"10.{current_subnet.network_address.packed[1]}.{self._current_internal_ip_octet + 1}.0/24"

        # Calculate the users subnet (10.60.X.0/24 where X increments for each team)
        users_subnet = f"10.60.{self._current_user_subnet_num}.0/24"

        # Increment the subnet indices for the next subnet
        self._current_internal_ip_octet += 1
        self._current_user_subnet_num += 1

        return Vuln(external_ip=external_ip, name=name, internal_ip=internal_ip, 
                       internal_subnet=internal_subnet, users_subnet=users_subnet, team_members=self.team_members)


class VulnFactoryBuilder:
    def __init__(self):
        self._internal_subnet = '10.80.0.0/16'  # Default subnet
        self._users_subnet = '10.60.0.0/16'  # Default users subnet
        self._num_users = 1  # Default number of users to create

    def set_internal_subnet(self, internal_subnet):
        self._internal_subnet = internal_subnet
        return self

    def set_users_subnet(self, users_subnet):
        self._users_subnet = users_subnet
        return self

    def set_team_members(self, team_members):
        self._num_users = team_members
        return self

    def build(self):
        return VulnFactory(internal_subnet=self._internal_subnet, users_subnet=self._users_subnet, team_members=self._num_users)
