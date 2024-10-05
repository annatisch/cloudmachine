# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import json
import time
from typing import IO, Any, Dict, Generator, Iterable, List, Mapping, Optional, Tuple, TypeVar, Generic, TYPE_CHECKING, Literal, ContextManager
from threading import Thread
from concurrent.futures import Executor, ThreadPoolExecutor, Future

import requests
from dotenv import load_dotenv

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.pipeline.transport import HttpTransport, RequestsTransport
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.data.tables import TableServiceClient, TableClient
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient

from .resources import CloudMachineDeployment, StorageAccount, azd_env_name

from blinker import Namespace
cloudmachine_events = Namespace()

file_uploaded = cloudmachine_events.signal('file-uploaded')


def load_dev_environment(name: str):
    azd_dir = os.path.join(os.getcwd(), ".azure")
    if not os.path.isdir(azd_dir):
        raise RuntimeError("No '.azure' directory found in current working dir. Please run 'azd init' with the Minimal template.")

    env_name = azd_env_name(name, 'local', None)
    # try:
    #     azd_env_name = os.environ['AZURE_ENV_NAME']
    # except KeyError:
    #     with open(os.path.join(azd_dir, "config.json")) as azd_config:
    #         azd_env_name = json.load(azd_config)["defaultEnvironment"]

    env_loaded = load_dotenv(os.path.join(azd_dir, env_name, ".env"), override=True)
    if not env_loaded:
        raise RuntimeError(
            f"No cloudmachine infrastructure loaded loaded for env: '{env_name}'.\n"
            " Please run 'azd provision' to provision cloudmachine resources."
        )
    print(env_loaded)

class Process(Future):

    def __init__(self, future: Future) -> None:
        self._future = future

class Processer(Executor):

    def __init__(self, *, max_workers: int = 10) -> None:
        self._executor = ThreadPoolExecutor

    def submit(self, fn, /, *args, **kwargs) -> Process:
        future = self._executor.submit(fn, *args, **kwargs)
        return Process(future)

    def map(self, fn, *iterables, timeout: Optional[int] = None, chunksize: int = 1):
        self._executor.map(fn, *iterables, timeout=timeout, chunksize=chunksize)


class CloudMachineStorage:
    default_container_name: str = "default"
    
    def __init__(
            self,
            *,
            transport: Optional[HttpTransport] = None,
            name: Optional[str] = None,
            executor: Optional[Executor] = None,
            **kwargs
    ):
        if name:
            name = name.upper()
            endpoint = os.environ[f'AZURE_STORAGE_{name}_BLOB_ENDPOINT']
        else:
            endpoint = os.environ['AZURE_STORAGE_BLOB_ENDPOINT']
        if f'AZURE_STORAGE_{name}_KEY' in os.environ:
            account_name = os.environ[f'AZURE_STORAGE_{name}_NAME']
            credential = AzureNamedKeyCredential(account_name, os.environ[f'AZURE_STORAGE_{name}_KEY'])
        else:
            credential = DefaultAzureCredential()
        self._client = BlobServiceClient(
            account_url=endpoint,
            credential=credential,
            transport=transport,
            **kwargs
        )
        self._default_container = self._client.get_container_client(self.default_container_name)
        self._containers: Dict[str, ContainerClient] = {}

    def _get_container_client(self, container: Optional[str]) -> ContainerClient:
        if container:
            try:
                return self._containers[container]
            except KeyError:
                container_client = self._client.get_container_client(container)
                self._containers[container] = container_client
                return container_client
        return self._default_container

    def get_client(self) -> BlobServiceClient:
        return self._client

    def list(
            self,
            *,
            prefix: Optional[str] = None,
            container: Optional[str] = None
    ) -> Generator[str, None, None]:
        client = self._get_container_client(container)
        for blob in client.list_blobs(name_starts_with=prefix):
            yield blob.name

    def delete(self, name: str, *, container: Optional[str] = None) -> None:
        client = self._get_container_client(container)
        client.delete_blob(name)

    def upload(self, name: str, filedata: IO[bytes], *, container: Optional[str] = None) -> None:
        client = self._get_container_client(container)
        client.upload_blob(name, filedata, overwrite=True)

    def download(self, name: str, *, container: Optional[str] = None) -> Generator[bytes, None, None]:
        client = self._get_container_client(container)
        download = client.download_blob(name)
        for data in download.chunks():
            yield data
    
    def create_container(self, name: str) -> None:
        client = self._client.create_container(name)
        self._containers[name] = client

    def delete_container(self, name:str) -> None:
        if name.lower() == "default":
            raise ValueError("Default container cannot be deleted.")
        try:
            container = self._containers.pop(name)
            container.delete_container()
        except KeyError:
            self._client.delete_container(name)

    def close(self) -> None:
        self._client.close()


class EventListener:
    _listener_topic: str = "cm_internal_topic"
    _listen_subscription: str = "cm_internal_subscription"

    def __init__(self) -> None:
        endpoint = os.environ['AZURE_SERVICE_BUS_ENDPOINT']
        credential = DefaultAzureCredential()
        self._client = ServiceBusClient(
            fully_qualified_namespace=endpoint,
            credential=credential,
        )
        self._listener = self._client.get_subscription_receiver(
            topic_name=self._listener_topic,
            subscription_name=self._listen_subscription,
        )

    def __call__(self):
        try:
            with self._listener as receiver:
                for msg in receiver:
                    print(str(msg))
                    file_uploaded.send(msg)
        except Exception as exp:
            print(exp)

    def close(self):
        self._client.close()


