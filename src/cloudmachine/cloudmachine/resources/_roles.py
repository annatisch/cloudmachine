# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import IO, Any, ClassVar, List, Mapping, Optional, Dict, Literal, Set, overload
from dataclasses import InitVar, dataclass, field

from ._resource import (
    _serialize_resource,
    Resource,
    LocatedResource,
    ResourceGroup,
    dataclass_model,
    generate_symbol,
    _UNSET,
    GuidName
)


@dataclass_model
class RoleAssignmentProperties:
    principal_id: str = field(metadata={'rest': 'principalId'})
    role_definition_id: str = field(metadata={'rest': 'roleDefinitionId'})
    condition: Optional[str] = field(default=_UNSET, metadata={'rest': 'condition'})
    condition_version: Optional[Literal['2.0']] = field(default=_UNSET, metadata={'rest': 'conditionVersion'})
    delegated_managed_identity_resource_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'delegatedManagedIdentityResourceId'})
    description: Optional[str] = field(default=_UNSET, metadata={'rest': 'description'})
    principal_type: Optional[Literal['Device', 'ForeignGroup', 'Group', 'ServicePrincipal', 'User']] = field(default=_UNSET, metadata={'rest': 'principalType'})


@dataclass_model
class RoleAssignment(Resource):
    properties: RoleAssignmentProperties = field(metadata={'rest': 'properties'})
    _resource: ClassVar[Literal['Microsoft.Authorization/roleAssignments']] = 'Microsoft.Authorization/roleAssignments'
    _version: ClassVar[str] = '2022-04-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("role"), init=False, repr=False)
