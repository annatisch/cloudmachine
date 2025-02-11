from uuid import uuid4

import pytest
from unittest.mock import ANY

from azure.cloudmachine.resources._extension.roles import _BUILT_IN_ROLES, RoleAssignment
from azure.cloudmachine.resources.storage import StorageAccount
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine._parameters import GLOBAL_PARAMS
from azure.cloudmachine._resource import FieldType
from azure.cloudmachine._bicep.expressions import ResourceSymbol, Output, Guid
from azure.cloudmachine import Parameter

TEST_SUB = str(uuid4())
RG = ResourceSymbol('resourcegroup')
IDENTITY = ResourceSymbol("userassignedidentity", principal_id=True)
CONTRIB_GUID = Guid("StorageAccount", "foo", "ServicePrincipal", 'Storage Blob Data Contributor')
OWNER_GUID = Guid("StorageAccount", "foo", "ServicePrincipal", 'Storage Blob Data Owner')

def _get_outputs(suffix="", rg=None):
    return [
        Output(f"AZURE_STORAGE_ID{suffix.upper()}", "id", ResourceSymbol(f"storageaccount{suffix}")),
        Output(f"AZURE_STORAGE_NAME{suffix.upper()}", "name", ResourceSymbol(f"storageaccount{suffix}")),
        Output(f"AZURE_STORAGE_RESOURCE_GROUP{suffix.upper()}", (rg or RG).name),
    ]

def test_roles_properties():
    r = StorageAccount(name='foo', role_assignments=['Storage Blob Data Contributor'], user_role='Storage Blob Data Contributor')
    assert r.properties == {'name': 'foo', 'properties': {}}
    assert r.extensions == {
        'role_assignments': ['Storage Blob Data Contributor'],
        'user_role': 'Storage Blob Data Contributor'
    }
    fields = {}
    symbol = r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    role_symbol = fields[f'__main__.storageaccount_foo'].extensions['role_assignments'][0]
    assert fields[f'__main__.{role_symbol._value}'].resource == "Microsoft.Authorization/roleAssignments"
    assert fields[f'__main__.{role_symbol._value}'].properties == {'name': CONTRIB_GUID, 'scope': symbol, 'properties': {'principalId': IDENTITY.principal_id, 'principalType': 'ServicePrincipal', 'roleDefinitionId': 'Storage Blob Data Contributor'}}
    assert fields[f'__main__.{role_symbol._value}'].symbol == role_symbol
    assert fields[f'__main__.{role_symbol._value}'].resource_group == RG

    r = StorageAccount(name='foo', role_assignments=['Storage Blob Data Owner'], user_role='Owner')
    assert r.properties == {'name': 'foo', 'properties': {}}
    assert r.extensions == {
        'role_assignments': ['Storage Blob Data Owner'],
        'user_role': 'Owner'
    }
    symbol = r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    assert len(fields[f'__main__.storageaccount_foo'].extensions['role_assignments']) == 2
    assert len(fields[f'__main__.storageaccount_foo'].extensions['user_roles']) == 2


def test_roles_defaults():
    base = RoleAssignment({})
    r = StorageAccount(name='foo', role_assignments=['Storage Blob Data Contributor'], user_role='Storage Blob Data Contributor')
    assert r.properties == {'name': 'foo', 'properties': {}}
    assert r.extensions == {
        'role_assignments': ['Storage Blob Data Contributor'],
        'user_role': 'Storage Blob Data Contributor'
    }
    fields = {}
    symbol = r.__bicep__(fields, parameters=GLOBAL_PARAMS)
    role_symbol = fields[f'__main__.storageaccount_foo'].extensions['role_assignments'][0]
    base._add_defaults(fields[f'__main__.{role_symbol._value}'], parameters=GLOBAL_PARAMS)
    assert fields[f'__main__.{role_symbol._value}'].properties == {
        'name': CONTRIB_GUID,
        'scope': symbol,
        'properties': {'principalId': IDENTITY.principal_id, 'principalType': 'ServicePrincipal', 'roleDefinitionId': _BUILT_IN_ROLES['Storage Blob Data Contributor']}
    }
