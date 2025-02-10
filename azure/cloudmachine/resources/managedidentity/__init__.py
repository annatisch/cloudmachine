from typing import TYPE_CHECKING, List, Literal, Self, TypedDict, Union, Unpack, overload, Optional, Dict
from typing_extensions import TypeVar

from ...resources.resourcegroup import ResourceGroup
from ..._bicep.expressions import Output, ResourceSymbol, Parameter
from ..._parameters import DEFAULT_NAME, LOCATION, AZD_TAGS
from ..._resource import FieldType, Resource, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from .types import UserAssignedIdentityResource


_DEFAULT_USER_ASSIGNED_IDENTITY: 'UserAssignedIdentityResource' = {}


class UserAssignedIdentityKwargs(TypedDict, total=False):
    # lock: 'Lock'
    # """The lock settings of the service."""
    location: Union[str, Parameter[str]]
    """Location of the Resource Group. It uses the deployment's location when not provided."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Tags of the Resource Group."""


UserAssignedIdentityResourceType = TypeVar('UserAssignedIdentityResourceType', default='UserAssignedIdentityResource')

class UserAssignedIdentity(Resource[UserAssignedIdentityResourceType]):
    DEFAULTS: 'UserAssignedIdentityResource' = _DEFAULT_USER_ASSIGNED_IDENTITY
    resource: Literal["Microsoft.ManagedIdentity/userAssignedIdentities"]
    properties: UserAssignedIdentityResourceType

    @overload
    def __init__(
            self,
            properties: Optional['UserAssignedIdentityResource'] = None,
            /,
            name: Optional[Union[str, Parameter[str]]] = None,
            **kwargs: Unpack['UserAssignedIdentityKwargs']
    ) -> None:
        ...
    @overload
    def __init__(
            self,
            properties: ResourceReference,
            /,
            existing: Literal[True],
    ) -> None:
        ...
    def __init__(
            self,
            properties = None,
            /,
            name=None,
            existing=False,
            **kwargs: Unpack['UserAssignedIdentityKwargs']
    ) -> None:
        extensions: ExtensionResources = {}
        if not existing:
            properties = properties or {}
            if name:
                properties['name'] = name
            if 'location' in kwargs:
                properties['location'] = kwargs.pop('location')
            if 'tags' in kwargs:
                properties['tags'] = kwargs.pop('tags')
        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=["identity"],
            existing=existing,
            **kwargs
        )

    @property
    def resource(self) -> str:
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
            *,
            name: str,
            resource_group: Optional[Union[str, 'ResourceGroup']] = None,
    ) -> 'UserAssignedIdentity[ResourceReference]':
        from .types import RESOURCE, VERSION
        resource = f"{RESOURCE}@{VERSION}"
        return super().reference(
            resource=resource,
            name=name,
            resource_group=resource_group
        )

    def _symbol(self) -> ResourceSymbol:
        resource_ref = self.resource.split("/")[-1].lower()
        if resource_ref.endswith("ies"):
            resource_ref = resource_ref.rstrip("ies") + "y"
        else:
            resource_ref = resource_ref.rstrip('s')
        symbol = f"{resource_ref}{self._suffix.lower()}" if self._suffix else resource_ref
        return ResourceSymbol(symbol, principal_id="properties.principalId")

    def _outputs(self, symbol, **kwargs) -> List[Output]:
        return [Output("AZURE_CLIENT_ID", "properties.clientId", symbol)]
    
    def _find_identity(self, fields, parameters, index = 0):
        return None


def _add_defaults(
        field: FieldType,
        *,
        parameters: Dict[str, Parameter]
):
    if field.existing:
        return
    if 'name' not in field.properties:
        field.properties['name'] = DEFAULT_NAME
    if 'location' not in field.properties:
        field.properties['location'] = LOCATION
    if 'tags' not in field.properties:
        field.properties['tags'] = AZD_TAGS
