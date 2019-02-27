from ddi.cli import cli
from ddi.utilites import echo_host_info, get_exceptions

import click
import jsend
import json
import logging
import urllib.parse

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
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

    r = session.post(url + 'rest/ip_add', json=payload)

    logger.debug('Add host result code: %s, JSON: %s', r.status_code, r.json())

    r.raise_for_status()

    return r.json()[0]


def delete_host(fqdn: str, session: object, url: str):
    """
    Delete a given host by ip_id.

    :param str fqdn: The FQDN of the host object to delete.
    :param object session: The requests session object.
    :param str url: The URL of the DDI server.
    :return: The JSON result of the operation.
    :rtype: str
    """

    h = get_host(fqdn, session, url)

    if jsend.is_success(h):
        ip_id = h['data']['results'][0]['ip_id']

        logger.debug('Deleting host: %s with ip_id: %s', fqdn, ip_id)

        payload = {'ip_id': ip_id}
        r = session.delete(url + 'rest/ip_delete', params=payload)

        result = get_exceptions(r)

        return result
    else:
        return h


def get_host(fqdn: str, session: object, url: str):
    """
    Get the host information from DDI.

    :param str fqdn: The fully qualified domain name of the host to locate in DDI.
    :param object session: The requests session object.
    :param str url: The full URL of the DDI server.
    :return: The JSON result of the operation.
    :rtype: str
    """
    logger.debug('Getting host info for: %s', fqdn)

    payload = {'WHERE': f"name='{fqdn}'"}
    r = session.get(url + 'rest/ip_address_list', params=payload)

    result = get_exceptions(r)

    return result


@cli.group()
@click.pass_context
def host(ctx):
    """Host based commands."""
    pass


@host.command()
@click.option('--building', '-b', help='The UCB building the host is in.',
              prompt=True, required=True)
@click.option('--comment', help='Additional comment for the host.')
@click.option('--contact', '-c', help='The UCB contact for the host.',
              prompt=True, required=True)
@click.option('--department', '-d',
              help='The UCB department the host belongs to.', prompt=True,
              required=True)
@click.option('--ip', '-i',
              help='The IPv4 address for the host as a dotted quad.',
              prompt=True, required=True)
@click.option('--phone', '-p',
              help='The UCB phone number associated with the host.',
              prompt=True, required=True)
@click.argument('host', envvar='DDI_HOST_ADD_HOST', nargs=1)
@click.pass_context
def add(ctx, building, comment, contact, department, ip, phone, host):
    """Add a single host entry into DDI."""

    logger.debug('Add operation called for host: %s at ip %s', host, ip)

    r = add_host(building, department, contact, ip, phone, host,
                 ctx.obj['session'], ctx.obj['url'], comment=comment)

    if ctx.obj['json']:
        data = jsend.success(r)
        click.echo(json.dumps(data, indent=2, sort_keys=True))
    else:
        click.echo(f'Host: {host} added with IP {ip}.')


@host.command()
@click.confirmation_option(prompt='Are you sure you want to delete the host?')
@click.argument('hosts', envvar='DDI_HOST_DELETE_HOSTS', nargs=-1)
@click.pass_context
def delete(ctx, hosts):
    """Delete the host(s) from DDI."""

    logger.debug('Delete operation called on hosts: %s.', hosts)

    for host in hosts:
        r = delete_host(host, ctx.obj['session'], ctx.obj['url'])
        if ctx.obj['json']:
            click.echo(json.dumps(r, indent=2, sort_keys=True))
        elif jsend.is_success(r):
            click.echo(f'Host: {host} deleted.')
        else:
            click.echo(f'Deletion of host:{host} failed.')


@host.command()
@click.argument('hosts', envvar='DDI_HOST_INFO_HOSTS', nargs=-1)
@click.pass_context
def info(ctx, hosts):
    """Provide information on the given host(s)."""

    logger.debug('Info operation called on hosts: %s.', hosts)

    for host in hosts:
        r = get_host(host, ctx.obj['session'], ctx.obj['url'])
        if ctx.obj['json']:
            click.echo(json.dumps(r, indent=2, sort_keys=True))
        elif jsend.is_success(r):
            echo_host_info(r)
        else:
            click.echo('Request failed, enable debugging for more.')
            ctx.exit(1)
