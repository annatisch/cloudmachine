
from uuid import uuid4

import pytest
from azure.cloudmachine.resources.storage import StorageAccount
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine._parameters import GLOBAL_PARAMS
from azure.cloudmachine._resource import FieldType
from azure.cloudmachine.resources._identifiers import ResourceIdentifiers
from azure.cloudmachine._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.cloudmachine import Parameter, AzureInfrastructure, export, resource, AzureApp, client

TEST_SUB = '6e441d6a-23ce-4450-a4a6-78f8d4f45ce9'
RG = ResourceSymbol('resourcegroup')
IDENTITY = {
    'type': 'UserAssigned',
    'userAssignedIdentities': {GLOBAL_PARAMS['managedIdentityId'].format(): {}}
}

def _get_outputs(suffix="", rg=None):
    return {
        'resource_id': Output(f"AZURE_STORAGE_ID{suffix.upper()}", "id", ResourceSymbol(f"storageaccount{suffix}")),
        'name': Output(f"AZURE_STORAGE_NAME{suffix.upper()}", "name", ResourceSymbol(f"storageaccount{suffix}")),
        'resource_group': Output(f"AZURE_STORAGE_RESOURCE_GROUP{suffix.upper()}", rg if rg else DefaultResourceGroup().name),
    }

