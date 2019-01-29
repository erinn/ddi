from ddi.cli import cli
import binascii
import click
import jsend
import json
import logging
import netaddr
import socket
import urllib.parse

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


def add_cname(cname: str, host_data: dict, session:object, url: str):
    """
    Add a cname to a given host.

    :param str cname:
    :param dict host_data:
    :param object session:
    :param str url:
    :return:

    """
    pass


def add_host(building: str, department: str, contact: str,
             ip: str, phone: str, name: str, session: object,  url: str,
             comment=None, site_name: str = "UCB",):
    """
    Add a host to DDI.

    :param str building: The UCB building the host is located in.
    :param str contact: The UCB contact person for the host.
    :param str comment: An optional comment.
    :param str department: The UCB department the host is affiliated with.
    :param str ip: The IP address to give to the host.
    :param str phone: The phone number associated with the host.
    :param str name: The FQDN for the host, must be unique.
    :param object session: The requests session object.
    :param str url: The URL of the DDI server.
    :param str site_name: The site name to use, defaults to UCB.
    :return: The JSON result of the operation.
    :rtype: str
    """

    ip_class_parameters = {'hostname': name.split('.')[0],
                           'ucb_buildings': building,
                           'ucb_dept_aff': department,
                           'ucb_ph_no': phone,
                           'ucb_resp_per': contact}

    # Add the comment if it was passed in
    if comment:
        ip_class_parameters['ucb_comment'] = comment

    ip_class_parameters = urllib.parse.urlencode(ip_class_parameters)

    payload = {'hostaddr': ip, 'name': name, 'site_name': site_name,
               'ip_class_parameters': ip_class_parameters}

    logger.debug('Add operation invoked on Host: %s with IP: %s, Building: %s, '
                 'Department: %s, Contact: %s Phone: %s, and Payload: %s', name,
                 ip, building, department, contact, phone, payload)

    r = session.post(url + 'ip_add', json=payload)

    logger.debug('Add result code: %s, JSON: %s', r.status_code, r.json())

    r.raise_for_status()

    return r.json()[0]


def delete_host(ip_id: str, session: object, url: str):
    """
    Delete a given host by ip_id.

    :param str ip_id: The IP ID from the DDI database,
    :param object session: The requests session object.
    :param str url: The URL of the DDI server.
    :return: The JSON result of the operation.
    :rtype: str
    """
    logger.debug('Deleting host ip_id: %s', ip_id)

    payload = {'ip_id': ip_id}

    r = session.delete(url + 'ip_delete', params=payload)

    logger.debug('Delete result code: %s, JSON: %s', r.status_code, r.json())

    r.raise_for_status()

    return r.json()[0]


def get_host(fqdn: str, session: object, url: str):
    """
    Get the host information from DDI.

    :param str fqdn: The fully qualified domain name
    :param object session: The requests session object.
    :param str url: TThe URL of the DDI server.
    :return: The JSON result of the operation.
    :rtype: str
    """
    logger.debug('Getting host info for: %s', fqdn)

    r = session.get(url + "ip_address_list/WHERE/name='{0}'".format(fqdn))

    r.raise_for_status()

    json_response = r.json()

    # Modify the URL Query String format to be a dict
    for host in json_response:
        host = query_string_to_dict(host)

    return json_response


def get_subnets(fqdn: str, session: object, url: str):
    """
    Get the subnets on which a given host exists.

    :param str fqdn: The FQDN for the host to get the subnet information for.
    :param object session: The requests session object.
    :param str url: The URL for the DDI server.
    :return: A dictionary with the subnet information.
    :rtype: dict
    """
    d = {}
    host = get_host(fqdn, session, url)[0]

    d['name'] = host['name']
    d['ip_addr'] = unhexlify_address(host['ip_addr'])

    # If there is no start and end to the subnet we are usually dealing with
    # an external host.
    if host['subnet_start_ip_addr'] == '0' or host['subnet_end_ip_addr'] == '0':
        d['subnet_cidr'] = str(netaddr.IPNetwork(d['ip_addr'] + '/32'))
    else:
        d['subnet_start_ip_addr'] = unhexlify_address(host['subnet_start_ip_addr'])
        d['subnet_end_ip_addr'] = unhexlify_address(host['subnet_end_ip_addr'])
        subnet = netaddr.iprange_to_cidrs(d['subnet_start_ip_addr'],
                                          d['subnet_end_ip_addr'])[0]
        d['subnet_cidr'] = str(subnet)
        d['subnet_netmask'] = str(subnet.netmask)
    return d


def hexlify_address(ipv4_address: str):
    """
    Convert a dotted quad IPv4 address to hex.

    :param str ipv4_address: The IPv4 address.
    :return: The hex address.
    :rtype: str
    """

    return binascii.hexlify(socket.inet_aton(ipv4_address))


