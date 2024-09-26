# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import json
from typing import IO, Dict, Iterable, TypeVar, Generic, TYPE_CHECKING, Literal, ContextManager

from dotenv import load_dotenv
from azure.core import PipelineClient
from azure.core.pipeline.transport import RequestsTransport
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

from .resources import CloudMachineDeployment, StorageAccount


def load_dev_environment():
    azd_dir = os.path.join(os.getcwd(), ".azure")
    if not os.path.isdir(azd_dir):
        raise RuntimeError("No '.azure' directory found in current working dir. Please run 'azd init' with the Minimal template.")

    try:
        azd_env_name = os.environ['AZURE_ENV_NAME']
    except KeyError:
        with open(os.path.join(azd_dir, "config.json")) as azd_config:
            azd_env_name = json.load(azd_config)["defaultEnvironment"]

    env_loaded = load_dotenv(os.path.join(azd_dir, azd_env_name, ".env"), override=True)
    if not env_loaded:
        raise RuntimeError("No cloudmachine infrastructure loaded. Please run 'azd provision' to provision cloudmachine resources.")



class CloudMachineStorage:
    
    def __init__(self, deployment: CloudMachineDeployment):
        self._storage_accounts: Dict[str, str] = {}
        endpoint = os.environ['AZURE_STORAGE_ACCOUNT_BLOB_ENDPOINT']
        self._client = BlobServiceClient(
            account_url=endpoint,
            credential=DefaultAzureCredential()
        )
        self._default_container = self._client.get_container_client("default")

    # def _list_accounts(self, deployment):
    #     for rg in deployment.groups:
    #         for resource in rg.resources:
    #             if isinstance(resource, StorageAccount):

    def upload(self, name: str, filedata: IO[bytes]) -> None:
        self._default_container.upload_blob(name, filedata)

    def download(self) -> Iterable[bytes]:
        return self._default_container.download_blob()

    def close(self) -> None:
        self._client.close()
