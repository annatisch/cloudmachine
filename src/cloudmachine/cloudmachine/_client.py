# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TypeVar, Generic, TYPE_CHECKING, Literal, ContextManager

from azure.core import PipelineClient
from azure.core.pipeline.transport import RequestsTransport
from azure.storage.blob import BlobServiceClient

if TYPE_CHECKING:
    from azure.storage.blob import BlobServiceClient

ClientType = TypeVar("ClientType", bound=ContextManager)

class CloudMachineStorage(Generic[ClientType]):
    kind: str
    client: ClientType

class CloudMachineBlobStorage(CloudMachineStorage[BlobServiceClient]):

    client: BlobServiceClient
    kind: Literal["blob"] = "blob"
    
    def __init__(self, endpoint, credential, *, transport=None):
        self._transport = transport or RequestsTransport()
        self._pipeline = PipelineClient(transport=self._transport)
        self._client

    @property
    def sdk(self) -> "BlobServiceClient":
        try:
            from azure.storage.blob import BlobServiceClient
            return BlobServiceClient()
        except ImportError:
            raise ImportError("To access the Blob Storage SDK, please install azure-storage-blob.")

    def close(self) -> None:
        self._pipeline.close()
        self._transport.close()

class CloudMachineDataStorage(CloudMachineStorage):

    pass