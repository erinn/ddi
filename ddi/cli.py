from ddi import __version__
import base64
import click
import logging
import requests


def initiate_session(password: str, secure: bool, username: str):
    """
    This initializes a requests session object with the proper headers for authentication.

    :param str password: The password
    :param bool secure: Setting this to False disables verification of TLS
    :param str username: The user name
    :return: The requests session object
    :rtype: object
    """

    username = base64.b64encode(username.encode())
    password = base64.b64encode(password.encode())

    headers = {'X-IPM-Username': username,
               'X-IPM-Password': password}

    session = requests.Session()
    session.verify = secure
    session.headers = headers

    return session


@click.group()
@click.option('--debug', '-d', is_flag=True, default=False, help='Enable debug output.')
@click.option('--secure', '-S', is_flag=True, default=True, help='Disable TLS verification.')
@click.option('--json', '-j', is_flag=True, default=False, help='Output in JSON.')
# TODO: use keyring to store passwords if possible
@click.option('--password', '-p', prompt=True, hide_input=True, help="The DDI user's password.")
@click.option('--server', '-s', prompt=True, help="The DDI server's URL to connect to.")
@click.option('--username', '-u', help='The DDI username.')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, debug, json, password, secure, server, username):
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    session = initiate_session(password, secure, username)

    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['json'] = json
    ctx.obj['server'] = server
    ctx.obj['session'] = session
    ctx.obj['url'] = ctx.obj['server'] + '/rest/'





