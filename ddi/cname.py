from ddi.cli import cli
from ddi.host import get_host
import click
import jsend
import json
import logging

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


def add_cname(cname: str, host_data: dict, session: object, url: str):
    """
    Add a cname to a given host.

    :param str cname: The CNAME to add.
    :param dict host_data: The host data for the host.
    :param object session: The requests session object.
    :param str url: The full URL of the DDI server.
    :return: The response as JSON
    :rtype: list

    """
    logger.debug('Add cname: %s called on host: %s', cname, host_data['name'])

    payload = {'ip_id': host_data['ip_id'], 'ip_name': cname}
    r = session.put(url + 'ip_alias_add', json=payload)

    r.raise_for_status()

    logger.debug('Add cname result code: %s, JSON: %s', r.status_code, r.json())

    return r.json()


def delete_cname(cname: str, host_data: dict, session: object, url: str):
    """
    Delete a CNAME from a host.

    :param str cname: The CNAME to add.
    :param dict host_data: The host data for the host.
    :param object session: The requests session object.
    :param str url: The full URL of the DDI server.
    :return: The response as JSON
    :rtype: list
    """

    logger.debug('Delete cname: %s called on host: %s', cname, host_data['name'])

    payload = {'ip_id': host_data['ip_id'], 'ip_name': cname}

    r = session.delete(url + 'ip_alias_delete', json=payload)

    r.raise_for_status()

    logger.debug('Delete cname result code: %s, JSON: %s', r.status_code, r.json())

    return r.json()


def get_cname_info(cname: str, session:object, url: str):
    """
    Get host information associated with a given CNAME.

    :param str cname: The CNAME to search for.
    :param object session: The requests session object.
    :param str url: The full URL of the DDI server.
    :return: The response as JSON.
    :rtype: list
    """
    logger.debug('Get CNAME called for: %s', cname)

    payload = {'WHERE': f"ip_alias like '%{cname}%'"}

    r = session.get(url + 'ip_address_list', params=payload)

    r.raise_for_status

    logger.debug('Get cname result code: %s, JSON: %s', r.status_code, r.json())

    return r.json()


@cli.group()
@click.pass_context
def cname(ctx):
    """CNAME based commands."""


@cname.command()
@click.argument('host', envvar='DDI_CNAME_ADD_HOST', nargs=1)
@click.argument('cname', envvar='DDI_CNAME_ADD_CNAME', nargs=1)
@click.pass_context
def add(ctx, host, cname):
    """Add a single CNAME entry to an existing host."""

    host_data = get_host(host, ctx.obj['session'], ctx.obj['url'])[0]
    r = add_cname(cname, host_data, ctx.obj['session'], ctx.obj['url'])

    if ctx.obj['json']:
        data = jsend.success(r)
        click.echo(json.dumps(data, indent=2, sort_keys=True))
    else:
        click.echo(f"CNAME: {cname} added to host: {host_data['name']}.")


@cname.command()
@click.confirmation_option(prompt='Are you sure you want to delete this CNAME?')
@click.argument('cname', envvar='DDI_CNAME_DELETE_CNAME', nargs=1)
@click.pass_context
def delete(ctx, cname):
    """Delete a single CNAME entry for a host."""
    host_data = get_cname_info(cname, ctx.obj['session'], ctx.obj['url'])[0]
    r = delete_cname(cname, host_data, ctx.obj['session'], ctx.obj['url'])

    if ctx.obj['json']:
        data = jsend.success(r)
        click.echo(json.dumps(data, indent=2, sort_keys=True))
    else:
        click.echo(f"CNAME: {cname} deleted from host: {host_data['name']}.")


@cname.command()
@click.argument('cname', envvar='DDI_CNAME_INFO_CNAME', nargs=1)
@click.pass_context
def info(ctx, cname):
    """Retrieve the host info associated with a CNAME."""

    host_data = get_cname_info(cname, ctx.obj['session'], ctx.obj['url'])[0]

    if ctx.obj['json']:
        data = jsend.success(host_data)
        click.echo(json.dumps(data, indent=2, sort_keys=True))
    else:
        click.echo(f"Hostname: {host_data['name']}.")
        click.echo(f"CNAMES: {host_data['ip_alias']}")

