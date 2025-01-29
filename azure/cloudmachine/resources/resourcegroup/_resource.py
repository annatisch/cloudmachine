from typing import TYPE_CHECKING, Dict, List, Literal, Tuple, Type, Union, Unpack, Optional, Any

from ..._bicep.expressions import Expression, Output, Parameter, ModuleSymbol, ResourceGroupSymbol, ResourceSymbol, Variable
from ..._bicep.utils import generate_name, generate_suffix
from ..._resource import Resource, FieldsType, FieldType, ResourcesType

if TYPE_CHECKING:
    from . import ResourceGroupParams, ResourceGroupKwargs


_DEFAULT_RESOURCE_GROUP: 'ResourceGroupParams' = {
}


class ResourceGroup(Resource):
    resource: Literal["Microsoft.Resources/resourceGroups"] = "Microsoft.Resources/resourceGroups"
    module: Literal["br/public:avm/res/resources/resource-group:0.4.0"] = "br/public:avm/res/resources/resource-group:0.4.0"
    identifier: Literal["resourcegroup"] = "resourcegroup"
    defaults: 'ResourceGroupParams' = _DEFAULT_RESOURCE_GROUP
    properties: 'ResourceGroupParams'

    def __init__(
            self,
            properties: Optional['ResourceGroupParams'] = None,
            resource_group_name: Optional[str] = None,
            **kwargs: Unpack['ResourceGroupKwargs']
    ) -> None:
        rg_params: 'ResourceGroupParams' = properties or {}
        if resource_group_name:
            rg_params['name'] = resource_group_name
        if 'enable_telemetry' in kwargs:
            rg_params['enableTelemetry'] = kwargs.pop('enable_telemetry')
        if 'location' in kwargs:
            rg_params['location'] = kwargs.pop('location')
        if 'lock' in kwargs:
            rg_params['lock'] = kwargs.pop('lock')
        if 'role_assignments' in kwargs:
            rg_params['roleAssignments'] = kwargs.pop('role_assignments')
        if 'tags' in kwargs:
            rg_params['tags'] = kwargs.pop('tags')

        super().__init__(
            properties=rg_params,
            service_prefix=["resource_group"],
            **kwargs
        )

    def __bicep__(
            self,
            fields: FieldsType,
            resources: ResourcesType,
            *,
            parameters: Dict[str, Parameter],
            **kwargs
    ) -> FieldType:
        rg_name = self.properties.pop('name', parameters['cloudmachineId'])
        var_suffix = rg_name if isinstance(rg_name, str) else "default"
        symbol = ResourceGroupSymbol(
            symbol=self._symbol()._value,
            varname=f"resourcegroup_{var_suffix}_name",
            varvalue=rg_name
        )
        field = self._find_resource_match(fields, symbol, symbol.varname)
        
        # TODO: This probably needs fixing as self.properties shouldn't be mutated....
        self.properties["name"] = symbol.varname
        resource_id = (self.module, symbol)
        if field:
            reference, params, symbol, outputs, _ = field
        else:
            reference = self.module
            params = self.defaults.copy()
            outputs = {}
            field = (reference, params, symbol, outputs, symbol)
            resources[symbol].append(field)

        identity = self._find_identity(fields)
        role_assignments = params.pop("roleAssignments", [])
        self._merge_params(params, symbol=symbol)
        self._substitute_globals(params, parameters)
        self._update_role_assignments(
            params,
            role_assignments,
            symbol=symbol,
            identity=identity,
            user_principal=parameters.get("principalId")
        )
        return field
