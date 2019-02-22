from ddi.cli import cli
from ddi.utilites import echo_host_info, get_exceptions, hexlify_address

import click
import jsend
import json
import logging

logger = logging.getLogger(__name__)


def get_subnet_info(subnet: str, session:object, url:str):
    """
    Get information about a given subnet.

    :param str subnet: The subnet to get the free IP for (e.g. 192.168.127.0)
    :param object session: the requests session object
    :param url: The full URL of the DDI server.
    :return: The JSON response in JSEND format.
    :rtype: dict
    """
    logger.debug('Getting subnet info for: %s', subnet)

    subnet = hexlify_address(subnet).decode()

    payload = {'WHERE': f"start_ip_addr='{subnet}'"}

    r = session.get(url + '/rest/ip_block_subnet_list', params=payload)

    result = get_exceptions(r)

    return result


@cli.group()
@click.pass_context
def subnet(ctx):
    """Subnet based commands."""
    pass


@subnet.command()
@click.argument('subnets', envvar='DDI_SUBNET_INFO_SUBNETS', nargs=-1)
@click.pass_context
def info(ctx, subnets):
    """Provide the DDI info on the given subnet(s)."""

    logger.debug('Info operation called on subnets: %s.', subnets)

    for subnet in subnets:
        r = get_subnet_info(subnet, ctx.obj['session'], ctx.obj['url'])
        if ctx.obj['json']:
            click.echo(json.dumps(r, indent=2, sort_keys=True))
        elif jsend.is_success(r):
            echo_host_info(r)
        else:
            click.echo('Request failed, enable debugging for more.')
