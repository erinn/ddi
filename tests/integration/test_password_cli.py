from click.testing import CliRunner
from ddi.password import *


def test_password():
    runner = CliRunner()
    result = runner.invoke(password, ['--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_password_set():
    runner = CliRunner()
    result = runner.invoke(password, ['set', '--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output

    test_user = 'ddi-test-user'

    obj = {'username': test_user}
    result = runner.invoke(password, ['set'], obj=obj, input='foobar\nfoobar\n')

    assert result.exit_code == 0
    assert f'Password set for user: {test_user}' in result.output
