import ipaddress


class IPNetwork(ipaddress.IPv4Network):

    def __add__(self, offset):
        """Add numeric offset to the IPv4Network."""
        new_base_addr = int(self.network_address) + (self.size() * offset)
        return self.__class__((new_base_addr, str(self.netmask)))

    def __sub__(self, offset):
        """Subtract numeric offset to the IPv4Network. """
        new_base_addr = int(self.network_address) - (self.size() * offset)
        return self.__class__((new_base_addr, str(self.netmask)))

    def size(self):
        """Return network size."""
        start = int(self.network_address)
        return int(self.broadcast_address) + 1 - start
