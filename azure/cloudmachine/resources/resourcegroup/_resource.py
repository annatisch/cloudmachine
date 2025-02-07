from typing import TYPE_CHECKING, Dict, List, Literal, Self, Tuple, Type, Union, Unpack, Optional, Any, overload

from ..._bicep.expressions import (
    Expression,
    Output,
    Parameter,
    ModuleSymbol,
    ResourceGroupSymbol,
    ResourceSymbol,
    Variable,
    UniqueString,
    Subscription,
)
from ..._bicep.utils import generate_name, generate_suffix
from ..._resource import Resource, FieldsType, FieldType

if TYPE_CHECKING:
    from . import ResourceGroupParams, ResourceGroupKwargs


_DEFAULT_RESOURCE_GROUP: 'ResourceGroupParams' = {
}


class ResourceGroup(Resource):
    identifier: Literal["resourcegroup"] = "resourcegroup"
    module: Literal["br/public:avm/res/resources/resource-group"] = "br/public:avm/res/resources/resource-group"
    DEFAULTS: 'ResourceGroupParams' = _DEFAULT_RESOURCE_GROUP
    resource: Literal["Microsoft.Resources/resourceGroups"]
    properties: 'ResourceGroupParams'

    def __init__(
            self,
            properties: Optional['ResourceGroupParams'] = None,
            /,
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
            subscription: Optional[str] = None,
    ) -> Self:
        ...
    @classmethod
    def reference(
            cls,
            resource_id: Optional[str] = None,
            *,
            name: Optional[str] = None,
            subscription: Optional[str] = None,
    ) -> Self:
        if resource_id:
            return super().reference(resource_id)
        from . import MODULE_RESOURCE, MODULE_VERSION
        resource = f"{MODULE_RESOURCE}@{MODULE_VERSION}"
        existing = super().reference(
            resource=resource,
            name=name,
            subscription=subscription
        )
        return existing

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

    def __bicep__(
            self,
            fields: FieldsType,
            *,
            parameters: Dict[str, Parameter],
            attrname: Optional[str] = None,
            **kwargs
    ) -> FieldType:
        field_id = self._component.__name__ if self._component else '__main__'
        if self._existing:
            rg_name = self._reference['name']
            base_symbol = self._symbol()
            symbol = ResourceGroupSymbol(
                symbol=base_symbol._value,
                name=base_symbol.name,
                existing=True
            )
            field = FieldType(
                self.resource,
                {'name': rg_name},
                symbol,
                {},
                symbol,
                self.version
            )
            fields[f"{field_id}.{attrname if attrname else symbol.resolve()}"] = field
            return symbol
        try:
            rg_name = self.properties['name']
        except KeyError:
            rg_name = parameters['defaultName']

        symbol = ResourceGroupSymbol(
            symbol=self._symbol()._value,
            name=rg_name,
        )
        field = self._find_resource_match(fields, symbol, rg_name)
        if field:
            reference = field[0]
            params = field[1]
            symbol = field[2]
            outputs = field[3]
        else:
            reference = self.module
            params = self.DEFAULTS.copy()
            params['name'] = rg_name
            outputs = {}
            field = FieldType(reference, params, symbol, outputs, symbol, self.tag or self.version)

        self._merge_params(params, symbol=symbol, resource_group=symbol)
        self._substitute_globals(params, parameters)
        fields[f"{field_id}.{attrname if attrname else symbol.resolve()}"] = field
        return symbol
