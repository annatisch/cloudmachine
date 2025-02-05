from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Mapping, Self, Tuple, TypedDict, Union, Unpack, overload, Optional, Any, Type, TypeVar

from azure.cloudmachine.resources.resourcegroup._resource import ResourceGroup

from ...._bicep.expressions import Expression, ModuleSymbol, Output, Parameter, ResourceGroupSymbol, ResourceSymbol
from ...._setting import StoredPrioritizedSetting
from ...._resource import (
    Resource,
    _ClientResource,
    _build_envs,
)

from .._resource import _DEFAULT_AI_SERVICES, AIServices


if TYPE_CHECKING:
    from .. import CognitiveServicesAccountParams
    from . import DeploymentParams


class DeploymentKwargs(TypedDict, total=False):
    model: str
    format: str
    version: str
    sku: str
    capacity: int
    rai_policy: str

_DEFAULT_DEPLOYMENT: 'DeploymentParams' = {'model': {}, 'sku': {}}

ClientType = TypeVar("ClientType")


class AIDeployment(_ClientResource):
    identifier: Literal["ai:model"] = "ai:model"
    module: Literal["br/public:avm/res/cognitive-services/account"] = "br/public:avm/res/cognitive-services/account"
    DEFAULTS: 'CognitiveServicesAccountParams' = _DEFAULT_AI_SERVICES
    DEFAULT_DEPLOYMENT: 'DeploymentParams' = _DEFAULT_DEPLOYMENT
    resource: Literal["Microsoft.CognitiveServices/accounts/deployments"]
    properties: 'CognitiveServicesAccountParams'

    def __init__(
            self,
            properties: Optional['DeploymentParams'] = None,
            /,
            account_name: Optional[str] = None,
            deployment_name: Optional[str] = None,
            **kwargs: Unpack['DeploymentKwargs']
    ) -> None:
        account_params: 'CognitiveServicesAccountParams' = {}
        if account_name:
            account_params['name'] = account_name
        deployment_params: 'DeploymentParams' = properties or {'model': {}, 'sku': {}}
        if deployment_name:
            deployment_params['name'] = deployment_params
        if 'model' in kwargs:
            deployment_params['model']['name'] = kwargs.pop('model')
        if 'format' in kwargs:
            deployment_params['model']['format'] = kwargs.pop('format')
        if 'version' in kwargs:
            deployment_params['model']['version'] = kwargs.pop('version')
        if 'sku' in kwargs:
            deployment_params['sku']['name'] = kwargs.pop('sku')
        if 'capacity' in kwargs:
            deployment_params['sku']['capacity'] = kwargs.pop('capacity')
        if 'rai_policy' in kwargs:
            deployment_params['raiPolicyName'] = kwargs.pop('rai_policy')
        account_params["deployments"] = [deployment_params]
        super().__init__(
            properties=account_params,
            service_prefix=["ai"],
            **kwargs
        )
        self.deployment_name = StoredPrioritizedSetting(
            name='deployment_name',
            env_vars=_build_envs(self._prefixes, ['DEPLOYMENT_NAME']),
        )
        self.deployment_endpoint = StoredPrioritizedSetting(
            name='deployment_endpoint',
            env_vars=_build_envs(self._prefixes, ['DEPLOYMENT_ENDPOINT']),
            system_hook=self._build_deployment_endpoint
        )
        self.model_name = StoredPrioritizedSetting(
            name='model_name',
            env_vars=_build_envs(self._prefixes, ['MODEL_NAME']),
        )
        self.model_version = StoredPrioritizedSetting(
            name='model_version',
            env_vars=_build_envs(self._prefixes, ['MODEL_VERSION']),
        )
        self._settings['deployment_name'] = self.deployment_name
        self._settings['model_name'] = self.model_name
        self._settings['model_version'] = self.model_version

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
    def reference(cls, resource_id: str, /) -> Self:
        ...
    @overload
    def reference(
            cls,
            *,
            account_name: str,
            deployment_name: str,
            resource_group: Optional[Union[str, ResourceGroup]] = None,
            subscription: Optional[str] = None,
    ) -> Self:
        ...
    @classmethod
    def reference(
            cls,
            resource_id: Optional[str] = None,
            *,
            account_name: Optional[str] = None,
            deployment_name: Optional[str] = None,
            resource_group: Optional[str] = None,
            subscription: Optional[str] = None
    ) -> Self:
        if resource_id:
            return super().reference(resource_id)
        from . import MODULE_RESOURCE, MODULE_VERSION
        resource = f"{MODULE_RESOURCE}@{MODULE_VERSION}"
        parent = AIServices.reference(
            name=account_name,
            resource_group=resource_group,
            subscription=subscription
        )
        existing = super().reference(resource=resource, name=deployment_name, parent=parent)
        existing.deployment_name.set_value(deployment_name)
        return existing

    def _build_endpoint(self) -> str:
        return f"https://{self.name()}.openai.azure.com/"

    def _build_deployment_endpoint(self) -> str:
        return f"https://{self.name()}.openai.azure.com/openai/deployments/{self.deployment_name}"

    def _merge_deployments(
            self,
            deployments: List['DeploymentParams'],
            new_deployment: 'DeploymentParams',
            *,
            parameters: Dict[str, Parameter],
    ) -> Tuple['DeploymentParams', List['DeploymentParams']]:
        deployment_name = new_deployment.get('name') or parameters['defaultName']
        existing = False
        for deployment in deployments:
            if deployment['name'] == deployment_name:
                existing = True
                deployment['model'].update(new_deployment['model'])
                deployment['sku'].update(new_deployment['sku'])
                if 'raiPolicyName' in new_deployment:
                    deployment['raiPolicyName'] = new_deployment['raiPolicyName']
        if not existing:
            deployment: 'DeploymentParams' = dict(self.DEFAULT_DEPLOYMENT)
            deployment['name'] = deployment_name
            deployment['model'].update(new_deployment['model'])
            deployment['sku'].update(new_deployment['sku'])
            if 'raiPolicyName' in new_deployment:
                deployment['raiPolicyName'] = new_deployment['raiPolicyName']
            deployments.append(deployment)
        return deployment, deployments
 
    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            attrname: Optional[str],
            resource_group: Union[str, ResourceGroupSymbol],
            name: Union[str, Expression],
            model: Optional[str] = None,
            version: Optional[str] = None,
            parent: Optional[ResourceSymbol] = None,
            **kwargs
    ):
        suffix = self._get_suffix()
        if isinstance(name, str):
            url_suffix = name
        else:
            url_suffix = name.format()
        if parent:
            outputs = {}
            outputs[f"AZURE_AI_DEPLOYMENT_NAME{suffix}"] = name
            outputs[f"AZURE_AI_MODEL_NAME{suffix}"] =  Output('properties.model.name', symbol)
            outputs[f"AZURE_AI_MODEL_VERSION{suffix}"] = Output('properties.model.version', symbol)
            outputs[f"AZURE_AI_MODEL_ENDPOINT{suffix}"] = Output(
                "properties.endpoint",
                parent
            ).format(suffix=f"deployments/{url_suffix}")
        else:
            outputs = super()._outputs(symbol=symbol, attrname=attrname, resource_group=resource_group, **kwargs)
            outputs[f"AZURE_AI_DEPLOYMENT_NAME{suffix}"] = name
            outputs[f"AZURE_AI_MODEL_NAME{suffix}"] = model
            outputs[f"AZURE_AI_MODEL_VERSION{suffix}"] = version
            outputs[f"AZURE_AI_ENDPOINT{suffix}"] = Output(
                "outputs.endpoint",
                symbol
            )
            outputs[f"AZURE_AI_MODEL_ENDPOINT{suffix}"] = Output(
                "outputs.endpoint",
                symbol
            ).format(suffix=f"deployments/{url_suffix}")
        return outputs

    def _merge_params(
            self,
            params: 'CognitiveServicesAccountParams',
            *,
            symbol: ModuleSymbol,
            parameters: Dict[str, Parameter],
            attrname: Optional[str] = None,
            **kwargs
    ) -> Dict[str, Any]:
        new_deployment = self.properties["deployments"][0]
        updated_deployment, deployments = self._merge_deployments(
            params.pop("deployments", []),
            new_deployment,
            parameters=parameters,
        )
        output_config = super()._merge_params(params, symbol=symbol, attrname=attrname, **kwargs)
        params["deployments"] = deployments
        output_config['name'] = updated_deployment['name']
        output_config['model'] = updated_deployment['model']['name']
        output_config['version'] = updated_deployment['model']['version']
        return output_config


