from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from click.testing import CliRunner
from ddi.cli import initiate_session
from ddi.ipv4 import *

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

# Test variables:
errant_ipv4_address = '1.1.1.1'
errant_subnet='1.1.1.0'
ipv4_address = '172.23.23.4'
subnet = '172.23.23.0'

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


def test_ipv4():

    runner = CliRunner()
    result = runner.invoke(ipv4, '--help')
    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_ipv4_info(client):

    runner = CliRunner()
    result = runner.invoke(ipv4, ['info', '--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output

    recorder = Betamax(client)

    obj = {'session': client, 'url': ddi_url, 'json': False}
    jobj ={'session': client, 'url': ddi_url, 'json': True}

    with recorder.use_cassette('cli_ipv4_info'):
        cli_result = runner.invoke(ipv4, ['info', ipv4_address], obj=obj)
        cli_json_result = runner.invoke(ipv4, ['info', ipv4_address], obj=jobj)
        failed_cli_result = runner.invoke(ipv4, ['info', errant_ipv4_address], obj=obj)
        failed_json_cli_result = runner.invoke(ipv4, ['info', errant_ipv4_address], obj=jobj)

    assert cli_result.exit_code == 0
    assert f'Hostname: {ddi_host}' in cli_result.stdout

    assert cli_json_result.exit_code == 0
    assert '"data"' in cli_json_result.stdout

    assert failed_cli_result.exit_code == 1

    assert 'failed' in failed_cli_result.stdout
