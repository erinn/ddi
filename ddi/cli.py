from ddi import __version__
import base64
import click
import requests


def initiate_session(username: str, password: str):
    """
    This initializes a requests session object with the proper headers for authentication.

    :param str username: The user name
    :param str password: The password
    :return: The requests session object
    :rtype: object
    """

    username = base64.b64encode(username.encode())
    password = base64.b64encode(password.encode())

    headers = {'X-IPM-Username': username,
               'X-IPM-Password': password}

    session = requests.Session()
    session.verify = False
    session.headers = headers

    return session


@click.group()
@click.option('--debug', '-d', is_flag=True, default=False, help='Enable debug output.')
@click.option('--json', '-j', is_flag=True, default=False, help='Output in JSON.')
@click.option('--password', '-p', prompt=True, hide_input=True, help="The DDI user's password.")
@click.option('--server', '-s', prompt=True, help="The DDI server's URL to connect to.")
@click.option('--username', '-u', help='The DDI username.')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, debug, json, password, server, username):
    session = initiate_session(username, password)

    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['json'] = json
    ctx.obj['server'] = server
    ctx.obj['session'] = session





