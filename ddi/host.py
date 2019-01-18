from ddi.cli import cli
import binascii
import click
import json
import netaddr
import socket



class NotFoundError(Exception):
    pass


def get_host(fqdn: str, session: object, url: str):
    """
    :param str fqdn: The fully qualified domain name
    :param object session: A Requests session object.
    :param str url: The URL of the SolidServer.
    :return:
    """

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
        d['subnet_cidr'] = netaddr.IPNetwork( d['ip_addr'] + '/32')
    else:
        d['subnet_start_ip_addr'] = unhexlify_address(
            host['subnet_start_ip_addr'])
        d['subnet_end_ip_addr'] = unhexlify_address(host['subnet_end_ip_addr'])
        d['subnet_cidr'] = netaddr.iprange_to_cidrs(d['subnet_start_ip_addr'],
                                                    d['subnet_end_ip_addr'])[0]
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


@host.command()
@click.confirmation_option(prompt='Are you sure you want to delete the host?')
@click.pass_context
def delete(ctx):
    """Delete the host from DDI"""
    click.echo("deleted host!")


@host.command()
@click.argument('hosts', envvar='DDI_HOST_HOSTS', nargs=-1)
@click.pass_context
def info(ctx, hosts):
    """Provide the DDI info on the given host(s)"""
    url = ctx.obj['server'] + '/rest/'

    for host in hosts:
        click.echo('Host: {}'.format(host))
        h = get_host(host, ctx.obj['session'], url)
        click.echo(h)


@host.command()
@click.argument('hosts', envvar='DDI_HOST_HOSTS', nargs=-1)
@click.pass_context
def subnet(ctx, hosts):
    """Provide the subnets for the given hosts"""
    url = ctx.obj['server'] + '/rest/'

    for host in hosts:
        click.echo('Host: {}'.format(host))
        d = get_subnets(host, ctx.obj['session'], url)
        click.echo(d)

