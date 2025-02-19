from uuid import uuid4

import pytest
from azure.cloudmachine._resource import FieldType
from azure.cloudmachine.resources.managedidentity import UserAssignedIdentity
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine._parameters import GLOBAL_PARAMS
from azure.cloudmachine.resources._identifiers import ResourceIdentifiers
from azure.cloudmachine._bicep.expressions import ResourceSymbol, Output
from azure.cloudmachine import Parameter, export, AzureInfrastructure, resource

TEST_SUB = '6ceba549-5d9d-47da-a5bb-72816776ba40'

def test_identity_properties():
    r = UserAssignedIdentity()
    assert r.properties == {}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS), module_name="test")
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity']
    assert fields['__main__.userassignedidentity'].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields['__main__.userassignedidentity'].properties == {}
    assert fields['__main__.userassignedidentity'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields['__main__.userassignedidentity'].extensions == {}
    assert fields['__main__.userassignedidentity'].existing == False
    assert fields['__main__.userassignedidentity'].version
    assert fields['__main__.userassignedidentity'].symbol == symbols[0]
    assert fields['__main__.userassignedidentity'].resource_group == ResourceSymbol('resourcegroup')
    assert not fields['__main__.userassignedidentity'].name
    assert fields['__main__.userassignedidentity'].add_defaults

    r2 = UserAssignedIdentity(location='westus')
    assert r2.properties == {'location': 'westus'}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS), module_name="test")
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity']
    assert fields['__main__.userassignedidentity'].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields['__main__.userassignedidentity'].properties == {'location': 'westus'}
    assert fields['__main__.userassignedidentity'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields['__main__.userassignedidentity'].extensions == {}
    assert fields['__main__.userassignedidentity'].existing == False
    assert fields['__main__.userassignedidentity'].version
    assert fields['__main__.userassignedidentity'].symbol == symbols[0]
    assert fields['__main__.userassignedidentity'].resource_group == ResourceSymbol('resourcegroup')
    assert not fields['__main__.userassignedidentity'].name
    assert fields['__main__.userassignedidentity'].add_defaults

    r3 = UserAssignedIdentity(location='eastus')
    assert r3.properties == {'location': 'eastus'}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS), module_name="test")

    r4 = UserAssignedIdentity(name='foo', tags={'test': 'value'})
    assert r4.properties == {'name': 'foo', 'tags': {'test': 'value'}}
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS), module_name="test")
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.userassignedidentity_foo']
    assert fields['__main__.userassignedidentity_foo'].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields['__main__.userassignedidentity_foo'].properties == {'name': 'foo', 'tags': {'test': 'value'}}
    assert fields['__main__.userassignedidentity_foo'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields['__main__.userassignedidentity_foo'].extensions == {}
    assert fields['__main__.userassignedidentity_foo'].existing == False
    assert fields['__main__.userassignedidentity_foo'].version
    assert fields['__main__.userassignedidentity_foo'].symbol == symbols[0]
    assert fields['__main__.userassignedidentity_foo'].resource_group == ResourceSymbol('resourcegroup')
    assert fields['__main__.userassignedidentity_foo'].name == 'foo'
    assert fields['__main__.userassignedidentity_foo'].add_defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    r5 = UserAssignedIdentity(name=param1, tags={"foo": param2})
    assert r5.properties == {'name': param1, 'tags': {'foo': param2}}
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params, module_name="test")
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity_testa']
    assert fields['__main__.userassignedidentity_testa'].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields['__main__.userassignedidentity_testa'].properties == {'name': param1, 'tags': {'foo': param2}}
    assert fields['__main__.userassignedidentity_testa'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields['__main__.userassignedidentity_testa'].extensions == {}
    assert fields['__main__.userassignedidentity_testa'].existing == False
    assert fields['__main__.userassignedidentity_testa'].version
    assert fields['__main__.userassignedidentity_testa'].symbol == symbols[0]
    assert fields['__main__.userassignedidentity_testa'].resource_group == ResourceSymbol('resourcegroup')
    assert fields['__main__.userassignedidentity_testa'].name == param1
    assert fields['__main__.userassignedidentity_testa'].add_defaults

    assert params.get('testA') == param1
    assert params.get('testB') == param2


def test_identity_reference():
    r = UserAssignedIdentity.reference(name='foo')
    assert r.properties == {'name': 'foo'}
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
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS), module_name="test")
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity_foo']
    assert fields['__main__.userassignedidentity_foo'].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields['__main__.userassignedidentity_foo'].properties == {'name': 'foo', 'scope': ResourceSymbol("resourcegroup")}
    assert fields['__main__.userassignedidentity_foo'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields['__main__.userassignedidentity_foo'].extensions == {}
    assert fields['__main__.userassignedidentity_foo'].existing == True
    assert fields['__main__.userassignedidentity_foo'].version
    assert fields['__main__.userassignedidentity_foo'].symbol == symbols[0]
    assert fields['__main__.userassignedidentity_foo'].resource_group == ResourceSymbol('resourcegroup')
    assert fields['__main__.userassignedidentity_foo'].name == 'foo'
    assert not fields['__main__.userassignedidentity_foo'].add_defaults

    r = UserAssignedIdentity.reference(name='bar', resource_group="rgtest")
    assert r.properties == {'name': 'bar', 'resource_group': ResourceGroup(name='rgtest')}
    assert r.resource_group() == 'rgtest'
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS), module_name="test")
    assert list(fields.keys()) == ['__main__.resourcegroup_rgtest', '__main__.userassignedidentity_bar']
    assert fields['__main__.userassignedidentity_bar'].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields['__main__.userassignedidentity_bar'].properties == {'name': 'bar', 'scope': ResourceSymbol("resourcegroup_rgtest")}
    assert fields['__main__.userassignedidentity_bar'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields['__main__.userassignedidentity_bar'].extensions == {}
    assert fields['__main__.userassignedidentity_bar'].existing == True
    assert fields['__main__.userassignedidentity_bar'].version
    assert fields['__main__.userassignedidentity_bar'].symbol == symbols[0]
    assert fields['__main__.userassignedidentity_bar'].resource_group == ResourceSymbol('resourcegroup_rgtest')
    assert fields['__main__.userassignedidentity_bar'].name == 'bar'
    assert not fields['__main__.userassignedidentity_bar'].add_defaults

    r = UserAssignedIdentity.reference(name='bar', resource_group=ResourceGroup.reference(name='rgtest', subscription=TEST_SUB))
    assert r.properties == {'name': 'bar', 'resource_group': ResourceGroup(name='rgtest')}
    assert r.resource_group() == 'rgtest'
    assert r.subscription() == TEST_SUB
    assert r.resource_id() == f"/subscriptions/{TEST_SUB}/resourceGroups/rgtest/providers/Microsoft.ManagedIdentity/userAssignedIdentities/bar"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS), module_name="test")
    assert list(fields.keys()) == ['__main__.resourcegroup_rgtest', '__main__.userassignedidentity_bar']
    assert fields['__main__.userassignedidentity_bar'].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields['__main__.userassignedidentity_bar'].properties == {'name': 'bar', 'scope': ResourceSymbol("resourcegroup_rgtest")}
    assert fields['__main__.userassignedidentity_bar'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields['__main__.userassignedidentity_bar'].extensions == {}
    assert fields['__main__.userassignedidentity_bar'].existing == True
    assert fields['__main__.userassignedidentity_bar'].version
    assert fields['__main__.userassignedidentity_bar'].symbol == symbols[0]
    assert fields['__main__.userassignedidentity_bar'].resource_group == ResourceSymbol('resourcegroup_rgtest')
    assert fields['__main__.userassignedidentity_bar'].name == 'bar'
    assert not fields['__main__.userassignedidentity_bar'].add_defaults


def test_identity_defaults():
    ua_name = Parameter('uaName')
    r = UserAssignedIdentity(name=ua_name)
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS), module_name="test")
    field: FieldType = fields.popitem()[1]
    r._add_defaults(field, parameters=dict(GLOBAL_PARAMS))
    assert field.properties == {
        'name': ua_name,
        'location': GLOBAL_PARAMS['location'],
        'tags': GLOBAL_PARAMS['azdTags']
    }

