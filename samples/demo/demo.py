

from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.storage.queue import QueueServiceClient
from azure.keyvault.secrets import SecretClient
from azure.keyvault.keys import KeyClient

from azure.cloudmachine.resources import (
    BlobContainer,
    BlobStorage,
    TableStorage,
    EventSystemTopic,
    SystemTopicSubscription,
    QueueStorage,
    AIServices,
    ResourceGroup,
    UserAssignedIdentity,
    KeyVault
)
from azure.cloudmachine import (
    resource,
    provision,
    export,
    CloudMachine,
    MISSING,
    Resource
)



data = BlobContainer(container_name="mydata")
provision(data)
client = data(ContainerClient)
client.upload_blob("my_data.txt", b"DATA", overwrite=True)



class EventListener(CloudMachine):
    queue: QueueStorage = resource(default=MISSING, queues=[{'name': 'systemevents'}])
    events: SystemTopicSubscription = resource(filter=['Microsoft.Storage.BlobCreated'])


class MyApp(CloudMachine):
    keys: KeyClient = resource()
    data: ContainerClient = resource(container_name="foo")
    messages: QueueServiceClient = resource(EventListener.queue)


app_client = provision(MyApp)


print("Uploading blob...")
app_client.data.upload_blob("helloworld.txt", b"Hello World", overwrite=True)
queue = app_client.messages.get_queue_client("systemevents")
response = queue.receive_messages()
for message in response:
    print("Received blob upload event!")
    queue.delete_message(message)



# class TestInfra(CloudMachine):
#     data: BlobContainer = resource(container_name="images", metadata={"foo":"bar"})
#     users: TableStorage = resource(tables=[{'name': 'users'}])

# # Resource inferred from type hint
# class TestAppA(CloudMachine):
#     images_one: ContainerClient = resource(TestInfra.data)
#     images_two: ContainerClient = resource(TestInfra.data)
#     users: TableServiceClient = resource(TestInfra.users)

# # Explicit resource declaration
# class TestAppB(CloudMachine):
#     _blobs_three = resource("storage:blobs", "foo")
#     images_three = resource(TestInfra.data)
#     _blobs_four = resource("storage:blobs", "bar", role_assignments=[], enable_hierarchical_namespace=False)
#     images_four = resource(TestInfra.data)

# export(TestAppA, TestAppB)
# app_a, app_b = provision(TestAppA, TestAppB)
