from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from click.testing import CliRunner
from ddi.cli import initiate_session
from ddi.host import *

import base64
import os
import pytest
import url_normalize

ddi_host = os.environ.get('DDI_HOST', 'ddi-test-host.example.com')
ddi_password = os.environ.get('DDI_PASSWORD', 'test_password')
ddi_server = os.environ.get('DDI_SERVER', 'https://ddi.example.com')
ddi_site_name = os.environ.get('DDI_SITE_NAME', 'EXAMPLE')
ddi_url = url_normalize.url_normalize(ddi_server)
ddi_username = os.environ.get('DDI_USERNAME', 'test_user')
domain_name = os.environ.get('DOMAINNAME', 'example.com')
errant_ddi_host = 'bad-host.example.com'

# Makes the output more readable
Betamax.register_serializer(PrettyJSONSerializer)

config = Betamax.configure()
config.cassette_library_dir = 'tests/cassettes'
config.default_cassette_options['serialize_with'] = 'prettyjson'
config.default_cassette_options['placeholders'] = [
    {
        'placeholder': '<PASSWORD>',
        'replace': base64.b64encode(ddi_password.encode()).decode()
    },
    {
        'placeholder': '<LOGIN>',
        'replace': base64.b64encode(ddi_username.encode()).decode()
    },
    {
        'placeholder': '<DDI_SERVER>',
        'replace': ddi_server
    },
    {
        'placeholder': '<DDI_HOST>',
        'replace': ddi_host
    },
    {
        'placeholder': 'example.com',
        'replace': domain_name
    },
    {
        'placeholder': 'EXAMPLE',
        'replace': ddi_site_name
    },
]


@pytest.fixture()
def client():
    return initiate_session(ddi_password, False, ddi_username)


def test_host():

    runner = CliRunner()
    result = runner.invoke(host, '--help')
    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_host_add(client):

    runner = CliRunner()
    result = runner.invoke(host, ['info', '--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output

    recorder = Betamax(client)

    obj = {'session': client, 'url': ddi_url, 'json': False}
    jobj ={'session': client, 'url': ddi_url, 'json': True}

    with recorder.use_cassette('cli_host_add'):
        cli_result = runner.invoke(host, ['add', ddi_host, '-b', 'TEST',
                                          '-d TEST', '-c', 'Test User',
                                          '-i', '172.23.23.4', '-p',
                                          '555-1212', '--comment',
                                          'Test Comment"'],
                                   obj=obj)
        cli_json_result = runner.invoke(host, ['add', ddi_host, '-b', 'TEST',
                                               '-d TEST', '-c', 'Test User',
                                               '-i', '172.23.23.4', '-p',
                                               '555-1212', '--comment',
                                               'Test Comment"'],
                                        obj=jobj)

    assert cli_result.exit_code == 0
    assert f'Host: {ddi_host} added' in cli_result.stdout

    assert cli_json_result.exit_code == 0
    assert '"data"' in cli_json_result.stdout


def test_host_info(client):

    runner = CliRunner()
    result = runner.invoke(host, ['info', '--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output

    recorder = Betamax(client)

    obj = {'session': client, 'url': ddi_url, 'json': False}
    jobj ={'session': client, 'url': ddi_url, 'json': True}

    with recorder.use_cassette('cli_host_info'):
        cli_result = runner.invoke(host, ['info', ddi_host], obj=obj)
        cli_json_result = runner.invoke(host, ['info', ddi_host], obj=jobj)
        failed_result = runner.invoke(host, ['info', errant_ddi_host], obj=obj)

    assert cli_result.exit_code == 0
    assert f'Hostname: {ddi_host}' in cli_result.stdout

    assert cli_json_result.exit_code == 0
    assert '"data"' in cli_json_result.stdout

    assert failed_result.exit_code == 1
    assert "Request failed" in failed_result.stdout


def test_host_delete(client):
    """
    Test the deletion of a host object via the CLI. The keen observer will
    notice that this test is not in alphabetical order, this is needed due
    to the fact that you can't get a hosts' information after the host
    has been deleted :).
    """
    runner = CliRunner()
    result = runner.invoke(host, ['info', '--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output

    recorder = Betamax(client)

    obj = {'session': client, 'url': ddi_url, 'json': False}
    jobj ={'session': client, 'url': ddi_url, 'json': True}

    with recorder.use_cassette('cli_host_delete'):
        cli_result = runner.invoke(host, ['delete', ddi_host, '--yes'], obj=obj)
        cli_json_result = runner.invoke(host, ['delete', ddi_host, '--yes'], obj=jobj)
        failed_result = runner.invoke(host, ['delete', errant_ddi_host, '--yes'], obj=obj)

    assert cli_result.exit_code == 0
    assert f'Host: {ddi_host} deleted.' in cli_result.stdout

    assert cli_json_result.exit_code == 0
    assert '"data"' in cli_json_result.stdout

    assert failed_result.exit_code == 1
    assert "Request failed" in failed_result.stdout

