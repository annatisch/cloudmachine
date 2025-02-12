from unittest import mock
import os
import filecmp
import pytest
import difflib


from azure.cloudmachine import export, provision, Parameter
from azure.cloudmachine.resources.storage import StorageAccount
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine.resources.managedidentity import UserAssignedIdentity
from azure.cloudmachine.resources.ai import AIServices
from azure.cloudmachine.resources.ai.deployment import AIDeployment, AIChat, AIEmbeddings

TEST_SUB = '6e441d6a-23ce-4450-a4a6-78f8d4f45ce9'


def _get_infra_dir() -> str:
    test_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(test_dir, "test_infra")


def _compare_outputs(output_dir, ref_dir, test_dir):
    for _, _, files in os.walk(os.path.join(output_dir, ref_dir)):
        for filename in files:
            with open(os.path.join(output_dir, ref_dir, filename), 'r') as _ref:
                ref_file = _ref.readlines()
            with open(os.path.join(output_dir, test_dir, filename), 'r') as _test:
                test_file = _test.readlines()
            diff = difflib.unified_diff(
                ref_file,
                test_file,
                fromfile=f'{ref_dir}/{filename}',
                tofile=f'{test_dir}/{filename}',
            )
            changes = ("".join(diff))
            has_changes = bool(changes)
            assert not has_changes, "\n" + changes
            os.remove(os.path.join(output_dir, test_dir, filename))
    os.rmdir(os.path.join(output_dir, test_dir))


@pytest.fixture
def _compare_exports(request):
    output_dir = _get_infra_dir()
    ref_dir = request.node.name
    test_dir = f"infra_{request.node.name}"
    yield output_dir, ref_dir, test_dir
    _compare_outputs(output_dir, ref_dir, test_dir)


@pytest.fixture
def _record_exports(request):
    output_dir = _get_infra_dir()
    ref_dir = request.node.name
    return output_dir, ref_dir, ref_dir

export_dir = _record_exports if os.environ.get('TEST_EXPORT_RECORD', "").lower() == 'true' else _compare_exports


def test_export_resourcegroup(export_dir):
    r = ResourceGroup()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_resourcegroup_with_properties(export_dir):
    r = ResourceGroup(name="foo", location="eastus", tags={"key": "value"})
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_resourcegroup_with_parameter(export_dir):
    param = Parameter("resourceGroupName", default="foo")
    r = ResourceGroup(name=param)
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_resourcegroup_with_config(export_dir):
    param = Parameter("resourceGroupName", default="foo")
    r = ResourceGroup(name=param)
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test", config={"resourceGroupName": "bar"})


def test_export_resourcegroup_existing(export_dir):
    r = ResourceGroup.reference(name="foo")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_resourcegroup_existing_with_subscription(export_dir):
    r = ResourceGroup.reference(name="foo", subscription=TEST_SUB)
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_identity(export_dir):
    r = UserAssignedIdentity()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_identity_with_properties(export_dir):
    r = UserAssignedIdentity(name='foo', location='westus', tags={'key': 'value'})
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_identity_with_parameter(export_dir):
    param = Parameter("testLocation")
    r = UserAssignedIdentity(location=param)
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test", config={"testLocation": "eastus"})


def test_export_identity_existing(export_dir):
    r = UserAssignedIdentity.reference(name="exists")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_identity_existing_with_resourcegroup(export_dir):
    r = UserAssignedIdentity.reference(name="exists", resource_group="rgexists")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_identity_existing_with_resourcegroup_and_subscription(export_dir):
    r = UserAssignedIdentity.reference(name="exists", resource_group=ResourceGroup.reference(name='rgexists', subscription=TEST_SUB))
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_storage(export_dir):
    r = StorageAccount()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_storage_existing(export_dir):
    r = StorageAccount.reference(name='storagetest', resource_group='testrg')
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


#def test_export_storage_multiple(export_dir):
#def test_export_storage_with_parameters(export_dir):


def test_export_storage_with_properties(export_dir):
    r = StorageAccount(enable_hierarchical_namespace=True, allow_blob_public_access=True, sku='Premium_LRS', location="westus")
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_storage_with_role_assignments(export_dir):
    r = StorageAccount(roles=['Storage Blob Data Owner'], user_roles=['Storage Blob Data Contributor'])
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_storage_with_no_user_access(export_dir):
    r = StorageAccount(roles=['Storage Blob Data Owner'], user_roles=['Storage Blob Data Contributor'])
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test", user_access=False)


def test_export_aiservices(export_dir):
    r = AIServices()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_aiservices_existing(export_dir):
    r = AIServices.reference(name='aitest', resource_group='aitest')
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_aiservices_with_properties(export_dir):
    r = AIServices(sku='C2', location="westus", public_network_access='Disabled')
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_aiservices_with_role_assignments(export_dir):
    r = AIServices(roles=['Cognitive Services OpenAI Contributor'], user_roles=['Cognitive Services OpenAI User'])
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_export_aiservices_with_no_user_access(export_dir):
    r = AIServices(roles=['Cognitive Services OpenAI Contributor'], user_roles=['Cognitive Services OpenAI User'])
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test", user_access=False)


#def test_export_aiservices_multiple(export_dir):
#def test_export_aiservices_with_parameters(export_dir):


def test_export_aiservices_chat_deployment(export_dir):
    #p = AIServices(roles=['Cognitive Services OpenAI User'])
    r = AIChat()
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")



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

