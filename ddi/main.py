
from ddi.cli import cli
import ddi.host
import ddi.password


def main():
    cli(auto_envvar_prefix='DDI', obj={})
