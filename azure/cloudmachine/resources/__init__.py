from typing import Dict, Type, TYPE_CHECKING

from .resourcegroup._resource import ResourceGroup
from .managedidentity._resource import UserAssignedIdentity

from .ai._resource import AIServices
from .ai.deployment._resource import AIChatCompletions, AITextEmbeddings
from .ml._resource import AIHub, AIProject

from .storage._resource import StorageAccount
from .storage.blobs._resource import BlobStorage, DatalakeStorage
from .storage.blobs.container._resource import BlobContainer, FileSystem
from .storage.tables._resource import TableStorage
from .storage.queues._resource import QueueStorage
from .storage.files._resource import FileShareStorage
from .storage.files.share._resource import FileShare

from .eventgrid.systemtopic._resource import EventSystemTopic
from .eventgrid.systemtopic.subscription._resource import SystemTopicSubscription

from .keyvault._resource import KeyVault
from .search._resource import SearchService

if TYPE_CHECKING:
    from .._resource import Resource


# TODO: This doesn't account for naming conflicts - consider making this a function
RESOURCE_BY_ANNOTATION: Dict[str, Type['Resource']] = {
    'ResourceGroup': ResourceGroup,
    'UserAssignedIdentity': UserAssignedIdentity,
    'StorageAccount': StorageAccount,
    'BlobStorage': BlobStorage,
    'BlobServiceClient': BlobStorage,
    'DataLakeServiceClient': DatalakeStorage,
    'BlobContainer': BlobContainer,
    'ContainerClient': BlobContainer,
    'FileSystemClient': FileSystem,
    'TableStorage': TableStorage,
    'TableServiceClient': TableStorage,
    'FileShareStorage': FileShareStorage,
    'ShareServiceClient': FileShareStorage,
    'FileShare': FileShare,
    'ShareClient': FileShare,
    'QueueStorage': QueueStorage,
    'QueueServiceClient': QueueStorage,
    'EventSystemTopic': EventSystemTopic,
    'SystemTopicSubscription': SystemTopicSubscription,
    'KeyVault': KeyVault,
    'KeyClient': KeyVault,
    'SecretClient': KeyVault,
    'CertificateClient': KeyVault,
    'AIChatCompletions': AIChatCompletions,
    'ChatCompletionsClient': AIChatCompletions,
    'Chat': AIChatCompletions,
    'AsyncChat': AIChatCompletions,
    'AITextEmbeddings': AITextEmbeddings,
    'EmbeddingsClient': AITextEmbeddings,
    'Embeddings': AITextEmbeddings,
    'AsyncEmbeddings': AITextEmbeddings,
    'AIServices': AIServices,
    'AIHub': AIHub,
    'AIProject': AIProject,
    'AIProjectClient': AIProject,
    'SearchService': SearchService,
    'SearchIndexerClient': SearchService,
    'SearchIndexClient': SearchService
}

