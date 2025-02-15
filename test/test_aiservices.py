
from uuid import uuid4

import pytest
from azure.cloudmachine.resources.ai import AIServices, CognitiveServicesAccount
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine._parameters import GLOBAL_PARAMS
from azure.cloudmachine.resources._identifiers import ResourceIdentifiers
from azure.cloudmachine._resource import FieldType
from azure.cloudmachine._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.cloudmachine import Parameter, resource, AzureInfrastructure, export

TEST_SUB = str(uuid4())
RG = ResourceSymbol('resourcegroup')
IDENTITY = {
    'type': 'UserAssigned',
    'userAssignedIdentities': {GLOBAL_PARAMS['managedIdentityId'].format(): {}}
}

def _get_outputs(suffix="", rg=None):
    return {
        'resource_id': Output(f"AZURE_AI_AISERVICES_ID{suffix.upper()}", "id", ResourceSymbol(f"aiservices_account{suffix}")),
        'name': Output(f"AZURE_AI_AISERVICES_NAME{suffix.upper()}", "name", ResourceSymbol(f"aiservices_account{suffix}")),
        'resource_group': Output(f"AZURE_AI_AISERVICES_RESOURCE_GROUP{suffix.upper()}", rg if rg else DefaultResourceGroup().name),
        'endpoint': Output(f"AZURE_AI_AISERVICES_ENDPOINT{suffix.upper()}", "properties.endpoint", ResourceSymbol(f"aiservices_account{suffix}"))
    }

