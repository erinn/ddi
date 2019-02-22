from ddi.cli import cli
import ddi.cname
import ddi.host
import ddi.ipv4
import ddi.password
import ddi.subnet


def main():
    cli(auto_envvar_prefix='DDI', obj={})
