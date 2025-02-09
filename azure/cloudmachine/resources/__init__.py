from typing import Dict, Type, TYPE_CHECKING

from .resourcegroup._resource import ResourceGroup
from .managedidentity._resource import UserAssignedIdentity

from .ai._resource import AIServices
from .ai.deployment._resource import AIChatCompletions, AITextEmbeddings
from .ml._resource import AIHub, AIProject

from .storage import StorageAccount
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
