from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required


class RoleAssignment(TypedDict, total=False):
    """Array of role assignments to create."""
    principalId: Required[str]
    """The principal ID of the principal (user/group/identity) to assign the role to."""
    roleDefinitionIdOrName: Required[str]
    """The role to assign. You can provide either the display name of the role definition, the role definition GUID, or its fully qualified ID in the following format: '/providers/Microsoft.Authorization/roleDefinitions/c2f4ef07-c644-48eb-af81-4b1b4947fb11'."""
    condition: str
    """The conditions on the role assignment. This limits the resources it can be assigned to. e.g.: @Resource[Microsoft.Storage/storageAccounts/blobServices/containers:ContainerName] StringEqualsIgnoreCase "foo_storage_container"."""
    conditionVersion: Literal['2.0']
    """Version of the condition."""
    delegatedManagedIdentityResourceId: str
    """The Resource Id of the delegated managed identity resource."""
    description: str
    """The description of the role assignment."""
    name: str
    """The name (as GUID) of the role assignment. If not provided, a GUID will be generated."""
    principalType: Literal['Device', 'ForeignGroup', 'Group', 'ServicePrincipal', 'User']
    """The principal type of the assigned principal ID."""


class ShareParams(TypedDict, total=False):
    """"""
    name: str
    """The name of the file share to create."""
    accessTier: Literal['Cool', 'Hot', 'Premium', 'TransactionOptimized']
    """Access tier for specific share. Required if the Storage Account kind is set to FileStorage (should be set to "Premium"). GpV2 account can choose between TransactionOptimized (default), Hot, and Cool."""
    enabledProtocols: Literal['NFS', 'SMB']
    """The authentication protocol that is used for the file share. Can only be specified when creating a share."""
    roleAssignments: List['RoleAssignment']
    """Array of role assignments to create."""
    rootSquash: Literal['AllSquash', 'NoRootSquash', 'RootSquash']
    """Permissions for NFS file shares are enforced by the client OS rather than the Azure Files service. Toggling the root squash behavior reduces the rights of the root user for NFS shares."""
    shareQuota: int
    """The maximum size of the share, in gigabytes. Must be greater than 0, and less than or equal to 5120 (5TB). For Large File Shares, the maximum size is 102400 (100TB)."""


class ShareKwargs(TypedDict, total=False):
    """"""
    access_tier: Literal['Cool', 'Hot', 'Premium', 'TransactionOptimized']
    """Access tier for specific share. Required if the Storage Account kind is set to FileStorage (should be set to "Premium"). GpV2 account can choose between TransactionOptimized (default), Hot, and Cool."""
    enabled_protocols: Literal['NFS', 'SMB']
    """The authentication protocol that is used for the file share. Can only be specified when creating a share."""
    role_assignments: List['RoleAssignment']
    """Array of role assignments to create."""
    root_squash: Literal['AllSquash', 'NoRootSquash', 'RootSquash']
    """Permissions for NFS file shares are enforced by the client OS rather than the Azure Files service. Toggling the root squash behavior reduces the rights of the root user for NFS shares."""
    share_quota: int
    """The maximum size of the share, in gigabytes. Must be greater than 0, and less than or equal to 5120 (5TB). For Large File Shares, the maximum size is 102400 (100TB)."""
