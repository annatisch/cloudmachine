from uuid import uuid4

import pytest
from azure.cloudmachine._resource import FieldType
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine._parameters import GLOBAL_PARAMS
from azure.cloudmachine._component import InfrastructureResource
from azure.cloudmachine._bicep.expressions import ResourceSymbol, Subscription
from azure.cloudmachine import Parameter, export, AzureInfrastructure, resource
from azure.cloudmachine.resources._identifiers import ResourceIdentifiers

TEST_SUB = "25b4d56c-0dc2-4c45-9a13-c3653a70b912"


def test_resourcegroup_properties():
    r = ResourceGroup()
    assert r.properties == {}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.Resources/resourceGroups"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert len(symbols) == 1
    assert list(fields.keys()) == ['resourcegroup']
    assert fields['resourcegroup'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['resourcegroup'].properties == {}
    assert fields['resourcegroup'].outputs == {}
    assert fields['resourcegroup'].extensions == {}
    assert fields['resourcegroup'].existing == False
    assert fields['resourcegroup'].version
    assert fields['resourcegroup'].symbol == symbols[0]
    assert fields['resourcegroup'].resource_group == symbols[0]
    assert fields['resourcegroup'].name == None
    assert fields['resourcegroup'].add_defaults

    r2 = ResourceGroup(location='westus')
    assert r2.properties == {'location': 'westus'}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['resourcegroup']
    assert fields['resourcegroup'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['resourcegroup'].properties == {'location': 'westus'}
    assert fields['resourcegroup'].outputs == {}
    assert fields['resourcegroup'].extensions == {}
    assert fields['resourcegroup'].existing == False
    assert fields['resourcegroup'].version
    assert fields['resourcegroup'].symbol == symbols[0]
    assert fields['resourcegroup'].resource_group == symbols[0]
    assert fields['resourcegroup'].name == None
    assert fields['resourcegroup'].add_defaults

    r3 = ResourceGroup(location='eastus')
    assert r3.properties == {'location': 'eastus'}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = ResourceGroup(name='foo', tags={'test': 'value'})
    assert r4.properties == {'name': 'foo', 'tags': {'test': 'value'}}
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['resourcegroup', 'resourcegroup_foo']
    assert fields['resourcegroup_foo'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['resourcegroup_foo'].properties == {'name': 'foo', 'tags': {'test': 'value'}}
    assert fields['resourcegroup_foo'].outputs == {}
    assert fields['resourcegroup_foo'].extensions == {}
    assert fields['resourcegroup_foo'].existing == False
    assert fields['resourcegroup_foo'].version
    assert fields['resourcegroup_foo'].symbol == symbols[0]
    assert fields['resourcegroup_foo'].resource_group == symbols[0]
    assert fields['resourcegroup_foo'].name == 'foo'
    assert fields['resourcegroup_foo'].add_defaults


def test_resourcegroup_parameter_properties():
    rg_name = Parameter('RgName')
    rg_tag = Parameter("RgTag")
    r = ResourceGroup(name=rg_name, tags={'rgtag': rg_tag})
    assert r.properties == {'name': rg_name, 'tags': {'rgtag': rg_tag}}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.Resources/resourceGroups"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['resourcegroup_rgname']
    assert fields['resourcegroup_rgname'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['resourcegroup_rgname'].properties == {'name': rg_name, 'tags': {'rgtag': rg_tag}}
    assert fields['resourcegroup_rgname'].outputs == {}
    assert fields['resourcegroup_rgname'].extensions == {}
    assert fields['resourcegroup_rgname'].existing == False
    assert fields['resourcegroup_rgname'].version
    assert fields['resourcegroup_rgname'].symbol == symbols[0]
    assert fields['resourcegroup_rgname'].resource_group == symbols[0]
    assert fields['resourcegroup_rgname'].name == rg_name
    assert fields['resourcegroup_rgname'].add_defaults

def test_resourcegroup_reference():
    r = ResourceGroup.reference(name='foo')
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
    assert list(fields.keys()) == ['resourcegroup_foo']
    assert fields['resourcegroup_foo'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['resourcegroup_foo'].properties == {'name': 'foo'}
    assert fields['resourcegroup_foo'].outputs == {}
    assert fields['resourcegroup_foo'].extensions == {}
    assert fields['resourcegroup_foo'].existing == True
    assert fields['resourcegroup_foo'].version
    assert fields['resourcegroup_foo'].symbol == symbols[0]
    assert fields['resourcegroup_foo'].resource_group == symbols[0]
    assert fields['resourcegroup_foo'].name == 'foo'
    assert not fields['resourcegroup_foo'].add_defaults

    r = ResourceGroup.reference(name='bar', subscription=TEST_SUB)
    assert r.properties == {'name': 'bar', 'subscription': TEST_SUB}
    assert r.subscription() == TEST_SUB
    assert r.resource_id() == f"/subscriptions/{TEST_SUB}/providers/Microsoft.Resources/resourceGroups/bar"
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['resourcegroup_foo', 'resourcegroup_bar']
    assert fields['resourcegroup_bar'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['resourcegroup_bar'].properties == {'name': 'bar', 'scope': Subscription(TEST_SUB)}
    assert fields['resourcegroup_bar'].outputs == {}
    assert fields['resourcegroup_bar'].extensions == {}
    assert fields['resourcegroup_bar'].existing == True
    assert fields['resourcegroup_bar'].version
    assert fields['resourcegroup_bar'].symbol == symbols[0]
    assert fields['resourcegroup_bar'].resource_group == symbols[0]
    assert fields['resourcegroup_bar'].name == 'bar'
    assert not fields['resourcegroup_bar'].add_defaults


def test_resourcegroup_parameter_reference():
    rg_name = Parameter('RgName')
    rg_sub = Parameter('RgSub')
    r = ResourceGroup.reference(name=rg_name, subscription=rg_sub)
    assert r.properties == {'name': rg_name, 'subscription': rg_sub}
    assert r._existing == True
    assert not r.parent
    assert r.extensions == {}
    with pytest.raises(RuntimeError):
        r.name()
    with pytest.raises(RuntimeError):
        r.resource_group()
    with pytest.raises(RuntimeError):
        r.subscription()
    with pytest.raises(RuntimeError):
        r.resource_id()

    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ['resourcegroup_rgname']
    assert fields['resourcegroup_rgname'].resource == "Microsoft.Resources/resourceGroups"
    assert fields['resourcegroup_rgname'].properties == {'name': rg_name, 'scope': Subscription(rg_sub)}
    assert fields['resourcegroup_rgname'].outputs == {}
    assert fields['resourcegroup_rgname'].extensions == {}
    assert fields['resourcegroup_rgname'].existing == True
    assert fields['resourcegroup_rgname'].version
    assert fields['resourcegroup_rgname'].symbol == symbols[0]
    assert fields['resourcegroup_rgname'].resource_group == symbols[0]
    assert fields['resourcegroup_rgname'].name == rg_name
    assert not fields['resourcegroup_rgname'].add_defaults


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

def test_resourcegroup_export(export_dir):
    class TestInfra(AzureInfrastructure):
        r: ResourceGroup = resource()
    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_resourcegroup_export_with_properties(export_dir):
    class TestInfra(AzureInfrastructure):
        r: ResourceGroup = resource(default=ResourceGroup(name="foo", location="eastus", tags={"key": "value"}))
    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_resourcegroup_export_with_parameter(export_dir):
    param = Parameter("resourceGroupName", default="foo")
    class TestInfra(AzureInfrastructure):
        r: ResourceGroup = resource(default=ResourceGroup(name=param))
    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_resourcegroup_export_with_config(export_dir):
    param = Parameter("resourceGroupName", default="foo")
    class TestInfra(AzureInfrastructure):
        r: ResourceGroup = resource(default=ResourceGroup(name=param))
    export(TestInfra(config_store={"resourceGroupName": "bar"}), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_resourcegroup_export_existing(export_dir):
    class TestInfra(AzureInfrastructure):
        r: ResourceGroup = resource(default=ResourceGroup.reference(name="foo"))
    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_resourcegroup_export_existing_with_parameter(export_dir):
    rg_name = Parameter('RgName')
    rg_sub = Parameter('RgSub')
    class TestInfra(AzureInfrastructure):
        r: ResourceGroup = resource(default=ResourceGroup.reference(name=rg_name, subscription=rg_sub))
    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_resourcegroup_export_existing_with_subscription(export_dir):
    class TestInfra(AzureInfrastructure):
        r: ResourceGroup = resource(default=ResourceGroup.reference(name="foo", subscription=TEST_SUB))
    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_resourcegroup_infra():
    class TestInfra(AzureInfrastructure):
        rg: ResourceGroup = resource()
    
    assert isinstance(TestInfra.rg, ResourceGroup)
    assert TestInfra.rg._infra is None
    infra = TestInfra()
    assert infra.rg._infra == infra
    assert isinstance(infra.rg, ResourceGroup)
    assert infra.rg.properties == {}

    infra = TestInfra(rg=ResourceGroup(name='foo'))
    assert infra.rg.name() == 'foo'

    #TODO: Finish testing default behaviours
    # assert resource(default=ResourceGroup.reference(name='foo'))
