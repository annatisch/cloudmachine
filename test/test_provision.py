from unittest import mock
import os
import filecmp
import pytest


from azure.cloudmachine import export, provision, Parameter
from azure.cloudmachine.resources.storage import StorageAccount
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine.resources.managedidentity import UserAssignedIdentity


TEST_SUB = '6e441d6a-23ce-4450-a4a6-78f8d4f45ce9'


def _get_infra_dir() -> str:
    test_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(test_dir, "test_infra")


@pytest.fixture
def export_dir(request):
    output_dir = _get_infra_dir()
    test_dir = f"infra_{request.node.name}"
    yield output_dir, test_dir
    basedir = os.path.join(output_dir, request.node.name)
    assert os.path.isdir(basedir)
    for filename in ["main.bicep", "main.parameters.json", "test.bicep"]:
        baseline = os.path.join(basedir, filename)
        if os.path.exists(baseline):
            assert filecmp.cmp(
                os.path.join(output_dir, test_dir, filename),
                baseline,
                shallow=False
            )
    #os.rmdir(os.path.join(output_dir, test_dir))


def test_export_resourcegroup(export_dir):
    r = ResourceGroup()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_resourcegroup_with_properties(export_dir):
    r = ResourceGroup(name="foo", location="eastus", tags={"key": "value"})
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_resourcegroup_with_parameter(export_dir):
    param = Parameter("resourceGroupName", default="foo")
    r = ResourceGroup(name=param)
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_resourcegroup_with_config(export_dir):
    param = Parameter("resourceGroupName", default="foo")
    r = ResourceGroup(name=param)
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test", config={"resourceGroupName": "bar"})


def test_export_resourcegroup_existing(export_dir):
    r = ResourceGroup.reference(name="foo")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_resourcegroup_existing_with_subscription(export_dir):
    r = ResourceGroup.reference(name="foo", subscription=TEST_SUB)
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_identity(export_dir):
    r = UserAssignedIdentity()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_identity_with_properties(export_dir):
    r = UserAssignedIdentity(name='foo', location='westus', tags={'key': 'value'})
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_identity_with_parameter(export_dir):
    param = Parameter("testLocation")
    r = UserAssignedIdentity(location=param)
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test", config={"testLocation": "eastus"})


def test_export_identity_existing(export_dir):
    r = UserAssignedIdentity.reference(name="exists")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_identity_existing_with_resourcegroup(export_dir):
    r = UserAssignedIdentity.reference(name="exists", resource_group="rgexists")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_identity_existing_with_resourcegroup_and_subscription(export_dir):
    r = UserAssignedIdentity.reference(name="exists", resource_group=ResourceGroup.reference(name='rgexists', subscription=TEST_SUB))
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_storage(export_dir):
    r = StorageAccount()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_storage_with_properties(export_dir):
    r = StorageAccount(enable_hierarchical_namespace=True, allow_blob_public_access=True, sku_name='Premium_LRS', location="westus")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_storage_with_role_assignments(export_dir):
    r = StorageAccount(role_assignments=['Storage Blob Data Owner'], user_role='Storage Blob Data Contributor')
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test")


def test_export_storage_with_no_user_access(export_dir):
    r = StorageAccount(role_assignments=['Storage Blob Data Owner'], user_role='Storage Blob Data Contributor')
    export(r, output_dir=export_dir[0], infra_dir=export_dir[1], name="test", user_access=False)


#def test_export_storage_multiple(export_dir):



# def test_export_resource(export_dir):
    
#     test_param = Parameter('TestAccessTier', varname='STORAGE_ACCESS_TIER', default="Hot")
#     rg = ResourceGroup.reference(name='antisch-cmtest')
#     ua = UserAssignedIdentity.reference(name='uatest', resource_group='foo')
#     r = StorageAccount(user_role='Storage Blob Data Owner', access_tier=test_param)
#     export(
#         rg, ua, r,
#         config={'TestAccessTier': 'Cold'},
#         name="test",
#         output_dir=export_dir,
#     )