def test_identity_export(export_dir):
    r = UserAssignedIdentity()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_identity_export_with_properties(export_dir):
    r = UserAssignedIdentity(name='foo', location='westus', tags={'key': 'value'})
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_identity_export_with_parameter(export_dir):
    param = Parameter("testLocation")
    r = UserAssignedIdentity(location=param)
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test", config={"testLocation": "eastus"})


def test_identity_export_existing(export_dir):
    r = UserAssignedIdentity.reference(name="exists")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_identity_export_existing_with_resourcegroup(export_dir):
    r = UserAssignedIdentity.reference(name="exists", resource_group="rgexists")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_identity_export_existing_with_resourcegroup_and_subscription(export_dir):
    r = UserAssignedIdentity.reference(name="exists", resource_group=ResourceGroup.reference(name='rgexists', subscription=TEST_SUB))
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_identity_infra():
    class TestInfra(AzureInfrastructure):
        rg: UserAssignedIdentity = resource()
    
    assert isinstance(TestInfra.rg, UserAssignedIdentity)
    assert TestInfra.rg.infrastructure == TestInfra
    infra = TestInfra()
    assert isinstance(infra.rg, UserAssignedIdentity)
    assert infra.rg.properties == {}

    infra = TestInfra(rg=UserAssignedIdentity(name='foo'))
    assert infra.rg.name() == 'foo'

    #TODO: Finish testing default behaviours
    # assert resource(default=ResourceGroup.reference(name='foo'))
