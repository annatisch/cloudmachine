
from uuid import uuid4

import pytest
from azure.cloudmachine.resources.ai import AIServices
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine._parameters import GLOBAL_PARAMS
from azure.cloudmachine._resource import FieldType
from azure.cloudmachine._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.cloudmachine import Parameter

TEST_SUB = str(uuid4())
RG = ResourceSymbol('resourcegroup')
IDENTITY = {
    'type': 'UserAssigned',
    'userAssignedIdentities': {ResourceSymbol('userassignedidentity'): {}}
}

def _get_outputs(suffix="", rg=None):
    return [
        Output(f"AZURE_AI_ID{suffix.upper()}", "id", ResourceSymbol(f"account{suffix}")),
        Output(f"AZURE_AI_NAME{suffix.upper()}", "name", ResourceSymbol(f"account{suffix}")),
        Output(f"AZURE_AI_RESOURCE_GROUP{suffix.upper()}", rg if rg else DefaultResourceGroup().name),
        Output(f"AZURE_AI_ENDPOINT{suffix.upper()}", "properties.endpoint", ResourceSymbol(f"account{suffix}"))
    ]

def test_aiservices_properties():
    r = AIServices()
    assert r.properties == {'kind': 'AIServices', 'properties': {}}
    assert r.extensions == {}
    assert r._existing == False
    assert not r._parent
    assert r.resource == "Microsoft.CognitiveServices/accounts"
    assert r.version
    fields = {}
    symbol = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.account']
    assert fields['__main__.account'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.account'].properties == {'kind': 'AIServices', 'properties': {}, 'identity': IDENTITY}
    assert fields['__main__.account'].outputs == _get_outputs()
    assert fields['__main__.account'].extensions == {}
    assert fields['__main__.account'].existing == False
    assert fields['__main__.account'].version
    assert fields['__main__.account'].symbol == symbol
    assert fields['__main__.account'].resource_group == RG
    assert not fields['__main__.account'].name
    assert fields['__main__.account'].add_defaults

    r2 = AIServices(location='westus', sku='F1')
    assert r2.properties == {'kind': 'AIServices', 'location': 'westus', 'sku': {'name': 'F1'}, 'properties': {}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.account']
    assert fields['__main__.account'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.account'].properties == {'kind': 'AIServices', 'location': 'westus', 'sku': {'name': 'F1'}, 'properties': {}, 'identity': IDENTITY}
    assert fields['__main__.account'].outputs == _get_outputs()
    assert fields['__main__.account'].extensions == {}
    assert fields['__main__.account'].existing == False
    assert fields['__main__.account'].version
    assert fields['__main__.account'].symbol == symbol
    assert fields['__main__.account'].resource_group == RG
    assert not fields['__main__.account'].name
    assert fields['__main__.account'].add_defaults

    r3 = AIServices(sku='C3')
    assert r3.properties == {'kind': 'AIServices', 'sku': {'name': 'C3'}, 'properties': {}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = AIServices(name='foo', tags={'test': 'value'}, public_network_access='Disabled')
    assert r4.properties == {'name': 'foo', 'kind': 'AIServices', 'tags': {'test': 'value'}, 'properties': {'publicNetworkAccess': 'Disabled'}}
    symbol = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.account', '__main__.account_foo']
    assert fields['__main__.account_foo'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.account_foo'].properties == {'name': 'foo', 'kind': 'AIServices', 'tags': {'test': 'value'}, 'properties': {'publicNetworkAccess': 'Disabled'}, 'identity': IDENTITY}
    assert fields['__main__.account_foo'].outputs == _get_outputs("_foo")
    assert fields['__main__.account_foo'].extensions == {}
    assert fields['__main__.account_foo'].existing == False
    assert fields['__main__.account_foo'].version
    assert fields['__main__.account_foo'].symbol == symbol
    assert fields['__main__.account_foo'].resource_group == RG
    assert fields['__main__.account_foo'].name == 'foo'
    assert fields['__main__.account_foo'].add_defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = AIServices(name=param1, sku=param2, public_network_access=param3)
    assert r5.properties == {'name': param1, 'kind': 'AIServices', 'sku': {'name': param2}, 'properties': {'publicNetworkAccess': param3}}
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbol = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.account_testa']
    assert fields['__main__.account_testa'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.account_testa'].properties == {'name': param1, 'kind': 'AIServices', 'sku': {'name': param2}, 'properties': {'publicNetworkAccess': param3}, 'identity': IDENTITY}
    assert fields['__main__.account_testa'].outputs == _get_outputs("_testa")
    assert fields['__main__.account_testa'].extensions == {}
    assert fields['__main__.account_testa'].existing == False
    assert fields['__main__.account_testa'].version
    assert fields['__main__.account_testa'].symbol == symbol
    assert fields['__main__.account_testa'].resource_group == RG
    assert fields['__main__.account_testa'].name == param1
    assert fields['__main__.account_testa'].add_defaults
    assert params.get('testA') == param1
    assert params.get('testB') == param2
    assert params.get('testC') == param3


def test_aiservices_reference():
    r = AIServices.reference(name='foo')
    assert r.properties == {'name': 'foo'}
    assert r._existing == True
    assert not r._parent
    assert r.extensions == {}
    assert r.name() == 'foo'
    with pytest.raises(RuntimeError):
        r.resource_group()
    with pytest.raises(RuntimeError):
        r.subscription()
    with pytest.raises(RuntimeError):
        r.resource_id()
    fields = {}
    symbol = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.account_foo']
    assert fields['__main__.account_foo'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.account_foo'].properties == {'name': 'foo', 'scope': RG}
    assert fields['__main__.account_foo'].outputs == _get_outputs("_foo")
    assert fields['__main__.account_foo'].extensions == {}
    assert fields['__main__.account_foo'].existing == True
    assert fields['__main__.account_foo'].version
    assert fields['__main__.account_foo'].symbol == symbol
    assert fields['__main__.account_foo'].resource_group == RG
    assert fields['__main__.account_foo'].name == 'foo'
    assert not fields['__main__.account_foo'].add_defaults

    rg = ResourceSymbol('resourcegroup_bar')
    r = AIServices.reference(name='foo', resource_group='bar')
    assert r.properties == {'name': 'foo', 'resource_group': ResourceGroup(name='bar')}
    assert r.resource_group() == 'bar'
    fields = {}
    symbol = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup_bar', '__main__.account_foo']
    assert fields['__main__.account_foo'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.account_foo'].properties == {'name': 'foo', 'scope': rg}
    assert fields['__main__.account_foo'].outputs == _get_outputs("_foo", 'bar')
    assert fields['__main__.account_foo'].extensions == {}
    assert fields['__main__.account_foo'].existing == True
    assert fields['__main__.account_foo'].version
    assert fields['__main__.account_foo'].symbol == symbol
    assert fields['__main__.account_foo'].resource_group == rg
    assert fields['__main__.account_foo'].name == 'foo'
    assert not fields['__main__.account_foo'].add_defaults

    r = AIServices.reference(name='foo', resource_group=ResourceGroup.reference(name='bar', subscription=TEST_SUB))
    assert r.properties == {'name': 'foo', 'resource_group': ResourceGroup(name='bar')}
    assert r.subscription() == TEST_SUB
    assert r.resource_id() == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.CognitiveServices/accounts/foo"


def test_aiservices_defaults():
    sku_param = Parameter('AISku', default='S0')
    r = AIServices(location='westus', sku=sku_param, public_network_access='Disabled')
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    field = fields.popitem()[1]
    r._add_defaults(field, parameters=dict(GLOBAL_PARAMS))
    assert field.properties == {
        'name': GLOBAL_PARAMS['defaultName'],
        'location': 'westus',
        'sku': {
            'name': sku_param
        },
        'kind': 'AIServices',
        'properties': {
            'publicNetworkAccess': 'Disabled',
            'disableLocalAuth': True
        },
        'identity': IDENTITY,
        'tags': GLOBAL_PARAMS['azdTags']
    }