def unhexlify_address(hex_address: str):
    """
    Convert a hex address into a dotted quad address.

    :param str hex_address: The address as hex.
    :return: The address as a dotted quad.
    :rtype: str
    """

    return socket.inet_ntoa(binascii.unhexlify(hex_address))


def query_string_to_dict(host_info):
    """
    Turn a URL query string into a dictionary.

    :param dict host_info: Host info from DDI with populated attributes
    :return: Host info with attributes translaced from query string to dict
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


@cli.group()
@click.pass_context
def host(ctx):
    """Host based commands."""
    pass


@host.command()
@click.option('--building', '-b', help='The UCB building the host is in.', prompt=True, required=True)
@click.option('--comment', help='Additional comment for the host.')
@click.option('--contact', '-c', help='The UCB contact for the host.', prompt=True, required=True)
@click.option('--department', '-d', help='The UCB department the host belongs to.', prompt=True, required=True)
@click.option('--ip', '-i', help='The IPv4 address for the host.', prompt=True, required=True)
@click.option('--phone', '-p', help='The UCB phone number associated with the host.', prompt=True, required=True)
@click.argument('host', envvar='DDI_HOST_ADD_HOST', nargs=1)
@click.pass_context
def add(ctx, building, comment, contact, department, ip, phone, host):
    """Add a single host entry into DDI"""

    r = add_host(building, department, contact, ip, phone, host, ctx.obj['session'], ctx.obj['url'], comment=comment)

    if ctx.obj['json']:
        data = jsend.success(r)
        click.echo(json.dumps(data, indent=2, sort_keys=True))
    else:
        click.echo('Host: {} added with IP {}.'.format(host, ip))


@host.command()
@click.confirmation_option(prompt='Are you sure you want to delete the host?')
@click.argument('hosts', envvar='DDI_HOST_DELETE_HOSTS', nargs=-1)
@click.pass_context
def delete(ctx, hosts):
    """Delete the host(s) from DDI."""

    logger.debug('Delete operation called on hosts: %s.', hosts)

    for host in hosts:
        h = get_host(host, ctx.obj['session'], ctx.obj['url'])[0]
        r = delete_host(h['ip_id'], ctx.obj['session'], ctx.obj['url'])
        if ctx.obj['json']:
            data = jsend.success(r)
            click.echo(json.dumps(data, indent=2, sort_keys=True))
        else:
            click.echo('Host: {} deleted.'.format(host))


@host.command()
@click.argument('hosts', envvar='DDI_HOST_INFO_HOSTS', nargs=-1)
@click.pass_context
def info(ctx, hosts):
    """Provide the DDI info on the given host(s)."""

    logger.debug('Info operation called on hosts: %s.', hosts)

    for host in hosts:
        click.echo('Host: {}'.format(host))
        r = get_host(host, ctx.obj['session'], ctx.obj['url'])[0]
        if ctx.obj['json']:
            data = jsend.success(r)
            click.echo(json.dumps(data, indent=2, sort_keys=True))
        else:
            click.echo('')
            click.echo('Hostname: {}'.format(r['name']))
            click.echo('Short Hostname: {}'
                       .format(r['ip_class_parameters']['hostname'][0]))
            click.echo('IP Address: {}'.format(unhexlify_address(r['ip_addr'])))
            click.echo('CNAMES: {}'.format(r['ip_alias']))
            click.echo('UCB Department: {}'
                       .format(r['ip_class_parameters']['ucb_dept_aff'][0]))
            click.echo('UCB Building: {}'.format(r['ip_class_parameters']['ucb_buildings'][0]))
            click.echo('UCB Responsible Person: {}'
                       .format(r['ip_class_parameters']['ucb_resp_per'][0]))
            click.echo('UCB Phone Number: {}'
                       .format(r['ip_class_parameters']['ucb_ph_no'][0]))
            click.echo('')



@host.command()
@click.argument('hosts', envvar='DDI_HOST_SUBNET_HOSTS', nargs=-1)
@click.pass_context
def subnet(ctx, hosts):
    """Provide the subnet beginning, end, netmask, and CIDR for the given host(s)."""

    logger.debug('Subnet operation called on hosts: %s.', hosts)

    for host in hosts:
        r = get_subnets(host, ctx.obj['session'], ctx.obj['url'])
        if ctx.obj['json']:
            data = jsend.success(r)
            click.echo(json.dumps(data, indent=2, sort_keys=True))
        else:
            click.echo('')
            click.echo('Hostname: {}'.format(r['name']))
            click.echo('Host IP: {}'.format(r['ip_addr']))
            click.echo('Subnet Start: {}'.format(r['subnet_start_ip_addr']))
            click.echo('Subnet End: {}'.format(r['subnet_end_ip_addr']))
            click.echo('Subnet Netmask: {}'.format(r['subnet_netmask']))
            click.echo('Subnet CIDR: {}'.format(r['subnet_cidr']))
            click.echo('')

