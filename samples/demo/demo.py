

from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.storage.queue import QueueServiceClient
from azure.ai.inference import ChatCompletionsClient
from azure.keyvault.secrets import SecretClient
from azure.keyvault.keys import KeyClient

from azure.cloudmachine.resources.storage.blobs import BlobStorage
from azure.cloudmachine.resources.ai.deployment import AIChat
from azure.cloudmachine import (
    AzureInfrastructure,
    AzureApp,
    resource,
    provision,
)


# Simple scenario, using a single resource
data = BlobStorage.reference(account="foo", resource_group="bar")
client = data.get_client()  # Default client type for BlobStorage is azure.storage.blob.BlobServiceClient
client.list_containers()


# Simple scenario with multiple resources
class MyInfra(AzureInfrastructure):
    storage: BlobStorage = resource(default=BlobStorage.reference(account="foo", resource_group="bar"))
    chat: AIChat = resource(default=AIChat.reference(name='gpt-4o', account='shared'))

class MyApp(AzureApp):
    data: BlobServiceClient = client()
    ai: ChatCompletionsClient = client()


infra = MyInfra()
app = MyApp.from_infra(infra)
app.data.list_containers()

