import ddi
from ddi.host import *
from click.testing import CliRunner


def test_host_help():

    runner = CliRunner()
    result = runner.invoke(host, '--help')
    assert result.exit_code == 0
    assert 'Usage:' in result.output
