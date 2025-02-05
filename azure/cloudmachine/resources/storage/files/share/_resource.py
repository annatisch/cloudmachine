from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Mapping, Self, Union, Unpack, overload, Optional, Any, Type, TypeVar

from azure.cloudmachine.resources.resourcegroup._resource import ResourceGroup

from ....._bicep.expressions import Expression, ModuleSymbol, Output, Parameter, ResourceGroupSymbol, ResourceSymbol
from ....._setting import StoredPrioritizedSetting
from ....._resource import (
    Resource,
    _ClientResource,
    _build_envs,
)
from ..._resource import _DEFAULT_STORAGE_ACCOUNT
from .._resource import _DEFAULT_FILE_STORAGE, FileShareStorage


if TYPE_CHECKING:
    from .. import FileServiceParams
    from ... import StorageAccountParams
    from . import ShareParams, ShareKwargs
    from azure.storage.fileshare import ShareClient

_DEFAULT_SHARE: 'ShareParams' = {}

ClientType = TypeVar("ClientType")


class FileShare(_ClientResource):
    identifier: Literal["storage:files:share"] = "storage:files:share"
    module: Literal["br/public:avm/res/storage/storage-account"] = "br/public:avm/res/storage/storage-account"
    DEFAULTS: 'StorageAccountParams' = _DEFAULT_STORAGE_ACCOUNT
    DEFAULT_SERVICES: 'FileServiceParams' = _DEFAULT_FILE_STORAGE
    DEFAULT_SHARE: 'ShareParams' = _DEFAULT_SHARE
    resource: Literal["Microsoft.Storage/storageAccounts/fileServices/shares"]
    properties: 'StorageAccountParams'

    def __init__(
            self,
            properties: Optional['ShareParams'] = None,
            storage_name: Optional[str] = None,
            share_name: Optional[str] = None,
            *,
            role_assignments = ['Storage File Data SMB Share Contributor'],
            **kwargs: Unpack['ShareKwargs']
    ) -> None:
        storage_params: 'StorageAccountParams' = {}
        if storage_name:
            storage_params['name'] = storage_name
        file_service_params: 'FileServiceParams' = {}
        share_params: 'ShareParams' = properties or {}
        if share_name:
            share_params['name'] = share_name
        if 'access_tier' in kwargs:
            share_params['accessTier'] = kwargs.pop('access_tier')
        if 'enabled_protocols' in kwargs:
            share_params['enabledProtocols'] = kwargs.pop('enabled_protocols')
        if 'root_squash' in kwargs:
            share_params['rootSquash'] = kwargs.pop('root_squash')
        if 'share_quota' in kwargs:
            share_params['shareQuota'] = kwargs.pop('share_quota')
        if role_assignments:
            share_params['roleAssignments'] = role_assignments
        file_service_params["shares"] = [share_params]
        storage_params["fileServices"] = file_service_params
        super().__init__(
            properties=storage_params,
            service_prefix=["files", "storage"],
            **kwargs
        )
        self.share_name = StoredPrioritizedSetting(
            name='share_name',
            env_vars=_build_envs(self._prefixes, ['SHARE_NAME']),
        )
        self.share_endpoint = StoredPrioritizedSetting(
            name='share_endpoint',
            env_vars=_build_envs(self._prefixes, ['SHARE_ENDPOINT']),
            system_hook=self._build_share_endpoint
        )
        self._settings['share_name'] = self.share_name
        self._settings['share_endpoint'] = self.share_endpoint

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
        share_name: str,
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
            share_name: Optional[str] = None,
            resource_group: Optional[str] = None,
            subscription: Optional[str] = None
    ) -> Self:
        if resource_id:
            return super().reference(resource_id)
        from . import MODULE_RESOURCE, MODULE_VERSION
        resource = f"{MODULE_RESOURCE}@{MODULE_VERSION}"

        parent = FileShareStorage.reference(
            name=account_name,
            resource_group=resource_group,
            subscription=subscription
        )
        existing = super().reference(resource=resource, name=share_name, parent=parent)
        existing.share_name.set_value(share_name)
        return existing

    def _build_endpoint(self) -> str:
        return f"https://{self.name()}.file.core.windows.net/"

    def _build_share_endpoint(self) -> str:
        return f"https://{self.name()}.file.core.windows.net/{self.share_name()}"

    def _merge_shares(
            self,
            shares: List['ShareParams'],
            new_share: 'ShareParams',
            *,
            symbol: ModuleSymbol,
            parameters: Dict[str, Parameter],
            identity: ModuleSymbol,
    ) -> List['ShareParams']:
        share_name = new_share.get('name') or parameters['defaultName']
        existing = False
        for share in shares:
            if share['name'] == share_name:
                existing = True
                role_assignments = share.pop('roleAssignments')
                share.update(new_share)
                self._update_role_assignments(
                    share,
                    role_assignments,
                    symbol=symbol,
                    identity=identity,
                    user_principal=parameters.get("principalId")
                )
        if not existing:
            share = dict(self.DEFAULT_SHARE)
            share['name'] = share_name
            share.update(new_share)
            self._update_role_assignments(
                share,
                symbol=symbol,
                identity=identity,
                user_principal=parameters.get("principalId")
            )
            shares.append(share)
        return share_name, shares
 
    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            name: Union[str, Expression],
            parent: Optional[ResourceSymbol] = None,
            **kwargs
        ) -> Dict[str, Union[Output, str]]:
        suffix = self._get_suffix()
        if isinstance(name, str):
            url_suffix = name
        else:
            url_suffix = name.format()
        if parent:
            outputs = {}
            outputs[f"AZURE_FILES_SHARE_ENDPOINT{suffix}"] = Output(
                "properties.primaryEndpoints.file",
                symbol
            ).format(suffix=f"{url_suffix}")
            outputs[f"AZURE_FILES_SHARE_NAME{suffix}"] = name
        else:
            outputs = super()._outputs(symbol=symbol, **kwargs)
            outputs[f"AZURE_FILES_ENDPOINT{suffix}"] = Output("outputs.serviceEndpoints.file", symbol)
            outputs[f"AZURE_FILES_SHARE_ENDPOINT{suffix}"] = Output(
                "outputs.serviceEndpoints.file",
                symbol
            ).format(suffix=f"{url_suffix}")
            outputs[f"AZURE_FILES_SHARE_NAME{suffix}"] = name
        return outputs

    def _merge_params(
            self,
            params: 'StorageAccountParams',
            *,
            symbol: ModuleSymbol,
            parameters: Dict[str, Parameter],
            identity: ModuleSymbol,
            attrname: Optional[str] = None,
            **kwargs
    ) -> Dict[str, Any]:
        new_share = self.properties["fileServices"]["shares"][0]
        file_services = params.pop("fileServices", dict(self.DEFAULT_SERVICES))
        share_name, shares = self._merge_shares(
            file_services.pop("shares", []),
            new_share,
            parameters=parameters,
            identity=identity,
            symbol=symbol
        )
        file_services["shares"] = shares
        output_config = super()._merge_params(params, symbol=symbol, attrname=attrname, **kwargs)
        output_config['name'] = share_name
        params["fileServices"] = file_services
        return output_config
