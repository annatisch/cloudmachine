
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
    storage: BlobStorage = None
    data: BlobContainer = resource(container_name="images", metadata={"foo":"bar"})
    users: TableStorage = resource(tables=[{'name': 'users'}])


# Resource inferred from type hint
class TestAppA(CloudMachineClient):
    images_one: ContainerClient = resource(TestInfra.data)
    images_two: ContainerClient = resource(TestInfra.data)
    users: TableServiceClient = resource(TestInfra.users)

# Explicit resource declaration
class TestAppB(CloudMachineClient):
    _blobs_three = resource("storage:blobs", "foo")
    images_three = resource(TestInfra.data)
    _blobs_four = resource("storage:blobs", "bar", role_assignments=[], enable_hierarchical_namespace=False)
    images_four = resource(TestInfra.data)

export(TestAppA, TestAppB)

# This doesn't work yet because env vars aren't populated.
# app = provision(TestAppB)