def test_aiservices_properties():
    r = AIServices()
    assert r.properties == {'kind': 'AIServices', 'properties': {}}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.CognitiveServices/accounts"
    assert r.version
    fields = {}
    symbol = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.aiservices_account']
    assert fields['__main__.aiservices_account'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.aiservices_account'].properties == {'kind': 'AIServices', 'properties': {}}
    assert fields['__main__.aiservices_account'].outputs == _get_outputs()
    assert fields['__main__.aiservices_account'].extensions == {}
    assert fields['__main__.aiservices_account'].existing == False
    assert fields['__main__.aiservices_account'].version
    assert fields['__main__.aiservices_account'].symbol == symbol
    assert fields['__main__.aiservices_account'].resource_group == RG
    assert not fields['__main__.aiservices_account'].name
    assert fields['__main__.aiservices_account'].add_defaults

    r2 = AIServices(location='westus', sku='F1')
    assert r2.properties == {'kind': 'AIServices', 'location': 'westus', 'sku': {'name': 'F1'}, 'properties': {}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.aiservices_account']
    assert fields['__main__.aiservices_account'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.aiservices_account'].properties == {'kind': 'AIServices', 'location': 'westus', 'sku': {'name': 'F1'}, 'properties': {}}
    assert fields['__main__.aiservices_account'].outputs == _get_outputs()
    assert fields['__main__.aiservices_account'].extensions == {}
    assert fields['__main__.aiservices_account'].existing == False
    assert fields['__main__.aiservices_account'].version
    assert fields['__main__.aiservices_account'].symbol == symbol
    assert fields['__main__.aiservices_account'].resource_group == RG
    assert not fields['__main__.aiservices_account'].name
    assert fields['__main__.aiservices_account'].add_defaults

    r3 = AIServices(sku='C3')
    assert r3.properties == {'kind': 'AIServices', 'sku': {'name': 'C3'}, 'properties': {}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = AIServices(name='foo', tags={'test': 'value'}, public_network_access='Disabled')
    assert r4.properties == {'name': 'foo', 'kind': 'AIServices', 'tags': {'test': 'value'}, 'properties': {'publicNetworkAccess': 'Disabled'}}
    symbol = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.aiservices_account', '__main__.aiservices_account_foo']
    assert fields['__main__.aiservices_account_foo'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.aiservices_account_foo'].properties == {'name': 'foo', 'kind': 'AIServices', 'tags': {'test': 'value'}, 'properties': {'publicNetworkAccess': 'Disabled'}}
    assert fields['__main__.aiservices_account_foo'].outputs == _get_outputs("_foo")
    assert fields['__main__.aiservices_account_foo'].extensions == {}
    assert fields['__main__.aiservices_account_foo'].existing == False
    assert fields['__main__.aiservices_account_foo'].version
    assert fields['__main__.aiservices_account_foo'].symbol == symbol
    assert fields['__main__.aiservices_account_foo'].resource_group == RG
    assert fields['__main__.aiservices_account_foo'].name == 'foo'
    assert fields['__main__.aiservices_account_foo'].add_defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = AIServices(name=param1, sku=param2, public_network_access=param3)
    assert r5.properties == {'name': param1, 'kind': 'AIServices', 'sku': {'name': param2}, 'properties': {'publicNetworkAccess': param3}}
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbol = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.aiservices_account_testa']
    assert fields['__main__.aiservices_account_testa'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.aiservices_account_testa'].properties == {'name': param1, 'kind': 'AIServices', 'sku': {'name': param2}, 'properties': {'publicNetworkAccess': param3}}
    assert fields['__main__.aiservices_account_testa'].outputs == _get_outputs("_testa")
    assert fields['__main__.aiservices_account_testa'].extensions == {}
    assert fields['__main__.aiservices_account_testa'].existing == False
    assert fields['__main__.aiservices_account_testa'].version
    assert fields['__main__.aiservices_account_testa'].symbol == symbol
    assert fields['__main__.aiservices_account_testa'].resource_group == RG
    assert fields['__main__.aiservices_account_testa'].name == param1
    assert fields['__main__.aiservices_account_testa'].add_defaults
    assert params.get('testA') == param1
    assert params.get('testB') == param2
    assert params.get('testC') == param3


def test_aiservices_reference():
    r = AIServices.reference(name='foo')
    assert r.properties == {'name': 'foo', 'kind': 'AIServices'}
    assert r._existing == True
    assert not r.parent
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
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.aiservices_account_foo']
    assert fields['__main__.aiservices_account_foo'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.aiservices_account_foo'].properties == {'name': 'foo', 'scope': RG, 'kind': 'AIServices'}
    assert fields['__main__.aiservices_account_foo'].outputs == _get_outputs("_foo")
    assert fields['__main__.aiservices_account_foo'].extensions == {}
    assert fields['__main__.aiservices_account_foo'].existing == True
    assert fields['__main__.aiservices_account_foo'].version
    assert fields['__main__.aiservices_account_foo'].symbol == symbol
    assert fields['__main__.aiservices_account_foo'].resource_group == RG
    assert fields['__main__.aiservices_account_foo'].name == 'foo'
    assert not fields['__main__.aiservices_account_foo'].add_defaults

    rg = ResourceSymbol('resourcegroup_bar')
    r = AIServices.reference(name='foo', resource_group='bar')
    assert r.properties == {'name': 'foo', 'resource_group': ResourceGroup(name='bar'), 'kind': 'AIServices'}
    assert r.resource_group() == 'bar'
    fields = {}
    symbol = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup_bar', '__main__.aiservices_account_foo']
    assert fields['__main__.aiservices_account_foo'].resource == "Microsoft.CognitiveServices/accounts"
    assert fields['__main__.aiservices_account_foo'].properties == {'name': 'foo', 'scope': rg, 'kind': 'AIServices'}
    assert fields['__main__.aiservices_account_foo'].outputs == _get_outputs("_foo", 'bar')
    assert fields['__main__.aiservices_account_foo'].extensions == {}
    assert fields['__main__.aiservices_account_foo'].existing == True
    assert fields['__main__.aiservices_account_foo'].version
    assert fields['__main__.aiservices_account_foo'].symbol == symbol
    assert fields['__main__.aiservices_account_foo'].resource_group == rg
    assert fields['__main__.aiservices_account_foo'].name == 'foo'
    assert not fields['__main__.aiservices_account_foo'].add_defaults

    r = AIServices.reference(name='foo', resource_group=ResourceGroup.reference(name='bar', subscription=TEST_SUB))
    assert r.properties == {'name': 'foo', 'resource_group': ResourceGroup(name='bar'), 'kind': 'AIServices'}
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
        'name': GLOBAL_PARAMS['defaultName'].format("{}-aiservices"),
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

def test_aiservices_export(export_dir):
    r = AIServices()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_aiservices_export_existing(export_dir):
    r = AIServices.reference(name='aitest', resource_group='aitest')
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_aiservices_export_with_properties(export_dir):
    r = AIServices(sku='C2', location="westus", public_network_access='Disabled')
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_aiservices_export_with_role_assignments(export_dir):
    user_role = Parameter("UserRole")
    r = AIServices(roles=['Cognitive Services OpenAI Contributor'], user_roles=['Cognitive Services OpenAI User'])
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_aiservices_export_with_no_user_access(export_dir):
    r = AIServices(roles=['Cognitive Services OpenAI Contributor'], user_roles=['Cognitive Services OpenAI User'])
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test", user_access=False)


def test_aiservices_export_multiple_cogservices(export_dir):
    c = CognitiveServicesAccount(kind='MetricsAdvisor')
    r = AIServices()
    export(c, r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_aiservices_export_multiple_ai(export_dir):
    r1 = AIServices(disable_local_auth=False)
    r2 = AIServices(disable_local_auth=Parameter("LocalAuth", default=True))
    with pytest.raises(ValueError):
        export(r1, r2, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")
    r2 = AIServices()
    export(r1, r2, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")

# TODO:
# def test_aiservices_export_with_parameters(export_dir):
