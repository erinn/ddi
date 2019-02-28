from requests.exceptions import HTTPError
from json.decoder import JSONDecodeError
import binascii
import click
import jsend
import logging
import netaddr
import socket
import urllib

logger = logging.getLogger(__name__)


def echo_host_info(host_info):
    """
    A central function to echo out host info so code is not dulpicated
    everywhere.

    :param host_info: A JSEND success object.
    :return: None
    :rtype: None
    """
    logger.debug('Echoing host info.')
    for host in host_info['data']['results']:
        host = get_subnets(host)
        host = query_string_to_dict(host)
        click.echo('')
        click.echo(f"Hostname: {host['name']}")
        click.echo('Short Hostname: '
                   f"{host['ip_class_parameters'].get('hostname', [''])[0]}")
        click.echo(f"IP Address: {host['ip_addr']}")
        click.echo(f"CNAMES: {host['ip_alias']}")
        click.echo(f"Subnet Start: {host['subnet_start_ip_addr']}")
        click.echo(f"Subnet End: {host['subnet_end_ip_addr']}")
        click.echo(f"Subnet Netmask: {host['subnet_netmask']}")
        click.echo(f"Subnet CIDR: {host['subnet_cidr']}")
        click.echo('UCB Building: '
                   f"{host['ip_class_parameters'].get('ucb_buildings', [''])[0]}")
        click.echo('UCB Comment: '
                   f"{host['ip_class_parameters'].get('ucb_comment', [''])[0]}")
        click.echo('UCB Department: '
                   f"{host['ip_class_parameters'].get('ucb_dept_aff', [''])[0]}")
        click.echo(f"UCB Phone Number: "
                   f"{host['ip_class_parameters'].get('ucb_ph_no', [''])[0]}")
        click.echo('UCB Responsible Person: '
                   f"{host['ip_class_parameters'].get('ucb_resp_per', [''])[0]}")
        click.echo('')

    return None


def get_exceptions(result: object):
    """
    Catch and return errors from a request result.

    :param result: A requests session result.
    :return: A jsend formatted result with either success or failure.
    :rtype: dict
    """
    logger.debug('Examining result for exceptions.')

    # Determine if they gave us JSON, if not set the data to nothing.
    try:
        r_json = {'results': result.json()}
    except JSONDecodeError:
        logger.debug('Results are not JSON.')
        r_json = {'results': []}

    try:
        result.raise_for_status()
    except HTTPError:
        logger.debug('HTTP Error Code: %s detected', result.status_code)
        return jsend.fail(r_json)

    # 204 is essentially an error, so we catch it.
    if result.status_code == 204:
        return jsend.fail(r_json)
    else:
        return jsend.success(r_json)


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
