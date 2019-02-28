from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from ddi.cli import initiate_session
from ddi.ipv4 import *

import base64
import jsend
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


def test_get_free_ipv4(client):
    recorder = Betamax(client)

    with recorder.use_cassette('ddi_get_free_ipv4'):
        result = get_free_ipv4(subnet=subnet, session=client, url=ddi_url)
        failed_result = get_free_ipv4(subnet=errant_subnet, session=client, url=ddi_url)

    assert isinstance(result, dict)
    assert jsend.is_success(result)
    assert len(result['data']['results']) == 10

    assert isinstance(failed_result, dict)
    assert jsend.is_fail(failed_result)


def test_get_ipv4_info(client):
    recorder = Betamax(client)

    with recorder.use_cassette('ddi_get_ipv4'):
        result = get_ipv4_info(ip=ipv4_address, session=client, url=ddi_url)
        failed_result = get_ipv4_info(ip=errant_ipv4_address, session=client, url=ddi_url)

    assert isinstance(result, dict)
    assert jsend.is_success(result)
    assert result['data']['results'][0]['name'] == ddi_host

    assert isinstance(failed_result, dict)
    assert jsend.is_fail(failed_result)
