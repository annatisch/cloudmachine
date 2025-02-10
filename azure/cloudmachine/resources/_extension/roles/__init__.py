from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Self, Type, TypeVar, TypedDict, Union, Unpack, Optional, overload

from ...._resource import Resource, ResourceReference
from ...._bicep.expressions import Output, ResourceSymbol, Parameter
from ....resources.resourcegroup import ResourceGroup

if TYPE_CHECKING:
    from .types import RoleAssignmentResource


_DEFAULT_ROLE_ASSIGNMENT: 'RoleAssignmentResource' = {}


class RoleAssignment(Resource['RoleAssignmentResource']):
    DEFAULTS: 'RoleAssignmentResource' = _DEFAULT_ROLE_ASSIGNMENT
    resource: Literal["Microsoft.Authorization/roleAssignments"]
    properties: 'RoleAssignmentResource'

    def __init__(self, properties: 'RoleAssignmentResource', /, **kwargs) -> None:
        super().__init__(properties=properties, **kwargs)

    @property
    def resource(self) -> Literal["Microsoft.Authorization/roleAssignments"]:
        if self._resource:
            return self._resource
        from .types import RESOURCE
        self._resource = RESOURCE
        return self._resource

    @property
    def version(self) -> str:
        if self._version:
            return self._version
        from .types import VERSION
        self._version = VERSION
        return self._version

    @classmethod
    def reference(
            cls,
            resource: str,
            *,
            name: str,
            resource_group: Optional[Union[str, 'ResourceGroup', Parameter[str]]] = None,
            subscription: Optional[Union[str, Parameter[str]]] = None,
            parent: Optional[Resource] = None,
    ) -> Self[ResourceReference]:
        raise TypeError("Referenced Role Assignments not supported.")

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            attrname: Optional[str],
            resource_group: ResourceSymbol,
            **kwargs
    ) -> Dict[str, Output]:
        return {}
