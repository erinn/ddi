from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from ddi.cli import initiate_session
from ddi.cname import *

import base64
import jsend
import os
import pytest
import url_normalize

ddi_cname = os.environ.get('DDI_CNAME', 'ddi-test-cname.int.example.com')
ddi_host = os.environ.get('DDI_HOST', 'ddi-test-host.example.com')
ddi_password = os.environ.get('DDI_PASSWORD', 'test_password')
ddi_server = os.environ.get('DDI_SERVER', 'https://ddi.example.com')
ddi_site_name = os.environ.get('DDI_SITE_NAME', 'EXAMPLE')
ddi_url = url_normalize.url_normalize(ddi_server)
print(ddi_url)
ddi_username = os.environ.get('DDI_USERNAME', 'test_user')
domain_name = os.environ.get('DOMAINNAME', 'example.com')

# Makes the output more readable
Betamax.register_serializer(PrettyJSONSerializer)

config = Betamax.configure()
config.cassette_library_dir = 'tests/integration/cassettes'
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


@pytest.fixture(scope='module')
def client():
    return initiate_session(ddi_password, False, ddi_username)


def test_add_cname(client):
    recorder = Betamax(client)
    with recorder.use_cassette('ddi_add_cname'):
        host_data = get_host(fqdn=ddi_host, session=client, url=ddi_url)
        result = add_cname(cname=ddi_cname, host_data=host_data, session=client,
                           url=ddi_url)

        assert isinstance(result, dict)
        assert jsend.is_success(result)


def test_get_cname(client):
    recorder = Betamax(client)
    with recorder.use_cassette('ddi_get_cname'):
        result = get_cname_info(cname=ddi_cname, session=client, url=ddi_url)

    assert isinstance(result, list)
    assert result[0]['name'] == ddi_host


def test_delete_cname(client):
    recorder = Betamax(client)
    with recorder.use_cassette('ddi_delete_cname'):
        host_data = get_host(fqdn=ddi_host, session=client, url=ddi_url)
        result = delete_cname(cname=ddi_cname, host_data=host_data,
                              session=client, url=ddi_url)

    assert isinstance(result, dict)
    assert jsend.is_success(result)
