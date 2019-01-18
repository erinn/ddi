from ddi.cli import cli
import click


@cli.group()
@click.pass_context
def host(ctx):
    """Host based commands"""


@host.command()
@click.argument('hosts', envvar='DDI_HOST_HOSTS', nargs=-1)
@click.pass_context
def info(ctx, hosts):
    """Provide the DDI info on the given host(s)"""
    for host in hosts:
        click.echo('Host: {}!'.format(host))


@host.command()
@click.confirmation_option(prompt='Are you sure you want to delete the host?')
@click.pass_context
def delete(ctx):
    click.echo("deleted host!")
