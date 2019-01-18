
from ddi.cli import cli
import ddi.host


def main():
    cli(auto_envvar_prefix='DDI', obj={})
