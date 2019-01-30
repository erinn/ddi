from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from click.testing import CliRunner
from ddi.cli import initiate_session
from ddi.host import *

import base64
import os
import pytest

ddi_host = os.environ.get('DDI_HOST', 'ddi-test-host.example.com')
ddi_password = os.environ.get('DDI_PASSWORD', 'test_password')
ddi_server = os.environ.get('DDI_SERVER', 'httpd://ddi.example.com')
ddi_url = ddi_server + '/rest/'
ddi_username = os.environ.get('DDI_USERNAME', 'test_user')


# Makes the output more readable
Betamax.register_serializer(PrettyJSONSerializer)

config = Betamax.configure()
config.cassette_library_dir = 'tests/integration/cassettes'
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
    }
]


@pytest.fixture(scope='module')
def client():
    return initiate_session(ddi_password, False, ddi_username)


def test_get_host(client):
    recorder = Betamax(client)
    with recorder.use_cassette('ddi_get_host', serialize_with='prettyjson'):
        result = get_host(ddi_host, client, ddi_url)

    assert isinstance(result, list)
    assert result[0]['name'] == ddi_host


def test_hexlify_address():
    assert hexlify_address('127.0.0.1') == b'7f000001'


def test_unhexlify_address():
    assert unhexlify_address('7f000001') == '127.0.0.1'
