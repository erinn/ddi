import ddi
from ddi.cli import *
from click.testing import CliRunner


# A silly test but it validates that testing works.
def test_cli_version():

    runner=CliRunner()
    result = runner.invoke(cli, '--version')
    assert result.exit_code == 0
    assert ddi.__version__ in result.output