class CloudMachineMessaging:
    default_queue_name: str = "default"

    def __init__(
            self,
            *,
            name: Optional[str] = None,
    ):
        if name:
            name = name.upper()
            endpoint = os.environ[f'AZURE_SERVICE_BUS_{name}_ENDPOINT']
        else:
            endpoint = os.environ['AZURE_SERVICE_BUS_ENDPOINT']
        if f'AZURE_SERVICE_BUS_{name}_KEY' in os.environ:
            account_name = os.environ[f'AZURE_SERVICE_BUS_{name}_NAME']
            credential = AzureNamedKeyCredential(account_name, os.environ[f'AZURE_SERVICE_BUS_{name}_KEY'])
        else:
            credential = DefaultAzureCredential()
        self._client = ServiceBusClient(
            fully_qualified_namespace=endpoint,
            credential=credential,
        )
        #self._default_queue_sender = self._client.get_queue_sender(self.default_queue_name)
        #self._default_queue_receiver = 
        #self._containers: Dict[str, ContainerClient] = {}

    def get_client(self) -> ServiceBusClient:
        return self._client

    def close(self) -> None:
        self._client.close()


class CloudMachineTableData:
    def __init__(
            self,
            *,
            transport: Optional[HttpTransport] = None,
            name: Optional[str] = None,
            **kwargs
    ):
        if name:
            name = name.upper()
            endpoint = os.environ[f'AZURE_STORAGE_{name}_TABLE_ENDPOINT']
        else:
            endpoint = os.environ['AZURE_STORAGE_TABLE_ENDPOINT']
        if f'AZURE_STORAGE_{name}_KEY' in os.environ:
            account_name = os.environ[f'AZURE_STORAGE_{name}_NAME']
            credential = AzureNamedKeyCredential(account_name, os.environ[f'AZURE_STORAGE_{name}_KEY'])
        else:
            credential = DefaultAzureCredential()
        self._client = TableServiceClient(
            account_url=endpoint,
            credential=credential,
            transport=transport,
            **kwargs
        )
        self._tables: Dict[str, TableClient] = {}

    def _get_table_client(self, tablename: str) -> TableClient:
        try:
            return self._tables[tablename]
        except KeyError:
            table_client = self._client.get_table_client(tablename)
            table_client.create_if_not_exists()
            self._tables[tablename] = table_client
            return table_client

    def get_client(self) -> TableServiceClient:
        return self._client

    def insert(self, table: str, *entities: Mapping[str, Any]) -> None:
        table_client = self._get_table_client(table)
        batch = [("create", e) for e in entities]
        table_client.submit_transaction(batch)

    def upsert(self, table: str, *entities: Mapping[str, Any], overwrite: bool = True) -> None:
        table_client = self._get_table_client(table)
        batch = [
            ("upsert", e, {'mode': 'replace' if overwrite else 'merge'}) for e in entities
        ]
        table_client.submit_transaction(batch)

    def update(self, table: str, *entities: Mapping[str, Any], overwrite: bool = True) -> None:
        table_client = self._get_table_client(table)
        batch = [
            ("update", e, {'mode': 'replace' if overwrite else 'merge'}) for e in entities
        ]
        table_client.submit_transaction(batch)

    def delete(self, table: str, *entities: Mapping[str, Any]) -> None:
        table_client = self._get_table_client(table)
        batch = [("delete", e) for e in entities]
        table_client.submit_transaction(batch)

    def list(self, table: str) -> Generator[Mapping[str, Any], None, None]:
        table_client = self._get_table_client(table)
        for entity in table_client.list_entities():
            yield entity

    def query(self, table: str, query: str) -> Generator[Mapping[str, Any], None, None]:
        table_client = self._get_table_client(table)
        for entity in table_client.query_entities(query):
            yield entity






class CloudMachineClient:
    name: str

    def __init__(
            self,
            *,
            name: str,
            http_transport: Optional[HttpTransport] = None,
            **kwargs
    ):
        self.name = name
        self._http_transport = http_transport or self._build_transport(**kwargs)
        self._listener = EventListener()
        self._listener_thread = Thread(target=self._listener, daemon=True)
        self._storage: Dict[CloudMachineStorage] = {}
        self._messaging: Dict[CloudMachineMessaging] = {}

    def _build_transport(self, **kwargs):
        session = requests.Session()
        session.mount(
            'https://',
            requests.adapters.HTTPAdapter(
                kwargs.pop('pool_connections', 10),
                kwargs.pop('pool_maxsize', 10)
            )
        )
        return RequestsTransport(
            session=session,
            session_owner=False,
            **kwargs
        )

    @property
    def storage(self):
        if not self._storage:
            self._listener_thread.start()
            self._storage['default'] = CloudMachineStorage()
        return self._storage['default']

    @property
    def messaging(self):
        if not self._messaging:
            self._messaging['default'] = CloudMachineMessaging()
        return self._messaging['default']

    def close(self):
        self._listener.close()
        for storage_client in self._storage.values():
            storage_client.close()
        for queue_client in self._messaging.values():
            queue_client.close()
        if self._listener_thread.is_alive():
            self._listener_thread.join()
        self._http_transport.close()

"""

136
public class MessagingServices { 
137
public MessagingServices(AzureFXClient machine); 
138
public const string DefaultQueue = "$default"; 
139
public event Func<MessagingError, Task> Error; 
140
public event Func<ReceivedMessage, Task> MessageReceived; 
141
public Task SendAsync(ContentData content, string subject = null, string queue = "$default"); 
142
public Task SendAsync<T>(T content, string subject = null, string queue = "$default"); 
143
public ValueTask StartReceivingAsync(string queue); """