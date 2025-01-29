from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Self, Unpack, overload, Optional, Any, Type, TypeVar

from ....._bicep.expressions import ModuleSymbol, Output, Parameter
from ....._setting import StoredPrioritizedSetting
from ....._resource import (
    Resource,
    _ClientResource,
    _convert_str_from_setting,
    _build_envs,
    _convert_to_str
)
from ..._resource import _DEFAULT_STORAGE_ACCOUNT
from .._resource import _DEFAULT_FILE_STORAGE


if TYPE_CHECKING:
    from .. import FileServiceParams
    from ... import StorageAccountParams
    from . import ShareParams, ShareKwargs
    from azure.storage.fileshare import ShareClient

_DEFAULT_SHARE: 'ShareParams' = {}

ClientType = TypeVar("ClientType")


class FileShare(_ClientResource):
    resource: Literal["Microsoft.Storage/storageAccounts/fileServices/shares"] = "Microsoft.Storage/storageAccounts/fileServices/shares"
    module: Literal["br/public:avm/res/storage/storage-account:0.14.0"] = "br/public:avm/res/storage/storage-account:0.14.0"
    identifier: Literal["storage:files:share"] = "storage:files:share"
    defaults: 'StorageAccountParams' = _DEFAULT_STORAGE_ACCOUNT
    default_services: 'FileServiceParams' = _DEFAULT_FILE_STORAGE
    default_share: 'ShareParams' = _DEFAULT_SHARE
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
            convert=_convert_str_from_setting,
            to_str=_convert_to_str,
        )
        self.share_endpoint = StoredPrioritizedSetting(
            name='share_endpoint',
            env_vars=_build_envs(self._prefixes, ['SHARE_ENDPOINT']),
            convert=_convert_str_from_setting,
            to_str=_convert_to_str,
        )
        self._settings['share_name'] = self.share_name
        self._settings['share_endpoint'] = self.share_endpoint

    def _merge_shares(
            self,
            shares: List['ShareParams'],
            new_share: 'ShareParams',
            *,
            symbol: ModuleSymbol,
            parameters: Dict[str, Parameter],
            identity: ModuleSymbol,
    ) -> List['ShareParams']:
        share_name = new_share.get('name') or parameters['cloudmachineId']
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
            share = dict(self.default_share)
            share.update(new_share)
            self._update_role_assignments(
                share,
                symbol=symbol,
                identity=identity,
                user_principal=parameters.get("principalId")
            )
            shares.append(share)
        return share_name, shares
 
    def _merge_params(
            self,
            params: 'StorageAccountParams',
            *,
            symbol: ModuleSymbol,
            parameters: Dict[str, Parameter],
            identity: ModuleSymbol,
            attrname: Optional[str] = None,
            **kwargs
    ) -> Dict[str, Output]:
        new_share = self.properties["fileServices"]["shares"][0]
        file_services = params.pop("fileServices", dict(self.default_services))
        share_name, shares = self._merge_shares(
            file_services.pop("shares", []),
            new_share,
            parameters=parameters,
            identity=identity,
            symbol=symbol
        )
        file_services["shares"] = shares
        outputs = super()._merge_params(params, symbol=symbol, attrname=attrname)
        params.update(self.properties)
        params["fileServices"] = file_services
        
        suffix = (attrname or self._suffix).upper()
        if isinstance(share_name, str):
            share_suffix = share_name
        else:
            share_suffix = share_name.format()
        outputs[f"AZURE_FILES_ENDPOINT_{suffix}"] = Output("outputs.serviceEndpoints.file", symbol)
        outputs[f"AZURE_FILES_SHARE_ENDPOINT_{suffix}"] = Output(
            "outputs.serviceEndpoints.file",
            symbol
        ).format(suffix=f"/{share_suffix}")
        outputs[f"AZURE_FILES_SHARE_NAME_{suffix}"] = share_name
        return outputs

    @overload
    def __call__(
            self,
            cls: Callable[..., ClientType],
            /,
            *,
            transport: Any = None,
            options: Optional[Dict[str, Any]] = None,
    ) -> ClientType:
        ...
    @overload
    def __call__(self, *, transport: Any = None, options: Optional[Dict[str, Any]] = None) -> 'ShareClient':
        ...
    @overload
    def __call__(self, cls: Type[Resource], /) -> Self:
        ...
    def __call__(self, cls=None, /, *, transport=None, options=None):
        options = options or {}
        if transport:
            options['transport'] = transport
        try:
            # First we check if it's a Resource type or whether it has 'from_resource' constructor
            return super()(self, cls, options=options)
        except TypeError:
            pass
        kwargs = {}
        kwargs['credential'] = self.credential()
        try:
            kwargs['api_version'] = self.api_version()
        except RuntimeError:
            pass
        try:
            kwargs['audience'] = self.audience()
        except RuntimeError:
            pass
        kwargs.update(self.client_options())
        kwargs.update(options)
        if cls and cls.__name__ != 'ShareClient':
            client = cls(self.share_endpoint(), **kwargs)
        else:
            from azure.storage.fileshare import ShareClient
            try:
                client = ShareClient.from_share_url(
                    share_url=self.share_endpoint(),
                    **kwargs
                )
            except RuntimeError:
                client = ShareClient(
                    self.endpoint(),
                    self.share_name(),
                    **kwargs
                )
        client.__resource_settings__ = self
        return client
