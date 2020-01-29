import base64
import click
import ddi
import getpass
import keyring
import logging
import requests
import url_normalize

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

    username = base64.b64encode(username.encode()).decode()
    password = base64.b64encode(password.encode()).decode()

    headers = {'X-IPM-Username': username,
               'X-IPM-Password': password}

    session = requests.Session()
    session.verify = secure
    session.headers = headers

    logger.debug('Session initiated.')

    return session


@click.group()
@click.option('--debug', '-D', default=False, help='Enable debug output.',
              is_flag=True, show_default=True)
@click.option('--secure', '-S', default=True, help='TLS verification.',
              is_flag=True, show_default=True)
@click.option('--json', '-J', default=False, help='Output in JSON using the JSEND standard.',
              is_flag=True, show_default=True)
@click.option('--password', '-P', callback=cli_password, help="The DDI user's password.")
@click.option('--server', '-s', help="The DDI server's URL to connect to.",
              prompt=True, required=True)
@click.option('--username', '-U', default=getpass.getuser(),
              help='The DDI username.', is_eager=True, required=True, show_default=True)
@click.version_option(version=ddi.__version__)
@click.pass_context
def cli(ctx, debug, json, password, secure, server, username):
    """DDI Commands.

        All options can either be taken in on the command line or via an
        environment variable that is prefixed with 'DDI_'. For example to enable
        debugging using an env variable set 'DDI_DEBUG=True'. Or to disable
        TLS verification set DDI_SECURE=False. All options can be consumed
        in this manner.

        Environment variables also work with nested commands. For example to
        pass in the list of hosts to delete you would set 'DDI_HOST_DELETE_HOSTS'
        equal to a space separated list of the hosts to delete.

        Passwords are a special case, they can be passed in on the command line,
        via a environment variable 'DDI_PASSWORD' or pulled in via the systems
        keyring (OSX Keychain, Kwallet and similar on KDE/GNOME, or Windows
        Credential Locker). In order to use the system keyring the password must
        first be set in the keyring using 'ddi password set'. Ensure that the
        default username is correct, or set it via -u or DDI_USERNAME before
        setting the password.
    """
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
    ctx.obj['server'] = url_normalize.url_normalize(server)
    ctx.obj['session'] = session
    ctx.obj['url'] = ctx.obj['server']
    ctx.obj['username'] = username
