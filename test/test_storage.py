
from uuid import uuid4

import pytest
from azure.cloudmachine.resources.storage import StorageAccount, _add_defaults
from azure.cloudmachine.resources import ResourceGroup
from azure.cloudmachine._parameters import GLOBAL_PARAMS
from azure.cloudmachine import Parameter

TEST_SUB = str(uuid4())

def test_storage_properties():
    r = StorageAccount()
    assert r.properties == {'properties': {}}
    assert r.extensions == {}
    assert r._existing == False
    assert not r._parent
    assert r.resource == "Microsoft.Storage/storageAccounts"
    assert r.version
    fields = {}
    r.__bicep__(fields, parameters=GLOBAL_PARAMS)


    # r = StorageAccount(name='foo', location='eastus', sku_name='Standard_LRS')
    # fields = []
    # r.__bicep__(fields, parameters=GLOBAL_PARAMS)

def test_storage_reference():
    r = StorageAccount.reference(name='foo')
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

    r = StorageAccount.reference(name='foo', resource_group='bar')
    assert r.properties == {'name': 'foo', 'resource_group': ResourceGroup(name='bar')}
    assert r.resource_group() == 'bar'

    r = StorageAccount.reference(name='foo', resource_group=ResourceGroup(name='bar'), subscription=TEST_SUB)
    assert r.properties == {'name': 'foo', 'resource_group': ResourceGroup(name='bar'), 'subscription': TEST_SUB}
    assert r.subscription() == TEST_SUB
    assert r.resource_id() == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.Storage/storageAccounts/foo"

#def test_storage_merge():

def test_storage_defaults():
    access_tier = Parameter('myAccessTier', default='Premium')
    r = StorageAccount(location='westus', sku_name='Premium_ZRS', access_tier=access_tier)
    _add_defaults(properties=r.properties, extensions=r.extensions, parameters=GLOBAL_PARAMS)
    assert r.properties == {
        'name': GLOBAL_PARAMS['defaultName'],
        'location': 'westus',
        'sku': {
            'name': 'Premium_ZRS'
        },
        'kind': 'StorageV2',
        'properties': {
            'accessTier': access_tier,
            'allowCrossTenantReplication': False
        }
    }
