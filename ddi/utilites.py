import binascii
import netaddr
import socket
import urllib


def get_subnets(host_data: dict):
    """
    Get the subnets on which a given host exists.

    :param dict host_data: The host data as returned by get_host().
    :return: The host data with subnet_cidr and subnet_mask added and all
             other IPs and subnets converted to dotted quad from hex.
    :rtype: dict
    """

    host_data['ip_addr'] = unhexlify_address(host_data['ip_addr'])

    # If there is no start and end to the subnet we are usually dealing with
    # an external host.
    if host_data['subnet_start_ip_addr'] == '0' or \
            host_data['subnet_end_ip_addr'] == '0':
        host_data['subnet_cidr'] = \
            str(netaddr.IPNetwork(host_data['ip_addr'] + '/32'))
        host_data['subnet_mask'] = '255.255.255.255'
    else:
        host_data['subnet_start_ip_addr'] = \
            unhexlify_address(host_data['subnet_start_ip_addr'])
        host_data['subnet_end_ip_addr'] = \
            unhexlify_address(host_data['subnet_end_ip_addr'])
        subnet = netaddr.iprange_to_cidrs(host_data['subnet_start_ip_addr'],
                                          host_data['subnet_end_ip_addr'])[0]
        host_data['subnet_cidr'] = str(subnet)
        host_data['subnet_netmask'] = str(subnet.netmask)

    return host_data


def hexlify_address(ipv4_address: str):
    """
    Convert a dotted quad IPv4 address to hex.

    :param str ipv4_address: The IPv4 address.
    :return: The hex address.
    :rtype: str
    """

    return binascii.hexlify(socket.inet_aton(ipv4_address))


def query_string_to_dict(host_info):
    """
    Turn a URL query string into a dictionary.

    :param dict host_info: Host info from DDI with populated attributes.
    :return: Host info with attributes translated from query string to dict.
    :rtype: dict
    """

    parameters = [
        'ip_class_parameters',
        'ip_class_parameters_inheritance_source',
        'ip_class_parameters_properties',
        'subnet_class_parameters',
        'subnet_class_parameters_properties'
    ]

    for parameter in parameters:
        p = host_info.get(parameter, '')
        host_info[parameter] = urllib.parse.parse_qs(p)

    return host_info


def unhexlify_address(hex_address: str):
    """
    Convert a hex address into a dotted quad address.

    :param str hex_address: The address as hex.
    :return: The address as a dotted quad.
    :rtype: str
    """

    return socket.inet_ntoa(binascii.unhexlify(hex_address))