def test_storage_properties():
    r = StorageAccount()
    assert r.properties == {'properties': {}}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.Storage/storageAccounts"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert len(symbols) == 1
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.storageaccount']
    assert fields['__main__.storageaccount'].resource == "Microsoft.Storage/storageAccounts"
    assert fields['__main__.storageaccount'].properties == {'properties': {}}
    assert fields['__main__.storageaccount'].outputs == _get_outputs()
    assert fields['__main__.storageaccount'].extensions == {}
    assert fields['__main__.storageaccount'].existing == False
    assert fields['__main__.storageaccount'].version
    assert fields['__main__.storageaccount'].symbol == symbols[0]
    assert fields['__main__.storageaccount'].resource_group == RG
    assert not fields['__main__.storageaccount'].name
    assert fields['__main__.storageaccount'].add_defaults

    r2 = StorageAccount(location='westus', sku='Standard_RAGRS')
    assert r2.properties == {'location': 'westus', 'sku': {'name': 'Standard_RAGRS'}, 'properties': {}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.storageaccount']
    assert fields['__main__.storageaccount'].resource == "Microsoft.Storage/storageAccounts"
    assert fields['__main__.storageaccount'].properties == {'location': 'westus', 'sku': {'name': 'Standard_RAGRS'}, 'properties': {}}
    assert fields['__main__.storageaccount'].outputs == _get_outputs()
    assert fields['__main__.storageaccount'].extensions == {}
    assert fields['__main__.storageaccount'].existing == False
    assert fields['__main__.storageaccount'].version
    assert fields['__main__.storageaccount'].symbol == symbols[0]
    assert fields['__main__.storageaccount'].resource_group == RG
    assert not fields['__main__.storageaccount'].name
    assert fields['__main__.storageaccount'].add_defaults

    r3 = StorageAccount(sku='Premium_ZRS')
    assert r3.properties == {'sku': {'name': 'Premium_ZRS'}, 'properties': {}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = StorageAccount(name='foo', tags={'test': 'value'}, access_tier='Cool')
    assert r4.properties == {'name': 'foo', 'tags': {'test': 'value'}, 'properties': {'accessTier': 'Cool'}}
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.storageaccount', '__main__.storageaccount_foo']
    assert fields['__main__.storageaccount_foo'].resource == "Microsoft.Storage/storageAccounts"
    assert fields['__main__.storageaccount_foo'].properties == {'name': 'foo', 'tags': {'test': 'value'}, 'properties': {'accessTier': 'Cool'}}
    assert fields['__main__.storageaccount_foo'].outputs == _get_outputs("_foo")
    assert fields['__main__.storageaccount_foo'].extensions == {}
    assert fields['__main__.storageaccount_foo'].existing == False
    assert fields['__main__.storageaccount_foo'].version
    assert fields['__main__.storageaccount_foo'].symbol == symbols[0]
    assert fields['__main__.storageaccount_foo'].resource_group == RG
    assert fields['__main__.storageaccount_foo'].name == 'foo'
    assert fields['__main__.storageaccount_foo'].add_defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = StorageAccount(name=param1, sku=param2, access_tier=param3)
    assert r5.properties == {'name': param1, 'sku': {'name': param2}, 'properties': {'accessTier': param3}}
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.userassignedidentity', '__main__.storageaccount_testa']
    assert fields['__main__.storageaccount_testa'].resource == "Microsoft.Storage/storageAccounts"
    assert fields['__main__.storageaccount_testa'].properties == {'name': param1, 'sku': {'name': param2}, 'properties': {'accessTier': param3}}
    assert fields['__main__.storageaccount_testa'].outputs == _get_outputs("_testa")
    assert fields['__main__.storageaccount_testa'].extensions == {}
    assert fields['__main__.storageaccount_testa'].existing == False
    assert fields['__main__.storageaccount_testa'].version
    assert fields['__main__.storageaccount_testa'].symbol == symbols[0]
    assert fields['__main__.storageaccount_testa'].resource_group == RG
    assert fields['__main__.storageaccount_testa'].name == param1
    assert fields['__main__.storageaccount_testa'].add_defaults
    assert params.get('testA') == param1
    assert params.get('testB') == param2
    assert params.get('testC') == param3


def test_storage_reference():
    r = StorageAccount.reference(name='foo')
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
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup', '__main__.storageaccount_foo']
    assert fields['__main__.storageaccount_foo'].resource == "Microsoft.Storage/storageAccounts"
    assert fields['__main__.storageaccount_foo'].properties == {'name': 'foo', 'scope': RG}
    assert fields['__main__.storageaccount_foo'].outputs == _get_outputs("_foo")
    assert fields['__main__.storageaccount_foo'].extensions == {}
    assert fields['__main__.storageaccount_foo'].existing == True
    assert fields['__main__.storageaccount_foo'].version
    assert fields['__main__.storageaccount_foo'].symbol == symbols[0]
    assert fields['__main__.storageaccount_foo'].resource_group == RG
    assert fields['__main__.storageaccount_foo'].name == 'foo'
    assert not fields['__main__.storageaccount_foo'].add_defaults

    rg = ResourceSymbol('resourcegroup_bar')
    r = StorageAccount.reference(name='foo', resource_group='bar')
    assert r.properties == {'name': 'foo', 'resource_group': ResourceGroup(name='bar')}
    assert r.resource_group() == 'bar'
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['__main__.resourcegroup_bar', '__main__.storageaccount_foo']
    assert fields['__main__.storageaccount_foo'].resource == "Microsoft.Storage/storageAccounts"
    assert fields['__main__.storageaccount_foo'].properties == {'name': 'foo', 'scope': rg}
    assert fields['__main__.storageaccount_foo'].outputs == _get_outputs("_foo", 'bar')
    assert fields['__main__.storageaccount_foo'].extensions == {}
    assert fields['__main__.storageaccount_foo'].existing == True
    assert fields['__main__.storageaccount_foo'].version
    assert fields['__main__.storageaccount_foo'].symbol == symbols[0]
    assert fields['__main__.storageaccount_foo'].resource_group == rg
    assert fields['__main__.storageaccount_foo'].name == 'foo'
    assert not fields['__main__.storageaccount_foo'].add_defaults

    r = StorageAccount.reference(name='foo', resource_group=ResourceGroup.reference(name='bar', subscription=TEST_SUB))
    assert r.properties == {'name': 'foo', 'resource_group': ResourceGroup(name='bar')}
    assert r.subscription() == TEST_SUB
    assert r.resource_id() == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.Storage/storageAccounts/foo"


def test_storage_defaults():
    access_tier = Parameter('myAccessTier', default='Premium')
    r = StorageAccount(location='westus', sku='Premium_ZRS', access_tier=access_tier)
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    field = fields.popitem()[1]
    r._add_defaults(field, parameters=dict(GLOBAL_PARAMS))
    assert field.properties == {
        'name': GLOBAL_PARAMS['defaultName'],
        'location': 'westus',
        'sku': {
            'name': 'Premium_ZRS'
        },
        'kind': 'StorageV2',
        'properties': {
            'accessTier': access_tier,
            'allowCrossTenantReplication': False
        },
        'identity': IDENTITY,
        'tags': GLOBAL_PARAMS['azdTags']
    }


def test_storage_export(export_dir):
    r = StorageAccount()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_storage_export_existing(export_dir):
    r = StorageAccount.reference(name='storagetest', resource_group='testrg')
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


#def test_export_storage_multiple(export_dir):
#def test_export_storage_with_parameters(export_dir):


def test_storage_export_with_properties(export_dir):
    r = StorageAccount(enable_hierarchical_namespace=True, allow_blob_public_access=True, sku='Premium_LRS', location="westus")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_storage_export_with_role_assignments(export_dir):
    r = StorageAccount(roles=['Storage Blob Data Owner'], user_roles=['Storage Blob Data Contributor'])
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_storage_export_with_no_user_access(export_dir):
    r = StorageAccount(roles=['Storage Blob Data Owner'], user_roles=['Storage Blob Data Contributor'])
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test", user_access=False)


def test_storage_client():
    from azure.storage.blob import BlobServiceClient
    r = StorageAccount()
    with pytest.raises(TypeError):
        r.get_client(BlobServiceClient)

def test_storage_infra():
    class TestInfra(AzureInfrastructure):
        rg: StorageAccount = resource()
    
    assert isinstance(TestInfra.rg, StorageAccount)
    assert TestInfra.rg.infrastructure == TestInfra
    infra = TestInfra()
    assert isinstance(infra.rg, StorageAccount)
    assert infra.rg.properties == {'properties': {}}

    infra = TestInfra(rg=StorageAccount(name='foo'))
    assert infra.rg.name() == 'foo'


def test_storage_app():
    from azure.storage.blob import BlobServiceClient
    r = StorageAccount.reference(name='test', resource_group='test')

    class TestApp(AzureApp):
        client: BlobServiceClient = client()

    with pytest.raises(TypeError):
        app = TestApp()

    with pytest.raises(TypeError):
        app = TestApp(client=r)
 