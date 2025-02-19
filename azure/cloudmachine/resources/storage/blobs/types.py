from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required

from ...._bicep.expressions import Parameter

# TODO: Finish populating these properties and update API version
RESOURCE = "Microsoft.Storage/storageAccounts/blobServices"
VERSION = "2022-09-01"


class BlobServiceProperties(TypedDict, total=False):
    automaticSnapshotPolicyEnabled: Union[bool, Parameter[bool]]
    """Automatic Snapshot is enabled if set to true. Deprecated in favor of isVersioningEnabled property."""
    changeFeed: Union['ChangeFeed', Parameter['ChangeFeed']]
    """The blob service properties for change feed events."""
    containerDeleteRetentionPolicy: Union['DeleteRetentionPolicy', Parameter['DeleteRetentionPolicy']]
    """The blob service properties for container soft delete."""
    cors: Union['CorsRules', Parameter['CorsRules']]
    """Specifies CORS rules for the Blob service. You can include up to five CorsRule elements in the request. If no CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled for the Blob service."""
    defaultServiceVersion: Union[str, Parameter[str]]
    """DefaultServiceVersion indicates the default version to use for requests to the Blob service if an incoming request’s version is not specified. Possible values include version 2008-10-27 and all more recent versions."""
    deleteRetentionPolicy: Union['DeleteRetentionPolicy', Parameter['DeleteRetentionPolicy']]
    """The blob service properties for blob soft delete."""
    isVersioningEnabled: Union[bool, Parameter[bool]]
    """Use versioning to automatically maintain previous versions of your blobs."""
    lastAccessTimeTrackingPolicy: Union['LastAccessTimeTrackingPolicy', Parameter['LastAccessTimeTrackingPolicy']]
    """The blob service property to configure last access time based tracking policy."""
    restorePolicy: Union['RestorePolicyProperties', Parameter['RestorePolicyProperties']]
    """The blob service properties for blob restore policy."""


class BlobServiceResource(TypedDict, total=False):
    name: Union[Literal['default'], Parameter[str]]
    """The resource name."""
    properties: Union[BlobServiceProperties, Parameter[BlobServiceProperties]]
    """The properties of a storage account's Blob service."""
