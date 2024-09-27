# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import IO, Any, ClassVar, Iterable, Dict, Literal, TypedDict, Tuple, Union
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

class UserIdentityProperties(TypedDict, total=False):
    clientId: str
    principalId: str


class UserAssignedIdentities(dict):
    def __init__(self, *identities: Tuple[Union[str, LocatedResource], UserIdentityProperties]):
        self._identities = identities
        super().__init__()

    def __bool__(self) -> bool:
        return bool(self._identities)

    def __repr__(self) -> str:
        return repr(self._identities)

    def items(self) -> Iterable[Tuple[Any, Any]]:
        return self._identities


@dataclass_model
class ManagedIdentity(LocatedResource):
    _resource: ClassVar[Literal['Microsoft.ManagedIdentity/userAssignedIdentities']] = 'Microsoft.ManagedIdentity/userAssignedIdentities'
    _version: ClassVar[str] = '2023-01-31'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("ma"), init=False, repr=False)
