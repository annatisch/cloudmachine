from typing import TYPE_CHECKING, Literal, Self, Union, Unpack, overload, Optional, Any

from azure.cloudmachine.resources.resourcegroup._resource import ResourceGroup

from ..._bicep.expressions import ModuleSymbol, Output, ResourceSymbol
from ..._bicep.utils import generate_name, generate_suffix
from ..._resource import Resource

if TYPE_CHECKING:
    from . import UserAssignedIdentityParams, UserAssignedIdentityKwargs


_DEFAULT_USER_ASSIGNED_IDENTITY: 'UserAssignedIdentityParams' = {
}


class UserAssignedIdentity(Resource):
    identifier: Literal["userassignedidentity"] = "userassignedidentity"
    module: Literal["br/public:avm/res/managed-identity/user-assigned-identity"] = "br/public:avm/res/managed-identity/user-assigned-identity"
    DEFAULTS: 'UserAssignedIdentityParams' = _DEFAULT_USER_ASSIGNED_IDENTITY
    resource: Literal["Microsoft.ManagedIdentity/userAssignedIdentities"]
    properties: 'UserAssignedIdentityParams'

    def __init__(
            self,
            properties: Optional['UserAssignedIdentityParams'] = None,
            identity_name: Optional[str] = None,
            **kwargs: Unpack['UserAssignedIdentityKwargs']
    ) -> None:
        identity_params: 'UserAssignedIdentityParams' = properties or {}
        if identity_name:
            identity_params['name'] = identity_name
        if 'enable_telemetry' in kwargs:
            identity_params['enableTelemetry'] = kwargs.pop('enable_telemetry')
        if 'federated_identity_credentials' in kwargs:
            identity_params['federatedIdentityCredentials'] = kwargs.pop('federated_identity_credentials')
        if 'location' in kwargs:
            identity_params['location'] = kwargs.pop('location')
        if 'lock' in kwargs:
            identity_params['lock'] = kwargs.pop('lock')
        if 'role_assignments' in kwargs:
            identity_params['roleAssignments'] = kwargs.pop('role_assignments')
        if 'tags' in kwargs:
            identity_params['tags'] = kwargs.pop('tags')
        super().__init__(
            properties=identity_params,
            service_prefix=["identity"],
            **kwargs
        )

    @property
    def resource(self) -> str:
        from . import MODULE_RESOURCE
        return MODULE_RESOURCE

    @property
    def version(self) -> str:
        from . import MODULE_VERSION
        return MODULE_VERSION

    @property
    def tag(self) -> str:
        from . import MODULE_TAG
        return MODULE_TAG

    @overload
    @classmethod
    def reference(cls, resource_id: str, /) -> Self:
        ...
    @overload
    @classmethod
    def reference(
            cls,
            *,
            name: str,
            resource_group: Optional[Union[str, ResourceGroup]] = None,
            subscription: Optional[str] = None,
    ) -> Self:
        ...
    @classmethod
    def reference(
            cls,
            resource_id: Optional[str] = None,
            *,
            name: Optional[str] = None,
            resource_group: Optional[Union[str, ResourceGroup]] = None,
            subscription: Optional[str] = None,
    ) -> Self:
        if resource_id:
            return super().reference(resource_id)
        from . import MODULE_RESOURCE, MODULE_VERSION
        resource = f"{MODULE_RESOURCE}@{MODULE_VERSION}"
        return super().reference(
            resource=resource,
            name=name,
            resource_group=resource_group,
            subscription=subscription
        )

    def _symbol(self) -> ModuleSymbol:
        resource_ref = self.resource.split("/")[0].split(".")[1]
        if self._existing:
            return ResourceSymbol(
                f"{resource_ref.lower()}_{self._suffix}",
                principal_id="properties.principalId"
            )
        return ModuleSymbol(
            f"{resource_ref.lower()}_{self._suffix}",
            principal_id="outputs.principalId"
        )

    def _outputs(self, symbol, **kwargs):
        if self._existing:
            return {"AZURE_CLIENT_ID": Output("properties.clientId", symbol)}
        return {"AZURE_CLIENT_ID": Output("outputs.clientId", symbol)}
    
    def _find_identity(self, fields, parameters, index = 0):
        return None
