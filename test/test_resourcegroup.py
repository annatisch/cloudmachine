from uuid import uuid4

import pytest
from azure.cloudmachine._resource import FieldType
from azure.cloudmachine.resources.resourcegroup import ResourceGroup, _add_defaults
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
    symbol = r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup']
    assert fields['__main__.resourcegroup'] == FieldType(
        resource="Microsoft.Resources/resourceGroups",
        properties={},
        outputs={},
        extensions={},
        existing=False,
        version="2021-04-01",
        symbol=symbol,
        resource_group=symbol
    )

    r2 = ResourceGroup(location='westus')
    assert r2.properties == {'location': 'westus'}
    r2.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup']
    assert fields['__main__.resourcegroup'] == FieldType(
        resource="Microsoft.Resources/resourceGroups",
        properties={'location': 'westus'},
        outputs={},
        extensions={},
        existing=False,
        version="2021-04-01",
        symbol=symbol,
        resource_group=symbol
    )

    r3 = ResourceGroup(location='eastus')
    assert r3.properties == {'location': 'eastus'}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=GLOBAL_PARAMS)

    r4 = ResourceGroup(name='foo', tags={'test': 'value'})
    assert r4.properties == {'name': 'foo', 'tags': {'test': 'value'}}
    symbol = r4.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.resourcegroup_foo']
    assert fields['__main__.resourcegroup_foo'] == FieldType(
        resource="Microsoft.Resources/resourceGroups",
        properties={'name': 'foo', 'tags': {'test': 'value'}},
        outputs={},
        extensions={},
        existing=False,
        version="2021-04-01",
        symbol=symbol,
        resource_group=symbol
    )


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
    symbol = r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup_foo']
    assert fields['__main__.resourcegroup_foo'] == FieldType(
        resource="Microsoft.Resources/resourceGroups",
        properties={'name': 'foo'},
        outputs={},
        extensions={},
        existing=True,
        version="2021-04-01",
        symbol=symbol,
        resource_group=symbol
    )

    r = ResourceGroup.reference(name='bar', subscription=TEST_SUB)
    assert r.properties == {'name': 'bar', 'subscription': TEST_SUB}
    assert r.subscription() == TEST_SUB
    assert r.resource_id() == f"/subscriptions/{TEST_SUB}/providers/Microsoft.Resources/resourceGroups/bar"
    symbol = r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert list(fields.keys()) == ['__main__.resourcegroup_foo', '__main__.resourcegroup_bar']
    assert fields['__main__.resourcegroup_bar'] == FieldType(
        resource="Microsoft.Resources/resourceGroups",
        properties={'name': 'bar', 'scope': Subscription(TEST_SUB)},
        outputs={},
        extensions={},
        existing=True,
        version="2021-04-01",
        symbol=symbol,
        resource_group=symbol
    )

def test_resourcegroup_defaults():
    rg_name = Parameter('rgName')
    r = ResourceGroup(name=rg_name)
    fields = {}
    r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    field = fields.popitem()[1]
    _add_defaults(field, parameters=GLOBAL_PARAMS)
    assert field.properties == {
        'name': rg_name,
        'location': GLOBAL_PARAMS['__location'],
        'tags': GLOBAL_PARAMS['__azdTags']
    }
