from click.testing import CliRunner
from ddi.password import set_


# A silly test but it validates that testing works.
def test_password_set_help():
    runner = CliRunner()
    result = runner.invoke(set_, ['--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output
