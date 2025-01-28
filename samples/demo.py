
from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobServiceClient, ContainerClient


from azure.cloudmachine.resources import (
    BlobContainer,
    BlobStorage,
    TableStorage
)
from azure.cloudmachine import (
    resource,
    provision,
    export,
    CloudMachineClient,
)


class TestInfra(CloudMachineClient):
    storage: BlobStorage
    data: BlobContainer = resource(container_name="images", metadata={"foo":"bar"})


# Resource inferred from type hint
class TestAppA(CloudMachineClient):
    _blobs_one: BlobStorage = resource("foo")
    images_one: ContainerClient = resource(TestInfra.data)
    _blobs_two: BlobStorage = resource("bar", role_assignments=[], enable_hierarchical_namespace=False)
    images_two: ContainerClient = resource(TestInfra.data)

export(TestAppA)

# Explicit resource declaration
class TestAppB(CloudMachineClient):
    _blobs_three = resource("storage:blobs", "foo")
    images_three = resource(TestInfra.data)
    _blobs_four = resource("storage:blobs", "bar", role_assignments=[], enable_hierarchical_namespace=False)
    images_four = resource(TestInfra.data)

export(TestAppB)

# This doesn't work yet because env vars aren't populated.
# app = provision(TestAppB)
