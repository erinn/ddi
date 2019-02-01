import ddi
from ddi.host import *
from click.testing import CliRunner


def test_host():

    runner = CliRunner()
    result = runner.invoke(host, '--help')
    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_host_info():

    runner = CliRunner()
    result = runner.invoke(host, ['info', '--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output
