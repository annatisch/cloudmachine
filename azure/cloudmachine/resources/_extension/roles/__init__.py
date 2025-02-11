from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Self, TypedDict, Union, Unpack, Optional, overload
from typing_extensions import TypeVar

from ...._resource import FieldType, Resource, ResourceReference
from ...._bicep.utils import generate_suffix, generate_name
from ...._bicep.expressions import Output, RoleDefinition, Parameter
from ....resources.resourcegroup import ResourceGroup

if TYPE_CHECKING:
    from .types import RoleAssignmentResource


_DEFAULT_ROLE_ASSIGNMENT: 'RoleAssignmentResource' = {}

RoleAssignmentResourceType = TypeVar('RoleAssignmentResourceType', default='RoleAssignmentResource')


class RoleAssignment(Resource[RoleAssignmentResourceType]):
    DEFAULTS: 'RoleAssignmentResource' = _DEFAULT_ROLE_ASSIGNMENT
    resource: Literal["Microsoft.Authorization/roleAssignments"]
    properties: RoleAssignmentResourceType

    def __init__(self, properties: 'RoleAssignmentResource', /, **kwargs) -> None:
        super().__init__(properties, **kwargs)

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
            resource_group: Optional[Union[str, 'ResourceGroup']] = None,
            subscription: Optional[str] = None,
            parent: Optional[Resource] = None,
    ) -> 'RoleAssignment[ResourceReference]':
        raise TypeError("Referenced Role Assignments not supported.")

    def _outputs(self, **kwargs) -> List[Output]:
        return []

    def _set_suffix(self, name):
        return super()._set_suffix(generate_name(name.value))

    def _add_defaults(self, field: FieldType, parameters: Dict[str, Parameter]):
        try:
            role_name = field.properties['properties']['roleDefinitionId']
            field.properties['properties']['roleDefinitionId'] = _BUILT_IN_ROLES[role_name]
            field.properties['properties']['roleDefinitionId'].description = role_name
        except KeyError:
            pass


_BUILT_IN_ROLES: Dict[str, RoleDefinition] = {
    'Contributor': RoleDefinition('b24988ac-6180-42a0-ab88-20f7382dd24c'),
    'Owner': RoleDefinition('8e3af657-a8ff-443c-a75c-2fe8c4bcb635'),
    'Reader': RoleDefinition('acdd72a7-3385-48ef-bd42-f606fba81ae7'),
    'Reader and Data Access': RoleDefinition('c12c1c16-33a1-487b-954d-41c89c60f349'),
    'Role Based Access Control Administrator': RoleDefinition('f58310d9-a9f6-439a-9e8d-f62e7b41a168'),
    'Storage Account Backup Contributor': RoleDefinition('e5e2a7ff-d759-4cd2-bb51-3152d37e2eb1'),
    'Storage Account Contributor': RoleDefinition('17d1049b-9a84-46fb-8f53-869881c3d3ab'),
    'Storage Account Key Operator Service Role': RoleDefinition('81a9662b-bebf-436f-a333-f67b29880f12'),
    'Storage Blob Data Contributor': RoleDefinition('ba92f5b4-2d11-453d-a403-e96b0029c9fe'),
    'Storage Blob Data Owner': RoleDefinition('b7e6dc6d-f1e8-4753-8033-0f276bb0955b'),
    'Storage Blob Data Reader': RoleDefinition('2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'),
    'Storage Blob Delegator': RoleDefinition('db58b8e5-c6ad-4a2a-8342-4190687cbf4a'),
    'Storage File Data Privileged Contributor': RoleDefinition('69566ab7-960f-475b-8e7c-b3118f30c6bd'),
    'Storage File Data Privileged Reader': RoleDefinition('b8eda974-7b85-4f76-af95-65846b26df6d'),
    'Storage File Data SMB Share Contributor': RoleDefinition('0c867c2a-1d8c-454a-a3db-ab2ea1bdc8bb'),
    'Storage File Data SMB Share Elevated Contributor': RoleDefinition('a7264617-510b-434b-a828-9731dc254ea7'),
    'Storage File Data SMB Share Reader': RoleDefinition('aba4ae5f-2193-4029-9191-0cb91df5e314'),
    'Storage Queue Data Contributor': RoleDefinition('974c5e8b-45b9-4653-ba55-5f855dd0fb88'),
    'Storage Queue Data Message Processor': RoleDefinition('8a0f0c08-91a1-4084-bc3d-661d67233fed'),
    'Storage Queue Data Message Sender': RoleDefinition('c6a89b2d-59bc-44d0-9896-0f6e12d7b80a'),
    'Storage Queue Data Reader': RoleDefinition('19e7f393-937e-4f77-808e-94535e297925'),
    'Storage Table Data Contributor': RoleDefinition('0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3'),
    'Storage Table Data Reader': RoleDefinition('76199698-9eea-4c19-bc75-cec21354c6b6'),
    'User Access Administrator': RoleDefinition('18d7d88d-d35e-4fb5-a5c3-7773c20a72d9'),
}
