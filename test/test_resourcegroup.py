from uuid import uuid4

import pytest
from azure.cloudmachine._resource import FieldType
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine._parameters import GLOBAL_PARAMS
from azure.cloudmachine._bicep.expressions import ResourceSymbol, Subscription
from azure.cloudmachine import Parameter

TEST_SUB = str(uuid4())

def test_resourcegroup_properties():
    r = ResourceGroup()
    assert r.properties == {}
    assert r.extensions == {}
    assert r._existing == False
    assert not r._parent
    assert r.resource == "Microsoft.Resources/resourceGroups"
    assert r.version
    fields = {}
    symbol = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup']
    assert fields['__main__.resourcegroup'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['__main__.resourcegroup'].properties == {}
    assert fields['__main__.resourcegroup'].outputs == []
    assert fields['__main__.resourcegroup'].extensions == {}
    assert fields['__main__.resourcegroup'].existing == False
    assert fields['__main__.resourcegroup'].version
    assert fields['__main__.resourcegroup'].symbol == symbol
    assert fields['__main__.resourcegroup'].resource_group == symbol
    assert fields['__main__.resourcegroup'].name == None
    assert fields['__main__.resourcegroup'].add_defaults

    r2 = ResourceGroup(location='westus')
    assert r2.properties == {'location': 'westus'}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup']
    assert fields['__main__.resourcegroup'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['__main__.resourcegroup'].properties == {'location': 'westus'}
    assert fields['__main__.resourcegroup'].outputs == []
    assert fields['__main__.resourcegroup'].extensions == {}
    assert fields['__main__.resourcegroup'].existing == False
    assert fields['__main__.resourcegroup'].version
    assert fields['__main__.resourcegroup'].symbol == symbol
    assert fields['__main__.resourcegroup'].resource_group == symbol
    assert fields['__main__.resourcegroup'].name == None
    assert fields['__main__.resourcegroup'].add_defaults

    r3 = ResourceGroup(location='eastus')
    assert r3.properties == {'location': 'eastus'}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = ResourceGroup(name='foo', tags={'test': 'value'})
    assert r4.properties == {'name': 'foo', 'tags': {'test': 'value'}}
    symbol = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.resourcegroup_foo']
    assert fields['__main__.resourcegroup_foo'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['__main__.resourcegroup_foo'].properties == {'name': 'foo', 'tags': {'test': 'value'}}
    assert fields['__main__.resourcegroup_foo'].outputs == []
    assert fields['__main__.resourcegroup_foo'].extensions == {}
    assert fields['__main__.resourcegroup_foo'].existing == False
    assert fields['__main__.resourcegroup_foo'].version
    assert fields['__main__.resourcegroup_foo'].symbol == symbol
    assert fields['__main__.resourcegroup_foo'].resource_group == symbol
    assert fields['__main__.resourcegroup_foo'].name == 'foo'
    assert fields['__main__.resourcegroup_foo'].add_defaults


def test_resourcegroup_reference():
    r = ResourceGroup.reference(name='foo')
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
    assert list(fields.keys()) == ['__main__.resourcegroup_foo']
    assert fields['__main__.resourcegroup_foo'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['__main__.resourcegroup_foo'].properties == {'name': 'foo'}
    assert fields['__main__.resourcegroup_foo'].outputs == []
    assert fields['__main__.resourcegroup_foo'].extensions == {}
    assert fields['__main__.resourcegroup_foo'].existing == True
    assert fields['__main__.resourcegroup_foo'].version
    assert fields['__main__.resourcegroup_foo'].symbol == symbol
    assert fields['__main__.resourcegroup_foo'].resource_group == symbol
    assert fields['__main__.resourcegroup_foo'].name == 'foo'
    assert not fields['__main__.resourcegroup_foo'].add_defaults

    r = ResourceGroup.reference(name='bar', subscription=TEST_SUB)
    assert r.properties == {'name': 'bar', 'subscription': TEST_SUB}
    assert r.subscription() == TEST_SUB
    assert r.resource_id() == f"/subscriptions/{TEST_SUB}/providers/Microsoft.Resources/resourceGroups/bar"
    symbol = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup_foo', '__main__.resourcegroup_bar']
    assert fields['__main__.resourcegroup_bar'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['__main__.resourcegroup_bar'].properties == {'name': 'bar', 'scope': Subscription(TEST_SUB)}
    assert fields['__main__.resourcegroup_bar'].outputs == []
    assert fields['__main__.resourcegroup_bar'].extensions == {}
    assert fields['__main__.resourcegroup_bar'].existing == True
    assert fields['__main__.resourcegroup_bar'].version
    assert fields['__main__.resourcegroup_bar'].symbol == symbol
    assert fields['__main__.resourcegroup_bar'].resource_group == symbol
    assert fields['__main__.resourcegroup_bar'].name == 'bar'
    assert not fields['__main__.resourcegroup_bar'].add_defaults

def test_resourcegroup_defaults():
    rg_name = Parameter('rgName')
    r = ResourceGroup(name=rg_name)
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    field = fields.popitem()[1]
    r._add_defaults(field, parameters=dict(GLOBAL_PARAMS))
    assert field.properties == {
        'name': rg_name,
        'location': GLOBAL_PARAMS['location'],
        'tags': GLOBAL_PARAMS['azdTags']
    }
