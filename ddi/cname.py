from ddi.cli import cli
from ddi.host import get_host
from ddi.utilites import get_exceptions

import click
import jsend
import json
import logging

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


def add_cname(cname: str, host: str, session: object, url: str):
    """
    Add a cname to a given host.

    :param str cname: The CNAME to add.
    :param str host: The host FQDN.
    :param object session: The requests session object.
    :param str url: The full URL of the DDI server.
    :return: The response as JSON
    :rtype: list

    """
    logger.debug('Add CNAME: %s called on host: %s', cname, host)

    host_data = get_host(host, session, url)

    if jsend.is_success(host_data):
        entry = host_data['data']['results'][0]

        payload = {'ip_id': entry['ip_id'], 'ip_name': cname}
        r = session.put(url + 'rest/ip_alias_add', json=payload)

        result = get_exceptions(r)

        logger.debug('Add cname result code: %s, JSON: %s', r.status_code, result)

        return result
    else:
        return host_data


def delete_cname(cname: str, session: object, url: str):
    """
    Delete a CNAME from a host.

    :param str cname: The CNAME to add.
    :param str host: The host FQDN.
    :param object session: The requests session object.
    :param str url: The full URL of the DDI server.
    :return: The response as JSON
    :rtype: list
    """
    logger.debug('Delete cname: %s called.', cname)

    host_data = get_cname_info(cname, session, url)

    if jsend.is_success(host_data):
        entry = host_data['data']['results'][0]

        payload = {'ip_id': entry['ip_id'], 'ip_name': cname}

        r = session.delete(url + 'rest/ip_alias_delete', json=payload)

        result = get_exceptions(r)

        logger.debug('Delete cname result code: %s, JSON: %s', r.status_code, result)

        return result
    else:
        return host_data


def get_cname_info(cname: str, session: object, url: str):
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

    r = session.get(url + 'rest/ip_address_list', params=payload)

    result = get_exceptions(r)

    return result


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

    r = add_cname(cname, host, ctx.obj['session'], ctx.obj['url'])

    if ctx.obj['json']:
        click.echo(json.dumps(r, indent=2, sort_keys=True))
    elif jsend.is_success(r):
        click.echo(f'CNAME: {cname} added to host: {host}.')
    else:
        click.echo(f'CNAME: {cname} addition to host {host} failed.')
        ctx.exit(1)


@cname.command()
@click.confirmation_option(prompt='Are you sure you want to delete this CNAME?')
@click.argument('cname', envvar='DDI_CNAME_DELETE_CNAME', nargs=1)
@click.pass_context
def delete(ctx, cname):
    """Delete a single CNAME entry for a host."""

    r = delete_cname(cname, ctx.obj['session'], ctx.obj['url'])

    if ctx.obj['json']:
        click.echo(json.dumps(r, indent=2, sort_keys=True))
    elif jsend.is_success(r):
        click.echo(f'CNAME: {cname} deleted.')
    else:
        click.echo(f'CNAME delete failed for: {cname}')
        ctx.exit(1)


@cname.command()
@click.argument('cname', envvar='DDI_CNAME_INFO_CNAME', nargs=1)
@click.pass_context
def info(ctx, cname):
    """Retrieve the host info associated with a CNAME."""

    r = get_cname_info(cname, ctx.obj['session'], ctx.obj['url'])

    if ctx.obj['json']:
        click.echo(json.dumps(r, indent=2, sort_keys=True))
    elif jsend.is_success(r):
        host_data = r['data']['results'][0]
        click.echo(f"Hostname: {host_data['name']}.")
        click.echo(f"CNAMES: {host_data['ip_alias']}")
    else:
        click.echo(f'CNAME info for {cname} failed.')
        ctx.exit(1)
