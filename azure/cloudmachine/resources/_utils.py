from typing import Any, Dict, List, TypedDict, Union, Literal
from typing_extensions import Required

from .._bicep.expressions import Parameter


class CustomerManagedKey(TypedDict, total=False):
    """The customer managed key definition."""
    keyName: Required[str]
    """The name of the customer managed key to use for encryption."""
    keyVaultResourceId: Required[str]
    """The resource ID of a key vault to reference a customer managed key for encryption from."""
    keyVersion: str
    """The version of the customer managed key to reference for encryption. If not provided, using 'latest'."""
    userAssignedIdentityResourceId: str
    """User assigned identity to use when fetching the customer managed key. Required if no system assigned identity is available for use."""


class RoleAssignment(TypedDict, total=False):
    principalId: Required[Union[str, Parameter[str]]]
    """The principal ID of the principal (user/group/identity) to assign the role to."""
    roleDefinitionIdOrName: Required[Union[str, Parameter[str]]]
    """The role to assign. You can provide either the display name of the role definition, the role definition GUID, or its fully qualified ID in the following format: '/providers/Microsoft.Authorization/roleDefinitions/c2f4ef07-c644-48eb-af81-4b1b4947fb11'."""
    condition: Union[str, Parameter[str]]
    """The conditions on the role assignment. This limits the resources it can be assigned to. e.g.: @Resource[Microsoft.Storage/storageAccounts/blobServices/containers:ContainerName] StringEqualsIgnoreCase "foo_storage_container"."""
    conditionVersion: Literal['2.0']
    """Version of the condition."""
    delegatedManagedIdentityResourceId: Union[str, Parameter[str]]
    """The Resource Id of the delegated managed identity resource."""
    description: Union[str, Parameter[str]]
    """The description of the role assignment."""
    name: Union[str, Parameter[str]]
    """The name (as GUID) of the role assignment. If not provided, a GUID will be generated."""
    principalType: Union[Literal['Device', 'ForeignGroup', 'Group', 'ServicePrincipal', 'User'], Parameter[str]]
    """The principal type of the assigned principal ID."""


class Identity(TypedDict, total=False):
    type: Required[Union[Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned'], Parameter[str]]]
    """The identity type."""
    userAssignedIdentities: Dict[Union[str, Parameter[str]], Any]
    """Gets or sets a list of key value pairs that describe the set of User Assigned identities that will be used with this storage account. The key is the ARM resource identifier of the identity."""


class ManagedIdentity(TypedDict, total=False):
    systemAssigned: Union[bool, Parameter[bool]]
    """Enables system assigned managed identity on the resource."""
    userAssignedResourceIds: List[Union[str, Parameter[str]]]
    """The resource ID(s) to assign to the resource. Required if a user assigned identity is used for encryption."""


def _convert_managed_identities(managed_identities: ManagedIdentity) -> Identity:
    identity: Identity = {'type': 'None', 'userAssignedIdentities': {}}
    user_assigned_identities = managed_identities.get('userAssignedResourceIds', [])
    if managed_identities.get('systemAssigned', False):
        if user_assigned_identities:
            identity['type'] = 'SystemAssigned,UserAssigned'
            for uai in user_assigned_identities:
                identity['userAssignedIdentities'][uai] = {}
        else:
            identity['type'] = 'SystemAssigned'
    elif user_assigned_identities:
        identity['type'] = 'UserAssigned'
        for uai in user_assigned_identities:
            identity['userAssignedIdentities'][uai] = {}
    return identity
