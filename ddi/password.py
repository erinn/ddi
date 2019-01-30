from ddi.cli import cli
import click
import ddi
import keyring
import logging

logger = logging.getLogger(__name__)


@cli.group()
@click.pass_context
def password(ctx):
    """Password commands"""
    pass


@password.command()
@click.pass_context
def set(ctx):
    """Set the password in the system keyring."""
    logger.debug('Setting password for user: %s', ctx.obj['username'])
    p = click.prompt(f"{ddi.__name__} password for {ctx.obj['username']}",
                     hide_input=True, confirmation_prompt=True)
    k = keyring.get_keyring()
    k.set_password(ddi.__name__, ctx.obj['username'], p)
    click.echo(f"Password set for user: {ctx.obj['username']} in keychain: "
               f"{k.name}")
