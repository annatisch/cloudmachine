
from typing import Literal
from enum import Enum


class ResourceIdentifiers(str, Enum):
    resource_group: Literal['resourcegroup'] = 'resourcegroup'
    user_assigned_identity: Literal['userassignedidentity'] = 'userassignedidentity'
    role_assignment: Literal['roleassignment'] = 'roleassignment'
    storage_account: Literal['storage'] = 'storage'
    blob_storage: Literal['storage:blobs'] = 'storage:blobs'
    datalake_storage: Literal['storage:datalake'] = 'storage:datalake'
    blob_container: Literal['storage:blobs:container'] = 'storage:blobs:container'
    file_system: Literal['storage:datalake:filesystem'] = 'storage:datalake:filesystem'
    table_storage: Literal['storage:tables'] = 'storage:tables'
    table: Literal['storage:tables:table'] = 'storage:tables:table'
    queue_storage: Literal['storage:queues'] = 'storage:queues'
    queue: Literal['storage:queues:queue'] = 'storage:queues:queue'
    file_storage: Literal['storage:files'] = 'storage:files'
    file_share: Literal['storage:files:share'] = 'storage:files:share'
    system_topic: Literal['events:systemtopic'] = 'events:systemtopic'
    system_topic_subscription: Literal['events:systemtopic:subscription'] = 'events:systemtopic:subscription'
    keyvault: Literal['keyvault'] = 'keyvault'
    keyvault_key: Literal['keyvault:key'] = 'keyvault:key'
    keyvault_secret: Literal['keyvault:secret'] = 'keyvault:secret'
    search: Literal['search'] = 'search'
    cognitive_services: Literal['cognitive_services'] = 'cognitive_services'
    ai_services: Literal['ai'] = 'ai'
    ai_project: Literal['ai:project'] = 'ai:project'
    ai_hub: Literal['ai:hub'] = 'ai:hub'
    ai_deployment: Literal['ai:deployment'] = 'ai:deployment'
    ai_chat_deployment: Literal['ai:deployment:chat'] = 'ai:deployment:chat'
    ai_embeddings_deployment: Literal['ai:deployment:embeddings'] = 'ai:deployment:embeddings'
