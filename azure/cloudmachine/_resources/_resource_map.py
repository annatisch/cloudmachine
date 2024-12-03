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

from typing import Dict, Optional, Tuple, Union, Type, List, Any, TYPE_CHECKING
from azure.core.utils import case_insensitive_dict
from azure.core import AzureClouds


RESOURCE_SDK_MAP: Dict[str, Tuple[List[str], Optional[str]]] = case_insensitive_dict({
    'storage': (['storage'], None),
    'storage:blob': (['storage', 'blob'], 'azure.storage.blob.BlobServiceClient'),
    'storage:blob:container': (['storage', 'blob', 'container'], 'azure.storage.blob.ContainerClient'),
    'storage:table': (['storage', 'table'], 'azure.data.tables.TableServiceClient'),
    'keyvault': (['keyvault'], None),
    'keyvault:secrets': (['secrets'], 'azure.keyvault.secrets.SecretClient'),
    'keyvault:keys': (['keys'], 'azure.keyvault.secrets.KeyClient'),
    'servicebus': (['service_bus', 'servicebus'], 'azure.servicebus.ServiceBusClient'),
    'openai': (['openai', 'open_ai'], 'openai.AzureOpenAI'),
    'search': (['search'], 'azure.search.documents.indexes.SearchIndexClient'),
    'search:index': (['search', 'search_index'], 'azure.search.documents.SearchClient'),
    'documentai': (['document_intelligence', 'form_recognizer'], 'azure.ai.document_intelligence.DocumentIntelligenceClient'),
})


AUDIENCES: Dict[str, Dict[AzureClouds, str]] = case_insensitive_dict({
    'storage': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'storage:blob': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'storage:blob:container': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'storage:table': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'servicebus': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://servicebus.azure.net/.default",
    },
    'openai': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://cognitiveservices.azure.com/.default",
    },
    'search': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://search.azure.com/.default",
    },
    'search:index': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://search.azure.com/.default",
    },
    'documentai': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://cognitiveservices.azure.com/.default",
    }
})

RESOURCE_IDS: Dict[str, str] = case_insensitive_dict({
    'storage': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{name}',
    'storage:blob': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{name}',
    'storage:table': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{name}',
    'servicebus': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.ServiceBus/namespaces/{name}',
    'openai': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CognitiveServices/accounts/{name}',
    'search': '"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Search/searchServices/{name}',
    'documentai': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CognitiveServices/accounts/{name}'
})

DEFAULT_API_VERSIONS = {
    "storage:table": "2019-02-02",
    "storage:blob": "2020-12-06", # "2025-01-05"
    "storage": "2020-12-06",
    "servicebus": "2021-05",
    "openai": "2023-05-15"
}

