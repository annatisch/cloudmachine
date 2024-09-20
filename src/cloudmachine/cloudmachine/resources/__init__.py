# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import os
import shutil
import copy
from typing import IO, Literal, Dict, Any, Optional, Union, Unpack, overload, List

from ._resource import ResourceGroup, _DEFAULT_LOCATION
from ._storage import StorageAccount, Sku


# @dataclass
# class BlobStorage(Resource):
#     access_ties: Literal["Hot", "Cool", "Premium"] = "Hot"
#     allow_blob_public_acess: bool = True
#     allow_cross_tenant_replication: bool = True
#     allow_shared_key_access: bool = True
#     default_container: str = "default"
#     default_to_oauth_authentication: bool = True
#     delete_retention_policy: Dict[str, str] = {}
#     dns_endpoint_type: Literal["Standard", "AzureDnsZone"] = "Standard"
#     is_hns_enabled: bool = False
#     kind: str = "StorageV2"
#     minimum_tls_version: str = "TLS1_2"
#     supports_https_traffic_only: bool = True
#     public_network_access: Literal["Enabled", "Disabled"] = "Enabled"
#     sku: Dict[str, str] = {"name": "Standard_LRS"}
#     bypass: Optional[Literal["AzureServices"]] = "AzureServices"

DEFAULT_PARAMS = {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "environmentName": {
            "value": "${AZURE_ENV_NAME}"
        },
        "cloudmachine": {
            "value": None
        },
        "location": {
            "value": "${AZURE_LOCATION}"
        }
    }
}

def get_empty_directory(root_path: str, name: str) -> str:
    new_dir = os.path.join(root_path, name)
    try:
        shutil.rmtree(new_dir)
    except FileNotFoundError:
        pass
    os.makedirs(new_dir)

    return new_dir


class CloudMachineDeployment:

    id: str
    name: str
    resources: List[ResourceGroup]

    @overload
    def __init__(
        self,
        *,
        name: str,
        location: str = _DEFAULT_LOCATION,
        host: Literal['appservice'] = 'appservice',  # Union[Literal['appservice', 'container'], AppService, ContainerService]
        storage: Union[bool, StorageAccount] = True,
        fs: bool = False,  # Union[bool, DatalakeStorage]
        db: bool = False, # Union[bool, Literal['tables', 'cosmos'], Tables, Cosmos]
        telemetry: bool = False,
        vault: bool = False,  # Union[bool, KeyVault]
        events: bool = False,
        messaging: bool = False,
    ) -> None:
        ...

    @overload
    def __init__(self, resources: ResourceGroup, /, name: str) -> None:
        ...
    
    def __init__(self, *args, **kwargs) -> None:
        self._name = kwargs['name']
        self._params = copy.deepcopy(DEFAULT_PARAMS)
        if args:
            self.resources = args[0]
        else:
            location = kwargs.pop('location', None) or _DEFAULT_LOCATION()
            self.resources = ResourceGroup(
                location=location,
                tags={"abc": "def"},
            )
            self.resources.add(self._define_storage(kwargs))

    def _define_storage(self, kwargs: Dict[str, Any]) -> Optional[StorageAccount]:
        storage = kwargs.pop('storage', True)
        if storage is True:
            return StorageAccount(
                kind='StorageV2',
                sku=Sku(name='Standard_LRS')
            )
        elif isinstance(storage, StorageAccount):
            return storage
        elif storage is False:
            return None
        else:
            raise TypeError(f"Unexpected type for 'storage' param: '{storage}'.")

    def write(self, root_path: str):
        infra_dir = get_empty_directory(root_path, "infra")
        main_bicep = os.path.join(infra_dir, "main.bicep")
        get_empty_directory(infra_dir, "core")
        with open(main_bicep, 'w') as main:
            main.write("targetScope = 'subscription'\n\n")
            main.write("@minLength(1)\n")
            main.write("@maxLength(64)\n")
            main.write("@description('AZD environment name')\n")
            main.write("param environmentName string\n\n")
            main.write("@minLength(1)\n")
            main.write("@maxLength(64)\n")
            main.write("@description('Cloud Machine name')\n")
            main.write("param cloudmachine string\n\n")
            main.write("@minLength(1)\n")
            main.write("@description('Primary location for all resources')\n")
            main.write("param location string\n\n")
            main.write("var tags = { 'azd-env-name': environmentName, 'cloudmachine-name': cloudmachine }\n")
            main.write("var resourceToken = toLower(uniqueString(subscription().id, cloudmachine, location))\n\n")
            self.resources.write(main)
        params_json = os.path.join(infra_dir, "main.parameters.json")
        with open(params_json, 'w') as params:
            self._params["parameters"]["cloudmachine"]["value"] = self._name
            json.dump(self._params, params, indent=4)
