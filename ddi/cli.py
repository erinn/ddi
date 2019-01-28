import base64
import click
import ddi
import getpass
import keyring
import logging
import requests

logger = logging.getLogger(__name__)


# TODO: test all password variations
def cli_password(ctx, param, password):
    """
    This is a callback function that should only be used from the password
    option.

    Because password logic is a bit complex we use this callback to handle the
    multitude of options.
    :param object ctx: The ctx object from click.
    :param object param: The parameter object from click.
    :param str password: The password consumed (or not) by click.
    :return: The password or a non-zero exit.
    :rtype: str
    """

    username = ctx.params['username']

    logger.debug('Establishing password for user %s.', username)

    if password:
        logger.debug('Password established via the command line or environment '
                     'variable.')
        return password
    else:
        logger.debug('Password not passed in, attempting to extract from '
                     'keyring location: %s.', ddi.__name__)
        keyring.get_keyring()
        password = keyring.get_password(ddi.__name__, username)
        if password:
            logger.debug('Password obtained from keyring.')
            return password
        else:
            logger.debug('No password was obtained from the keyring.')

            click.echo('No password was found in the environment variable, '
                       'passed in on the command line, or found in the keyring. '
                       'If you wish to use a password in the keyring please use '
                       "'ddi password set'.")
            ctx.exit(code=1)

    # Should never be reached
    return None


def initiate_session(password: str, secure: bool, username: str):
    """
    This initializes a requests session object with the proper headers for authentication.

    :param str password: The password
    :param bool secure: Setting this to False disables verification of TLS
    :param str username: The user name
    :return: The requests session object
    :rtype: object
    """

    logger.debug('Initiating session with TLS verification set to: %s.', secure)

    username = base64.b64encode(username.encode())
    password = base64.b64encode(password.encode())

    headers = {'X-IPM-Username': username,
               'X-IPM-Password': password}

    session = requests.Session()
    session.verify = secure
    session.headers = headers

    logger.debug('Session initiated.')

    return session


@click.group()
@click.option('--debug', '-d', default=False, help='Enable debug output.',
              is_flag=True, show_default=True)
@click.option('--secure', '-S', default=True, help='TLS verification.',
              is_flag=True, show_default=True)
@click.option('--json', '-j', default=False, help='Output in JSON.',
              is_flag=True, show_default=True)
# TODO: use keyring to store passwords if possible
@click.option('--password', '-p', callback=cli_password, help="The DDI user's password.")
@click.option('--server', '-s', help="The DDI server's URL to connect to.",
              prompt=True, required=True)
@click.option('--username', '-u', default=getpass.getuser(),
              help='The DDI username.', is_eager=True, required=True, show_default=True)
@click.version_option(version=ddi.__version__)
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
    ctx.obj['username'] = username
