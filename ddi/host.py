from ddi.cli import cli
import binascii
import click
import logging
import jsend
import json
import netaddr
import socket

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


def add_host(ip: str, name: str, session: object,  url: str, site_name: str = "UCB",):
    """
    Add a host to DDI

    :param str ip: The IP address to give to the host.
    :param str name: The FQDN for the host, must be unique.
    :param object session: The requests session object.
    :param str url: The URL of the DDI server
    :param str site_name: The site name to use, defaults to UCB.
    :return:
    """
    logger.debug('Adding host: %s, with IP: %s', name, ip)

    payload = {'name': name, 'hostaddr': ip, 'site_name': site_name}

    r = session.post(url + 'ip_add', params=payload)

    logger.debug('Add result code: %s, JSON: %s', r.status_code, r.json())

    r.raise_for_status()

    return r.json()


def delete_host(ip_id: str, session: object, url: str):
    """
    Delete a given host by ip_id.

    :param str ip_id:
    :param object session:
    :param str url:
    :return:
    """
    logger.debug('Deleting host ip_id: %s', ip_id)

    payload = {'ip_id': ip_id}

    r = session.delete(url + 'ip_delete', params=payload)

    logger.debug('Delete result code: %s, JSON: %s', r.status_code, r.json())

    r.raise_for_status()

    return r.json()


def get_host(fqdn: str, session: object, url: str):
    """
    Get the host information from DDI

    :param str fqdn: The fully qualified domain name
    :param object session: A Requests session object.
    :param str url: The URL of the SolidServer.
    :return: Returns the result as JSON
    :rtype: str
    """
    logger.debug('Getting host info for: %s', fqdn)

    r = session.get(url + "ip_address_list/WHERE/name='{0}'".format(fqdn))

    if r.status_code == 200:
        return r.json()
    else:
        raise NotFoundError


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

    d['ip_addr'] = unhexlify_address(host['ip_addr'])

    # If there is no start and end to the subnet we are usually dealing with
    # an external host.
    if host['subnet_start_ip_addr'] == '0' or host['subnet_end_ip_addr'] == '0':
        d['subnet_cidr'] = str(netaddr.IPNetwork(d['ip_addr'] + '/32'))
    else:
        d['subnet_start_ip_addr'] = unhexlify_address(host['subnet_start_ip_addr'])
        d['subnet_end_ip_addr'] = unhexlify_address(host['subnet_end_ip_addr'])
        d['subnet_cidr'] = str(netaddr.iprange_to_cidrs(d['subnet_start_ip_addr'], d['subnet_end_ip_addr'])[0])
    return d


def hexlify_address(ipv4_address: str):
    """
    :param str ipv4_address:
    :return:
    """

    return binascii.hexlify(socket.inet_aton(ipv4_address))


def unhexlify_address(hex_address):
    """
    :param hex_address:
    :return:
    """

    return socket.inet_ntoa(binascii.unhexlify(hex_address))


@cli.group()
@click.pass_context
def host(ctx):
    """Host based commands"""
    pass


@host.command()
@click.argument('host', envvar='DDI_HOST_ADD_HOST', nargs=1)
@click.argument('ip', envvar='DDI_HOST_ADD_IP', nargs=1)
@click.pass_context
def add(ctx, host, ip):
    """Add a single host"""
    logger.debug('Add operation call on host: %s', host)
    r = add_host(ip, host, ctx.obj['session'], ctx.obj['url'])
    if ctx.obj['json']:
        data = jsend.success(r)
        click.echo(json.dumps(data, indent=2, sort_keys=True))
    else:
        click.echo('Host: {} added with IP {}.'.format(host, ip))


@host.command()
@click.confirmation_option(prompt='Are you sure you want to delete the host?')
@click.argument('hosts', envvar='DDI_HOST_HOSTS', nargs=-1)
@click.pass_context
def delete(ctx, hosts):
    """Delete the host(s) from DDI"""
    logger.debug('Delete operation called on hosts: %s', hosts)
    for host in hosts:
        h = get_host(host, ctx.obj['session'], ctx.obj['url'])[0]
        r = delete_host(h['ip_id'], ctx.obj['session'], ctx.obj['url'])
        if ctx.obj['json']:
            click.echo(json.dumps(r, indent=2, sort_keys=True))
        else:
            click.echo('Host: {} deleted.'.format(host))


@host.command()
@click.argument('hosts', envvar='DDI_HOST_HOSTS', nargs=-1)
@click.pass_context
def info(ctx, hosts):
    """Provide the DDI info on the given host(s)"""

    for host in hosts:
        click.echo('Host: {}'.format(host))
        h = get_host(host, ctx.obj['session'], ctx.obj['url'])
        if ctx.obj['json']:
            data = jsend.success(h[0])
            click.echo(json.dumps(data, indent=2, sort_keys=True))
        else:
            # TODO: Output for humans
            click.echo("Host info here!")


@host.command()
@click.argument('hosts', envvar='DDI_HOST_HOSTS', nargs=-1)
@click.pass_context
def subnet(ctx, hosts):
    """Provide the subnet for the given host(s)"""

    for host in hosts:
        click.echo('Host: {}'.format(host))
        d = get_subnets(host, ctx.obj['session'], ctx.obj['url'])
        if ctx.obj['json']:
            click.echo(json.dumps(d, indent=2, sort_keys=True))
        else:
            click.echo(d)

