from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from ddi.cli import initiate_session
from ddi.subnet import *

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
subnet = '172.23.23.0'
errant_subnet = '1.1.1.0'

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


def test_get_subnet_info(client):
    recorder = Betamax(client)

    with recorder.use_cassette('ddi_get_subnet'):
        result = get_subnet_info(subnet=subnet, session=client, url=ddi_url)
        failed_result = get_subnet_info(subnet=errant_subnet, session=client, url=ddi_url)

    assert isinstance(result, dict)
    assert jsend.is_success(result)
    assert 'subnet_id' in result['data']['results'][0]

    assert isinstance(failed_result, dict)
    assert jsend.is_fail(failed_result)
