# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------

from typing import Any, Protocol, TYPE_CHECKING, Mapping, TypeVar, NewType, Optional, runtime_checkable

from azure.core.pipeline.transport import HttpTransport


@runtime_checkable
class SyncClient(Protocol):

    # This is difficult because most client types don't have transport and api_version
    # as explicit keyword-only params.
    # def __init__(
    #         self,
    #         endpoint: str,
    #         *args: Any,
    #         credential: Any,
    #         transport: Optional[HttpTransport] = None,
    #         api_version: Optional[str] = None,
    #         audience: Optional[str] = None,
    #         **kwargs
    # ) -> None:
    #     ...
    def close(self) -> None:
        ...

@runtime_checkable
class WithSettings(Protocol):
    __resource_settings__ = Mapping[str, Any]

@runtime_checkable
class SyncClientWithSettings(SyncClient, WithSettings):
    ...


ClientType = TypeVar("ClientType", bound=SyncClient)
ClientTypeWithSettings = NewType("ClientTypeWithSettings", (ClientType, WithSettings))



if TYPE_CHECKING:
    try:
        from azure.storage.blob import BlobServiceClient, ContainerClient
        class BlobServiceClientWithSettings(BlobServiceClient, WithSettings):
            pass
        class ContainerClientWithSettings(ContainerClient, WithSettings):
            pass
    except ImportError:
        BlobServiceClient = Any
        ContainerClient = Any
        BlobServiceClientWithSettings = Any
        ContainerClientWithSettings = Any

    try:
        from azure.data.tables import TableServiceClient
        class TableServiceClientWithSettings(TableServiceClient, WithSettings):
            pass
    except ImportError:
        TableServiceClient = Any
        TableServiceClientWithSettings = Any

    try:
        from azure.servicebus import ServiceBusClient
        class ServiceBusClientWithSettings(ServiceBusClient, WithSettings):
            pass
    except ImportError:
        ServiceBusClient = Any
        ServiceBusClientWithSettings = Any

    try:
        from azure.keyvault.keys import KeyClient
        class KeyClientWithSettings(KeyClient, WithSettings):
            pass
    except ImportError:
        KeyClient = Any
        KeyClientWithSettings = Any

    try:
        from azure.keyvault.secrets import SecretClient
        class SecretClientWithSettings(SecretClient, WithSettings):
            pass
    except ImportError:
        SecretClient = Any
        SecretClientWithSettings = Any

    try:
        from openai import AzureOpenAI
        from openai.resources import Embeddings, Chat
        class AzureOpenAIWithSettings(AzureOpenAI, WithSettings):
            pass
        class EmbeddingsWithSettings(Embeddings, WithSettings):
            pass
        class ChatWithSettings(Chat, WithSettings):
            pass
    except ImportError:
        AzureOpenAI = Any
        Embeddings = Any
        Chat = Any
        AzureOpenAIWithSettings = Any
        EmbeddingsWithSettings = Any
        ChatWithSettings = Any

    try:
        from azure.search.documents import SearchClient
        from azure.search.documents.indexes import SearchIndexClient
        class SearchClientWithSettings(SearchClient, WithSettings):
            pass
        class SearchIndexClientWithSettings(SearchIndexClient, WithSettings):
            pass
    except ImportError:
        SearchClient = Any
        SearchClientWithSettings = Any
        SearchIndexClient = Any
        SearchIndexClientWithSettings = Any

    try:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        class DocumentIntelligenceClientWithSettings(DocumentIntelligenceClient, WithSettings):
            pass
    except ImportError:
        DocumentIntelligenceClient = Any
        DocumentIntelligenceClientWithSettings = Any