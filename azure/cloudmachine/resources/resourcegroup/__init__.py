from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Literal, Mapping, Self, Tuple, Type, TypedDict, Union, Unpack, Optional, Any, overload
from typing_extensions import TypeVar

from .._identifiers import ResourceIdentifiers
from ..._parameters import GLOBAL_PARAMS
from ..._bicep.expressions import (
    Expression,
    Output,
    Parameter,
    ResourceSymbol,
    Variable,
    UniqueString,
    Subscription,
)
from ..._bicep.utils import generate_name, generate_suffix
from ..._parameters import LOCATION, DEFAULT_NAME, AZD_TAGS
from ..._resource import Resource, FieldsType, FieldType, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from .types import ResourceGroupResource


_DEFAULT_RESOURCE_GROUP: 'ResourceGroupResource' = {
    'name': GLOBAL_PARAMS['defaultName'],
    'location': GLOBAL_PARAMS['location'],
    'tags': GLOBAL_PARAMS['azdTags'],
}


class ResourceGroupKwargs(TypedDict, total=False):
    # lock: 'Lock'
    # """The lock settings of the service."""
    location: Union[str, Parameter[str]]
    """Location of the Resource Group. It uses the deployment's location when not provided."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Tags of the Resource Group."""


ResourceGroupResourceType = TypeVar('ResourceGroupResourceType', bound=Dict[str, Any], default='ResourceGroupResource')

class ResourceGroup(Resource[ResourceGroupResourceType]):
    DEFAULTS: 'ResourceGroupResource' = _DEFAULT_RESOURCE_GROUP
    resource: Literal["Microsoft.Resources/resourceGroups"]
    properties: ResourceGroupResourceType

    def __init__(
            self,
            properties: Optional['ResourceGroupResource'] = None,
            /,
            name: Optional[Union[str, Parameter[str]]] = None,
            **kwargs: Unpack['ResourceGroupKwargs']
    ) -> None:
        extensions: ExtensionResources = defaultdict(list)
        existing = kwargs.pop('existing', False)
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
            service_prefix=["resource_group"],
            existing=existing,
            identifier=ResourceIdentifiers.resource_group,
            **kwargs
        )

    @classmethod
    def reference(
            cls,
            *,
            name: Union[str, Parameter[str]],
            subscription: Optional[Union[str, Parameter[str]]] = None,
    ) -> 'ResourceGroup[ResourceReference]':
        from .types import RESOURCE, VERSION
        resource = f"{RESOURCE}@{VERSION}"
        existing = super().reference(
            resource=resource,
            name=name,
            subscription=subscription
        )
        return existing

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

    def _build_resource_id(self, *, config_store: Mapping[str, Any]) -> str:
        prefix = f"/subscriptions/{self.subscription(config_store=config_store)}/providers/"
        return prefix + f"{self._resource}/{self.name(config_store=config_store)}"

    def __bicep__(
            self,
            fields: FieldsType,
            *,
            parameters: Dict[str, Parameter],
            **kwargs
    ) -> Tuple[ResourceSymbol, ...]:
        self._set_suffix(self.properties.get('name', ''))
        if self._existing:
            properties = {'name': self.properties['name']}
            if self.properties.get('subscription'):
                properties['scope'] = Subscription(self.properties['subscription'])
            symbol = self._symbol()
            field = FieldType(
                resource=self.resource,
                properties=properties,
                symbol=symbol,
                outputs={},
                resource_group=symbol,
                version=self.version,
                extensions={},
                existing=True,
                name=self.properties['name'],
                add_defaults=None,
            )
            fields[self._get_field_id(symbol, ())] = field
            return (symbol,)

        field = self._find_last_resource_match(fields, name=self.properties.get('name'))
        if field:
            properties = field.properties
            symbol = field.symbol
        else:
            properties = {}
            symbol = self._symbol()
            field = FieldType(
                resource=self.resource,
                properties=properties,
                symbol=symbol,
                outputs={},
                resource_group=symbol,
                version=self.version,
                extensions={},
                existing=False,
                name=self.properties.get('name'),
                add_defaults=self._add_defaults
            )
            fields[self._get_field_id(symbol, ())] = field
        self._merge_properties(properties, self.properties, symbol=symbol, resource_group=symbol)
        self._add_parameters(field.properties, parameters)
        return (symbol,)