_DEFAULT_AI_CHAT: 'DeploymentParams' = {
    'model': {
        'name': 'gpt-4o-mini',
        'format': 'OpenAI',
        'version': '2024-07-18'
    },
    'sku': {
        'name': 'Standard',
        'capacity': 30
    }
}

class AIChatCompletions(AIDeployment):
    identifier: Literal["ai:model:chat"] = "ai:model:chat"
    DEFAULT_DEPLOYMENT: 'DeploymentParams' = _DEFAULT_AI_CHAT

    def _build_deployment_endpoint(self) -> str:
        return f"https://{self.name()}.openai.azure.com/openai/deployments/{self.deployment_name}/chat/completions"


_DEFAULT_AI_TEXT_EMBEDDINGS: 'DeploymentParams' = {
    'model': {
        'name': 'text-embedding-ada-002',
        'format': 'OpenAI',
        'version': '2'
    },
    'sku': {
        'name': 'Standard',
        'capacity': 30
    }
}

class AITextEmbeddings(AIDeployment):
    identifier: Literal["ai:model:textembeddings"] = "ai:model:textembeddings"
    DEFAULT_DEPLOYMENT: 'DeploymentParams' = _DEFAULT_AI_TEXT_EMBEDDINGS

    def _build_deployment_endpoint(self) -> str:
        return f"https://{self.name()}.openai.azure.com/openai/deployments/{self.deployment_name}/embeddings"
