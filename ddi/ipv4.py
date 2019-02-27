from ddi.cli import cli
from ddi.utilites import echo_host_info, get_exceptions, hexlify_address

import click
import jsend
import json
import logging

logger = logging.getLogger(__name__)


def get_free_ipv4(subnet_id: str, session:object, url:str):
    """
    Get a free IP address in a given subnet ID.
    :param str subnet_id: The subnet ID to get the free IP for (e.g. 541)
    :param object session: the requests session object
    :param url: The full URL of the DDI server.
    :return: The JSON response in JSEND format.
    :rtype: dict
    """
    logger.debug('Getting free IP for subnet ID: %s', subnet_id)

    payload = {'subnet_id': subnet_id}

    r = session.get(url + '/rpc/ip_find_free_address', params=payload)

    result = get_exceptions(r)

    return result


def get_ipv4_info(ip: str, session: object, url: str):
    """
    Get the host information from DDI.

    :param str ip: The IPv4 address as a dotted quad.
    :param object session: The requests session object.
    :param str url: The full URL of the DDI server.
    :return: The JSON response in JSEND format.
    :rtype: dict
    """
    logger.debug('Getting IP info for: %s', ip)

    ip = hexlify_address(ip).decode()

    payload = {'WHERE': f"ip_addr='{ip}'"}
    r = session.get(url + 'rest/ip_address_list', params=payload)

    result = get_exceptions(r)

    return result


@cli.group()
@click.pass_context
def ipv4(ctx):
    """IPv4 based commands."""
    pass


@ipv4.command()
@click.argument('ips', envvar='DDI_IP_INFO_IPS', nargs=-1)
@click.pass_context
def info(ctx, ips):
    """Provide information on the given IPv4 address(es)."""

    logger.debug('Info operation called on IPs: %s.', ips)
    for ip in ips:
        r = get_ipv4_info(ip, ctx.obj['session'], ctx.obj['url'])
        if ctx.obj['json']:
            click.echo(json.dumps(r, indent=2, sort_keys=True))
        elif jsend.is_success(r):
            echo_host_info(r)
        else:
            click.echo('Request failed, enable debugging for more.')
