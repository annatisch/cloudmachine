from uuid import uuid4

import pytest
from azure.cloudmachine._resource import FieldType
from azure.cloudmachine.resources.managedidentity import UserAssignedIdentity, _add_defaults
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine._parameters import GLOBAL_PARAMS
from azure.cloudmachine._bicep.expressions import ResourceSymbol, Output
from azure.cloudmachine import Parameter

TEST_SUB = str(uuid4())

def test_identity_properties():
    r = UserAssignedIdentity()
    assert r.properties == {}
    assert r.extensions == {}
    assert r._existing == False
    assert not r._parent
    assert r.resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert r.version
    fields = {}
    symbol = r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity']
    assert fields['__main__.userassignedidentity'] == FieldType(
        resource="Microsoft.ManagedIdentity/userAssignedIdentities",
        properties={},
        outputs=[Output('AZURE_CLIENT_ID', "properties.clientId", symbol)],
        extensions={},
        existing=False,
        version="2024-11-30",
        symbol=symbol,
        resource_group=ResourceSymbol('resourcegroup')
    )

    r2 = UserAssignedIdentity(location='westus')
    assert r2.properties == {'location': 'westus'}
    r2.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity']
    assert fields['__main__.userassignedidentity'] == FieldType(
        resource="Microsoft.ManagedIdentity/userAssignedIdentities",
        properties={'location': 'westus'},
        outputs=[Output('AZURE_CLIENT_ID', "properties.clientId", symbol)],
        extensions={},
        existing=False,
        version="2024-11-30",
        symbol=symbol,
        resource_group=ResourceSymbol('resourcegroup')
    )

    r3 = UserAssignedIdentity(location='eastus')
    assert r3.properties == {'location': 'eastus'}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=GLOBAL_PARAMS)

    r4 = UserAssignedIdentity(name='foo', tags={'test': 'value'})
    assert r4.properties == {'name': 'foo', 'tags': {'test': 'value'}}
    symbol = r4.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.userassignedidentity_foo']
    assert fields['__main__.userassignedidentity_foo'] == FieldType(
        resource="Microsoft.ManagedIdentity/userAssignedIdentities",
        properties={'name': 'foo', 'tags': {'test': 'value'}},
        outputs=[Output('AZURE_CLIENT_ID', "properties.clientId", symbol)],
        extensions={},
        existing=False,
        version="2024-11-30",
        symbol=symbol,
        resource_group=ResourceSymbol('resourcegroup')
    )

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    r5 = UserAssignedIdentity(name=param1, tags={"foo": param2})
    assert r5.properties == {'name': param1, 'tags': {'foo': param2}}
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbol = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity_testa']
    assert fields['__main__.userassignedidentity_testa'] == FieldType(
        resource="Microsoft.ManagedIdentity/userAssignedIdentities",
        properties={'name': param1, 'tags': {'foo': param2}},
        outputs=[Output('AZURE_CLIENT_ID', "properties.clientId", symbol)],
        extensions={},
        existing=False,
        version="2024-11-30",
        symbol=symbol,
        resource_group=ResourceSymbol('resourcegroup')
    )
    assert params.get('testA') == param1
    assert params.get('testB') == param2


def test_identity_reference():
    r = UserAssignedIdentity.reference(name='foo')
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
    symbol = r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity_foo']
    assert fields['__main__.userassignedidentity_foo'] == FieldType(
        resource="Microsoft.ManagedIdentity/userAssignedIdentities",
        properties={'name': 'foo', 'scope': ResourceSymbol('resourcegroup')},
        outputs=[Output('AZURE_CLIENT_ID', "properties.clientId", symbol)],
        extensions={},
        existing=True,
        version="2024-11-30",
        symbol=symbol,
        resource_group=ResourceSymbol('resourcegroup')
    )

    r = UserAssignedIdentity.reference(name='bar', resource_group="rgtest")
    assert r.properties == {'name': 'bar', 'resource_group': ResourceGroup(name='rgtest')}
    assert r.resource_group() == 'rgtest'
    fields = {}
    symbol = r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup_rgtest', '__main__.userassignedidentity_bar']
    assert fields['__main__.userassignedidentity_bar'] == FieldType(
        resource="Microsoft.ManagedIdentity/userAssignedIdentities",
        properties={'name': 'bar', 'scope': ResourceSymbol("resourcegroup_rgtest")},
        outputs=[Output('AZURE_CLIENT_ID', "properties.clientId", symbol)],
        extensions={},
        existing=True,
        version="2024-11-30",
        symbol=symbol,
        resource_group=ResourceSymbol('resourcegroup_rgtest')
    )

    r = UserAssignedIdentity.reference(name='bar', resource_group=ResourceGroup.reference(name='rgtest', subscription=TEST_SUB))
    assert r.properties == {'name': 'bar', 'resource_group': ResourceGroup(name='rgtest')}
    assert r.resource_group() == 'rgtest'
    assert r.subscription() == TEST_SUB
    assert r.resource_id() == f"/subscriptions/{TEST_SUB}/resourceGroups/rgtest/providers/Microsoft.ManagedIdentity/userAssignedIdentities/bar"
    fields = {}
    symbol = r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup_rgtest', '__main__.userassignedidentity_bar']
    assert fields['__main__.userassignedidentity_bar'] == FieldType(
        resource="Microsoft.ManagedIdentity/userAssignedIdentities",
        properties={'name': 'bar', 'scope': ResourceSymbol("resourcegroup_rgtest")},
        outputs=[Output('AZURE_CLIENT_ID', "properties.clientId", symbol)],
        extensions={},
        existing=True,
        version="2024-11-30",
        symbol=symbol,
        resource_group=ResourceSymbol('resourcegroup_rgtest')
    )


def test_identity_defaults():
    ua_name = Parameter('uaName')
    r = UserAssignedIdentity(name=ua_name)
    fields = {}
    r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    field: FieldType = fields.popitem()[1]
    _add_defaults(field, parameters=GLOBAL_PARAMS)
    assert field.properties == {
        'name': ua_name,
        'location': GLOBAL_PARAMS['__location'],
        'tags': GLOBAL_PARAMS['__azdTags']
    }
