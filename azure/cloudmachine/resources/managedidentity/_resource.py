from typing import TYPE_CHECKING, Literal, Unpack, overload, Optional, Any

from ..._bicep.expressions import ModuleSymbol, Output
from ..._bicep.utils import generate_name, generate_suffix
from ..._resource import Resource

if TYPE_CHECKING:
    from . import UserAssignedIdentityParams, UserAssignedIdentityKwargs


_DEFAULT_USER_ASSIGNED_IDENTITY: 'UserAssignedIdentityParams' = {
}


class UserAssignedIdentity(Resource):
    resource: Literal["Microsoft.ManagedIdentity/userAssignedIdentities"] = "Microsoft.ManagedIdentity/userAssignedIdentities"
    module: Literal["br/public:avm/res/managed-identity/user-assigned-identity:0.4.0"] = "br/public:avm/res/managed-identity/user-assigned-identity:0.4.0"
    identifier: Literal["userassignedidentity"] = "userassignedidentity"
    defaults: 'UserAssignedIdentityParams' = _DEFAULT_USER_ASSIGNED_IDENTITY
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

    def _symbol(self) -> ModuleSymbol:
        resource_ref = self.resource.split("/")[0].split(".")[1]
        return ModuleSymbol(
            f"{resource_ref.lower()}_{self._suffix}",
            principal_id="outputs.principalId"
        )
    
    def _merge_params(self, params, *, symbol, **kwargs):
        outputs = super()._merge_params(params, symbol=symbol, **kwargs)
        outputs["AZURE_CLIENT_ID"] = Output("outputs.clientId", symbol)
        return outputs

    def _find_identity(self, fields, index = 0):
        index += 1
        return super()._find_identity(fields, index)
