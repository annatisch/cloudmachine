from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Mapping, Self, Tuple, TypedDict, Union, Unpack, overload, Optional, Any, Type
from typing_extensions import TypeVar

from ...resourcegroup import ResourceGroup
from ...._parameters import GLOBAL_PARAMS
from ...._bicep.expressions import Expression, Output, Parameter, ResourceSymbol
from ...._setting import StoredPrioritizedSetting
from ...._resource import (
    ExtensionResources,
    ResourceReference,
    _ClientResource,
    _build_envs,
)

from .. import AIServices

if TYPE_CHECKING:
    from .types import DeploymentResource


class DeploymentKwargs(TypedDict, total=False):
    model: Union[str, Parameter[str]]
    """Deployment model name."""
    format: Union[str, Parameter[str]]
    """Deployment model format."""
    version: Union[str, Parameter[str]]
    """Deployment model version."""
    sku: Union[str, Parameter[str]]
    """The name of the SKU. Ex - P3. It is typically a letter+number code."""
    capacity: Union[int, Parameter[int]]
    """If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted."""
    rai_policy: Union[str, Parameter[str]]
    """The name of RAI policy."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict]]
    """Tags of the resource."""


_DEFAULT_DEPLOYMENT: 'DeploymentResource' = {'name': GLOBAL_PARAMS['defaultName']}
AIDeploymentResourceType = TypeVar('AIDeploymentResourceType', default='DeploymentResource')
ClientType = TypeVar("ClientType")


class AIDeployment(_ClientResource[AIDeploymentResourceType]):
    DEFAULTS: 'DeploymentResource' = _DEFAULT_DEPLOYMENT
    resource: Literal["Microsoft.CognitiveServices/accounts/deployments"]
    properties: AIDeploymentResourceType
    parent: AIServices

    def __init__(
            self,
            properties: Optional['DeploymentResource'] = None,
            /,
            name: Optional[str] = None,
            account: Optional[Union[str, AIServices]] = None,
            **kwargs: Unpack['DeploymentKwargs']
    ) -> None:
        existing = kwargs.pop('existing', False)
        extensions: ExtensionResources = defaultdict(list)
        parent = account if isinstance(account, AIServices) else kwargs.pop('parent', AIServices(name=account))
        if not existing:
            properties = properties or {}
            if 'properties' not in properties:
                properties['properties'] = {}
            if name:
                properties['name'] = name
            if 'model' in kwargs:
                properties['properties']['model'] = properties['properties'].get('model', {})
                properties['properties']['model']['name'] = kwargs.pop('model')
            if 'format' in kwargs:
                properties['properties']['model'] = properties['properties'].get('model', {})
                properties['properties']['model']['format'] = kwargs.pop('format')
            if 'version' in kwargs:
                properties['properties']['model'] = properties['properties'].get('model', {})
                properties['properties']['model']['version'] = kwargs.pop('version')
            if 'sku' in kwargs:
                properties['sku'] = properties.get('sku', {})
                properties['sku']['name'] = kwargs.pop('sku')
            if 'capacity' in kwargs:
                properties['sku'] = properties.get('sku', {})
                properties['sku']['capacity'] = kwargs.pop('capacity')
            if 'rai_policy' in kwargs:
                properties['properties']['raiPolicyName'] = kwargs.pop('rai_policy')
            if 'tags' in kwargs:
                properties['tags'] = kwargs.pop('tags')
        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="deployments",
            service_prefix=kwargs.pop('service_prefix', ["ai_deployment"]),
            **kwargs
        )
        self._properties_to_merge.append('sku')
        self.model_name = StoredPrioritizedSetting(
            name='model_name',
            env_vars=_build_envs(self._prefixes, ['MODEL_NAME']),
        )
        self.model_version = StoredPrioritizedSetting(
            name='model_version',
            env_vars=_build_envs(self._prefixes, ['MODEL_VERSION']),
        )
        self._settings['model_name'] = self.model_name
        self._settings['model_version'] = self.model_version

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
            name: Union[str, Parameter[str]],
            account: Union[str, Parameter[str], AIServices],
            resource_group: Optional[Union[str, Parameter[str], 'ResourceGroup']] = None,
    ) -> 'AIDeployment[ResourceReference]':

        from .types import RESOURCE, VERSION
        resource = f"{RESOURCE}@{VERSION}"
        if isinstance(account, (str, Parameter)):
            parent = AIServices.reference(
                name=account,
                resource_group=resource_group,
            )
        else:
            parent = account
        existing = super().reference(
            resource=resource,
            name=name,
            parent=parent
        )
        existing.name.set_value(name)
        return existing

    def _build_endpoint(self) -> str:
        return f"https://{self.parent.name()}.openai.azure.com/openai/deployments/{self.name()}"

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            attrname: Optional[str],
            resource_group: Union[str, ResourceSymbol],
            parent: Optional[ResourceSymbol] = None,
            **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, attrname=attrname, resource_group=resource_group, **kwargs)
        outputs['model_name'] = Output(f"AZURE_AI_DEPLOYMENT_MODEL_NAME{self._suffix}", 'properties.model.name', symbol)
        outputs['model_version'] = Output(f"AZURE_AI_DEPLOYMENT_MODEL_VERSION{self._suffix}", 'properties.model.version', symbol)
        outputs['endpoint'] = Output(
            f"AZURE_AI_DEPLOYMENT_ENDPOINT{self._suffix}",
            Output("", "properties.endpoint", parent).format("{}openai/deployments/") + outputs['name'].format()
        )
        return outputs


ai_chat_model_param = Parameter("aiChatModel", type=str, default='gpt-4o-mini')
_DEFAULT_AI_CHAT: 'DeploymentResource' = {
    'name': ai_chat_model_param,
    'properties': {
        'model': {
            'name': ai_chat_model_param,
            'format': Parameter("aiChatModelFormat", type=str, default='OpenAI'),
            'version': Parameter("aiChatModelVersion", type=str, default='2024-07-18')
        }
    },
    'sku': {
        'name': Parameter("aiChatModelSku", type=str, default='Standard'),
        'capacity': Parameter("aiChatModelCapacity", type=int, default=30)
    }
}


class AIChat(AIDeployment):
    DEFAULTS: 'DeploymentResource' = _DEFAULT_AI_CHAT

    def __init__(
            self,
            properties: Optional['DeploymentResource'] = None,
            /,
            account: Optional[Union[str, AIServices]] = None,
            **kwargs: Unpack['DeploymentKwargs']
    ) -> None:
        super().__init__(
            properties,
            name=kwargs.get('model'),
            account=account,
            service_prefix=['ai_chat'],
            **kwargs
        )

    @classmethod
    def reference(
            cls,
            *,
            model: Optional[str] = None,
            account: Union[str, AIServices],
            resource_group: Optional[Union[str, 'ResourceGroup']] = None,
    ) -> 'AIChat[ResourceReference]':
        model = model or cls.DEFAULTS['properties']['model']['name']
        existing = super().reference(
            name=model,
            account=account,
            resource_group=resource_group
        )
        existing.model_name.set_value(model)
        return existing

    def _build_endpoint(self) -> str:
        return f"https://{self.parent.name()}.openai.azure.com/openai/deployments/{self.name()}/chat/completions"

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            attrname: Optional[str],
            resource_group: Union[str, ResourceSymbol],
            parent: Optional[ResourceSymbol] = None,
            **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, attrname=attrname, resource_group=resource_group, **kwargs)
        outputs['model_name'] = Output(f"AZURE_AI_CHAT_MODEL_NAME{self._suffix}", 'properties.model.name', symbol)
        outputs['model_version'] = Output(f"AZURE_AI_CHAT_MODEL_VERSION{self._suffix}", 'properties.model.version', symbol)
        outputs['endpoint'] = Output(
            f"AZURE_AI_CHAT_ENDPOINT{self._suffix}",
            Output("", "properties.endpoint", parent).format("{}openai/deployments/") + outputs['name'].format() + "/chat/completions"
        )
        return outputs


ai_embeddings_model_param = Parameter("aiEmbeddingsModel", type=str, default='text-embedding-ada-002')
_DEFAULT_AI_TEXT_EMBEDDINGS: 'DeploymentResource' = {
    'name': ai_embeddings_model_param,
    'properties': {
        'model': {
            'name': ai_embeddings_model_param,
            'format': Parameter("aiEmbeddingsModelFormat", type=str, default='OpenAI'),
            'version': Parameter("aiEmbeddingsModelVersion", type=str, default='2')
        }
    },
    'sku': {
        'name': Parameter("aiEmbeddingsModelSku", type=str, default='Standard'),
        'capacity': Parameter("aiEmbeddingsModelCapacity", type=int, default=30)
    }
}

class AIEmbeddings(AIDeployment[AIDeploymentResourceType]):
    DEFAULTS: 'DeploymentResource' = _DEFAULT_AI_TEXT_EMBEDDINGS

    def __init__(
            self,
            properties: Optional['DeploymentResource'] = None,
            /,
            account: Optional[Union[str, AIServices]] = None,
            **kwargs: Unpack['DeploymentKwargs']
    ) -> None:
        super().__init__(
            properties,
            name=kwargs.get('model'),
            account=account,
            service_prefix=['ai_embeddings'],
            **kwargs
        )

    def _build_endpoint(self) -> str:
        return f"https://{self.parent.name()}.openai.azure.com/openai/deployments/{self.name()}/embeddings"

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            attrname: Optional[str],
            resource_group: Union[str, ResourceSymbol],
            parent: Optional[ResourceSymbol] = None,
            **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, attrname=attrname, resource_group=resource_group, **kwargs)
        outputs['model_name'] = Output(f"AZURE_AI_EMBEDDINGS_MODEL_NAME{self._suffix}", 'properties.model.name', symbol)
        outputs['model_version'] = Output(f"AZURE_AI_EMBEDDINGS_MODEL_VERSION{self._suffix}", 'properties.model.version', symbol)
        outputs['endpoint'] = Output(
            f"AZURE_AI_EMBEDDINGS_ENDPOINT{self._suffix}",
            Output("", "properties.endpoint", parent).format("{}openai/deployments/") + outputs['name'].format() + "/embeddings"
        )
        return outputs