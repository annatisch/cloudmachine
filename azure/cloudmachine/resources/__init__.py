from typing import Dict, Type, TYPE_CHECKING

from .resourcegroup._resource import ResourceGroup
from .managedidentity._resource import UserAssignedIdentity

from .storage._resource import StorageAccount
from .storage.blobs._resource import BlobStorage
from .storage.blobs.container._resource import BlobContainer
from .storage.tables._resource import TableStorage
from .storage.queues._resource import QueueStorage
from .storage.files._resource import FileShareStorage
from .storage.files.share._resource import FileShare

if TYPE_CHECKING:
    from .._resource import Resource


# TODO: This doesn't account for naming conflicts - consider making this a function
INFERRED_RESOURCE: Dict[str, Type['Resource']] = {
    'ResourceGroup': ResourceGroup,
    'UserAssignedIdentity': UserAssignedIdentity,
    'StorageAccount': StorageAccount,
    'BlobStorage': BlobStorage,
    'BlobServiceClient': BlobStorage,
    'BlobContainer': BlobContainer,
    'ContainerClient': BlobContainer,
    'TableStorage': TableStorage,
    'TableServiceClient': TableStorage,
    'ShareServiceClient': FileShareStorage,
    'ShareClient': FileShare,
    'QueueServiceClient': QueueStorage,
}
__all__ = [
    'ResourceGroup',
    'UserAssignedIdentity',
    'StorageAccount',
    'BlobStorage',
    'BlobContainer',
    'TableStorage',
    'QueueStorage',
    'FileShareStorage',
    'FileShare',
]
