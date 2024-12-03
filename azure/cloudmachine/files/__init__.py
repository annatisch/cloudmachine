# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from abc import ABC, abstractmethod
import functools
from io import BytesIO
import json
from datetime import datetime, timedelta, timezone
from time import time
import uuid
from wsgiref.handlers import format_date_time
from urllib.parse import urlparse, quote, urljoin
from typing import IO, Any, Dict, Generator, Generic, Iterable, List, Mapping, Optional, Tuple, Type, TypeVar, Union, overload, Literal
from threading import Thread
from concurrent.futures import Executor, Future
import xml.etree.ElementTree as ET

from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, SupportsTokenInfo
from azure.core.pipeline.transport import HttpTransport
from azure.core.rest import HttpRequest, HttpResponse
from azure.core import PipelineClient, MatchConditions
from azure.core.utils import case_insensitive_dict
from azure.core.pipeline.policies import HeadersPolicy

from ..events import cloudmachine_events
from .._httpclient._base import CloudMachineClientlet
from .._httpclient._utils import (
    Pages,
    Stream,
    PartialStream,
    serialize_rfc,
    deserialize_rfc,
    prep_if_match,
    prep_if_none_match,
    parse_content_range,
    get_length,
    serialize_tags_header,
    deserialize_metadata_header
)

_ERROR_CODE = "x-ms-error-code"
_DEFAULT_CHUNK_SIZE = 32 * 1024 * 1024
_DEFAULT_BLOCK_SIZE = 256 * 1024 * 1024
SasPermissions = Literal['read', 'write', 'delete', 'tag', 'create', 'execute']


def _format_url(endpoint: str, container: str) -> str:
    parsed_url = urlparse(endpoint)
    return f"{parsed_url.scheme}://{parsed_url.hostname}/{quote(container)}{parsed_url.query}"


def _build_dict(element: ET) -> Union[str, Dict[str, Any]]:
    if element.text:
        return element.text
    children = [(e.tag, _build_dict(e)) for e in element]
    as_dict = dict(children)
    if len(as_dict) != len(children):
        return children
    return as_dict or None


class FileBatchError(HttpResponseError):
    succeeded: List[Union[str, 'StoredFile']]
    failed: List[Tuple[Union[str, 'StoredFile'], HttpResponseError]]

    def __init__(
            self,
            *args,
            succeeded: List[Union[str, 'StoredFile']],
            failed: List[Tuple[Union[str, 'StoredFile'], HttpResponseError]],
            response: HttpResponse,
            **kwargs):
        self.succeeded = succeeded
        self.failed = failed
        super().__init__(*args, response=response, **kwargs)


class DeletedFile:
    __responsedata__: Dict[str, Any]
    filename: str
    endpoint: str

    def __init__(
            self,
            *,
            filename: str,
            endpoint: str,
            responsedata: Dict[str, Any]
    ) -> None:
        self.filename = filename
        self.endpoint = endpoint
        self.__responsedata__ = responsedata

    def __repr__(self) -> str:
        return f"DeletedFile(filename={self.filename})"

    def __str__(self) -> str:
        return f"{self.filename}"


T = TypeVar("T")

class StoredFile(Generic[T]):
    __responsedata__: Dict[str, Any]
    metadata: Dict[str, str]
    tags: Dict[str, str]
    etag: str
    content: T
    filename: str
    endpoint: str
    content_length: int
    content_type: Optional[str]
    content_encoding: Optional[str]
    content_language: Optional[str]
    content_disposition: Optional[str]
    cache_control: Optional[str]

    def __init__(
            self,
            *,
            filename: str,
            content: T,
            content_length: Union[int, str],
            etag: str,
            endpoint: str,
            **kwargs
    ) -> None:
        self.content = content
        self.content_length = int(content_length)
        self.etag = etag
        self.filename = filename
        self.endpoint = endpoint
        self.metadata = kwargs.get('metadata') or {}
        self.tags = kwargs.get('tags') or {}
        self.content_type = kwargs.get('content_type')
        self.content_encoding = kwargs.get('content_type')
        self.content_language = kwargs.get('content_type')
        self.content_disposition = kwargs.get('content_type')
        self.cache_control = kwargs.get('content_type')
        self.__responsedata__ = kwargs.get('responsedata', {})

    def __repr__(self) -> str:
        return f"StoredFile(filename={self.filename}, content_length={self.content_length}, content_type={self.content_type})"

    def __str__(self) -> str:
        return f"{self.filename}"


class CloudMachineStorage(CloudMachineClientlet):
    _id: Literal['Blob'] = 'storage:blob'
    default_container_name: str
    
    def __init__(
            self,
            endpoint: str,
            account_name: str,
            credential: Union[AzureNamedKeyCredential, AzureSasCredential, SupportsTokenInfo],
            *,
            container_name: str,
            transport: Optional[HttpTransport] = None,
            api_version: Optional[str] = None,
            executor: Optional[Executor] = None,
            config: Optional[CloudMachinePipelineConfig] = None,
            resource_id: Optional[str] = None,
            scope: str,
            **kwargs
    ):
        headers_policy = StorageHeadersPolicy(**kwargs)
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            transport=transport,
            api_version=api_version,
            config=config,
            scope=scope,
            executor=executor,
            headers_policy=headers_policy,
            resource_id=resource_id,
            **kwargs
        )
        self.default_container_name = container_name
        self._account_name = account_name
        self._containers: Dict[str, PipelineClient] = {}
        self._user_delegation_key: Optional[str] = None

    def _get_container_client(self, container: Optional[str]) -> PipelineClient:
        container = container or self.default_container_name
        try:
            return self._containers[container]
        except KeyError:
            container_endpoint = _format_url(self._endpoint, container)
            container_client = PipelineClient(
                base_url=container_endpoint,
                pipeline=self._config.pipeline
            )
            container_client.endpoint = container_endpoint
            self._containers[container] = container_client
            return container_client

    def _batch_send(self, *reqs: HttpRequest, **kwargs) -> None:
        policies = [StorageHeadersPolicy(), self._config.authentication_policy]
        request = HttpRequest(
            method="POST",
            url=self._endpoint,
            params={'comp': 'batch'},
            headers={"x-ms-version": self._config.api_version},
        )
        request.set_multipart_mixed(
            *reqs,
            policies=policies,
            enforce_https=False,
            boundary=f"batch_{uuid.uuid4()}",
        )
        response = self._client.send_request(request, stream=True, **kwargs)
        if response.status_code not in [202]:
            raise HttpResponseError(response=response)
        return response

    @overload
    def get_url(
            self,
            *,
            file: StorageFile,
            permissions: Union[str, List[SasPermissions]] = 'r',
            expiry: Union[datetime, timedelta, Literal['never']] = 'never',
            start: Union[datetime, timedelta, Literal['now']] = 'now',
    ) -> str:
        ...
    @overload
    def get_url(
            self,
            *,
            file: Optional[str] = None,
            container: Optional[str] = None,
            permissions: Union[str, List[Union[SasPermissions, Literal['list', 'filter']]]] = 'r',
            expiry: Union[datetime, timedelta, Literal['never']] = 'never',
            start: Union[datetime, timedelta, Literal['now']] = 'now',
    ) -> str:
        ...
    def get_url(
            self,
            *,
            file: Optional[Union[str, StorageFile]] = None,
            container: Optional[str] = None,
            permissions: Union[str, List[SasPermissions]] = 'r',
            expiry: Union[datetime, timedelta, int] = 60,
            start: Union[datetime, timedelta, Literal['now']] = 'now',
    ) -> str:
        from azure.storage.blob import generate_blob_sas, generate_container_sas, BlobServiceClient
        kwargs = {}
        if isinstance(start, timedelta):
            kwargs['start'] = datetime.now(timezone.utc) + start
        elif start != 'now':
            kwargs['start'] = start
        if isinstance(expiry, int):
            expiry = timedelta(minutes=expiry)
        if isinstance(expiry, timedelta):
            kwargs['expiry'] = datetime.now(timezone.utc) + expiry
        else:
            kwargs['expiry'] = expiry
        kwargs['permission'] = permissions if isinstance(permissions, str) else "".join(p[0] for p in permissions)
        if isinstance(self._credential, AzureNamedKeyCredential):
            named_key = self._credential.named_key
            kwargs['account_name'] = self._account_name
            kwargs['account_key'] = named_key.key
        elif isinstance(self._credential, SupportsTokenInfo):
            kwargs['account_name'] = self._account_name
            # if not self._user_delegation_key or self._user_delegation_key.signed_expiry < kwargs['expiry']:
            service_client = BlobServiceClient(self._endpoint, self._credential)
            self._user_delegation_key = service_client.get_user_delegation_key(
                key_start_time=datetime.now(timezone.utc),
                key_expiry_time=kwargs['expiry']
            )
            kwargs['user_delegation_key'] = self._user_delegation_key
        else:
            raise NotImplementedError('AzureSasCredential does not support SAS URL generation.')
        kwargs['container_name'] = file.container if isinstance(file, StorageFile) else container or self.default_container_name
        if file:
            kwargs['blob_name'] = file.filename if isinstance(file, StorageFile) else file
            sas_token = generate_blob_sas(**kwargs)
            endpoint = urljoin(self._endpoint, f"{kwargs['container_name']}/{kwargs['blob_name']}")
            return f"{endpoint}?{sas_token}"
        else:
            sas_token = generate_container_sas(**kwargs)
            return f"{urljoin(self._endpoint, kwargs['container_name'])}?{sas_token}"

    def list(
            self,
            *,
            prefix: Optional[str] = None,
            container: Optional[str] = None,
            include_metadata: bool = False,
            include_tags: bool = False,
            minimal: bool = False,
            continue_from: Optional[str] = None,
            pages: Optional[int] = None,
            pagesize: int = 100,
            **kwargs
    ) -> Generator[StorageFile[None], None, Optional[str]]:
        client = self._get_container_client(container)
        include = []
        if include_metadata:
            include.append('metadata')
        if include_tags:
            include.append('tags')
        kwargs['delimiter'] = kwargs.pop('delimiter', None)
        kwargs['showonly'] = kwargs.pop('showonly', 'files')
        kwargs['maxresults'] = pagesize
        kwargs['prefix'] = prefix
        kwargs['include'] = include
        kwargs['version'] = self._config.api_version

        def _request_one_page(marker: Optional[str]) -> Generator[StorageFile[None], None, Optional[str]]:
            request_params = dict(kwargs)
            request = build_list_blob_page_request(
                url=client.endpoint,
                marker=marker,
                kwargs=request_params,
            )
            response = client.send_request(request, **request_params)
            if response.status_code == 404 and response.headers.get(_ERROR_CODE) == 'ContainerNotFound':
                return None
            if response.status_code != 200:
                raise HttpResponseError(response=response)
            page = ET.fromstring(response.read().decode('utf-8'))
            for xmlblob in page.find('Blobs'):
                if xmlblob.tag == 'Blob':
                    if minimal:
                        properties = xmlblob.find('Properties')
                        filename = xmlblob[0].text
                        yield StorageFile(
                            filename=filename,
                            container=container or self.default_container_name,
                            content=None,
                            content_length=properties.find('Content-Length').text,
                            etag=properties.find('Etag').text,
                            endpoint=urljoin(client.endpoint, quote(filename))
                        )
                    else:
                        blob = _build_dict(xmlblob)
                        properties = blob['Properties']
                        filename = blob['Name']
                        tags = None
                        if include_tags:
                            tags = {t['Key']: t['Value'] for t in blob.get('Tags', {}).get('TagSet', [])}
                        yield StorageFile(
                            filename=filename,
                            content=None,
                            container=container or self.default_container_name,
                            content_length=properties['Content-Length'],
                            etag=properties['Etag'],
                            metadata=blob.get('Metadata', {}),
                            tags=tags,
                            endpoint=urljoin(client.endpoint, quote(filename)),
                            content_type = properties['Content-Type'],
                            content_encoding = properties['Content-Encoding'],
                            content_language = properties['Content-Language'],
                            content_disposition = properties['Content-Disposition'],
                            cache_control = properties['Cache-Control'],
                            responsedata=blob,
                        )
            next_page = page.find('NextMarker')
            return next_page.text if next_page is not None else None
            
        return Pages(
            _request_one_page,
            n_pages=pages,
            continuation=continue_from,
        )
            
    # TODO: Scope batch delete to specific container to prevent accidental delete outside of scope.
    def _delete(self, *files: Union[str, StorageFile], container: Optional[str] = None, **kwargs) -> None:
        if not files:
            return
        condition = kwargs.pop('condition', MatchConditions.Unconditionally)
        requests = []
        etag = kwargs.pop('etag', None)
        for file in files:
            try:
                etag = file.etag
                filename = file.filename
                file_container = file.container
            except AttributeError:
                filename = file
                file_container = container or self.default_container_name

            kwargs['if_match'] = prep_if_match(etag, condition)
            kwargs['if_none_match'] = prep_if_none_match(etag, condition)
            requests.append(
                build_delete_blob_request(
                    f"/{quote(file_container)}",
                    filename,
                    kwargs
                )
            )
        response = self._batch_send(*requests)
        succeeded = []
        failed = []
        for file, part_response in zip(files, response.parts()):
            if ((part_response.status_code == 202) or
                (part_response.status_code == 404 and part_response.headers.get(_ERROR_CODE) == 'BlobNotFound') or
                (part_response.status_code == 404 and part_response.headers.get(_ERROR_CODE) == 'ContainerNotFound') or
                (part_response.status_code == 409 and part_response.headers.get(_ERROR_CODE) == 'ContainerBeingDeleted')):
                succeeded.append(file)
            else:
                failed.append((file, HttpResponseError(response=response)))
        if failed:
            raise StorageBatchError(response=response, succeeded=succeeded, failed=failed)

    @overload
    def delete(
            self,
            *files: Union[str, StorageFile],
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.Unconditionally,
            etag: Optional[str] = None,
            wait: Literal[True] = True,
            **kwargs
    ) -> None:
        ...
    @overload
    def delete(
            self,
            *files: Union[str, StorageFile],
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.Unconditionally,
            etag: Optional[str] = None,
            wait: Literal[False],
            **kwargs
    ) -> Future[None]:
        ...
    def delete(
            self,
            *files: Union[StorageFile, str],
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.Unconditionally,
            etag: Optional[str] = None,
            wait: bool = True,
            **kwargs) -> None:
        if wait:
            return self._delete(
                *files,
                container=container,
                condition=condition,
                etag=etag,
                **kwargs
            )
        return self._executor.submit(
                self._delete,
                *files,
                container=container,
                condition=condition,
                etag=etag,
                **kwargs
            )

    def _upload(
            self,
            data: IO[bytes],
            *,
            content_length: Optional[int] = None,
            filename: Optional[str] = None,
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.IfMissing,
            metadata: Optional[Dict[str, str]],
            etag: Optional[str] = None,
            tags: Optional[Dict[str, str]] = None,
            content_type: Optional[str] = None,
            content_encoding: Optional[str] = None,
            content_language: Optional[str] = None,
            content_disposition: Optional[str] = None,
            cache_control: Optional[str] = None,
            **kwargs
    ) -> StorageFile[None]:
        # TODO: support upload by block list + commit
        # TODO: support content validation
        client = self._get_container_client(container)
        filename = filename or data.filename if hasattr(data, 'filename') else str(uuid.uuid4())
        content_length=content_length or get_length(data)
        kwargs['version'] = self._config.api_version
        kwargs['if_match'] = prep_if_match(etag, condition)
        kwargs['if_none_match'] = prep_if_none_match(etag, condition)
        kwargs['blob_content_type'] = content_type
        kwargs['blob_content_encoding'] = content_encoding
        kwargs['blob_content_language'] = content_language
        kwargs['blob_content_disposition'] = content_disposition
        kwargs['blob_cache_control'] = cache_control
        kwargs['blob_tags_string'] = serialize_tags_header(tags)
        expiry = kwargs.pop('expiry', None)
        if isinstance(expiry, timedelta):
            kwargs['expiry_relative'] = int(expiry.microseconds/1000)
        elif expiry:
            kwargs['expiry_absolute'] = expiry
        content = data if hasattr(data, 'read') else BytesIO(data)
        initial_index = content.tell()
        request = build_upload_blob_request(
            client.endpoint + f"/{quote(filename)}",
            content_length=content_length,
            content=content,
            kwargs=kwargs
        )
        response = client.send_request(request, **kwargs)
        if response.status_code == 404 and response.headers.get(_ERROR_CODE) == 'ContainerNotFound':
            # TODO: if this is an authenticated session - set acl
            self._create_container(container, **kwargs)
            content.seek(initial_index)  # TODO: need to test this...
            response = client.send_request(request, **kwargs)
        if response.status_code not in [201]:
            raise HttpResponseError(response=response)
        return StorageFile(
            filename = filename,
            container = container or self.default_container_name,
            content_length = content_length,
            last_modified = response.headers['Last-Modified'],
            etag = response.headers['ETag'],
            responsedata = response.headers,
            content_type = content_type,
            content_encoding = content_encoding,
            content_language = content_language,
            content_disposition = content_disposition,
            cache_control = cache_control,
            metadata=metadata,
            endpoint=urljoin(client.endpoint, quote(filename)),
            tags=tags,
            content=None,
        )
    @overload
    def upload(
            self,
            data: Union[bytes, IO[bytes]],
            *,
            content_length: Optional[int] = None,
            content_type: Optional[str] = None,
            content_encoding: Optional[str] = None,
            content_language: Optional[str] = None,
            content_disposition: Optional[str] = None,
            filename: Optional[str] = None,
            container: Optional[str] = None,
            overwrite: bool = False,
            condition: MatchConditions = MatchConditions.IfMissing,
            etag: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None,
            tags: Optional[Dict[str, str]] = None,
            expiry: Optional[Union[datetime, timedelta]] = None,
            wait: Literal[True] = True,
            **kwargs
    ) -> StorageFile[None]:
        ...
    @overload
    def upload(
            self,
            data: Union[bytes, IO[bytes]],
            *,
            content_length: Optional[int] = None,
            content_type: Optional[str] = None,
            content_encoding: Optional[str] = None,
            content_language: Optional[str] = None,
            content_disposition: Optional[str] = None,
            filename: Optional[str] = None,
            container: Optional[str] = None,
            overwrite: bool = False,
            condition: MatchConditions = MatchConditions.IfMissing,
            etag: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None,
            tags: Optional[Dict[str, str]] = None,
            expiry: Optional[Union[datetime, timedelta]] = None,
            wait: Literal[False],
            **kwargs
    ) -> Future[StorageFile[None]]:
        ...
    def upload(
            self,
            data: Union[bytes, IO[bytes]],
            *,
            content_length: Optional[int] = None,
            filename: Optional[str] = None,
            container: Optional[str] = None,
            overwrite: bool = False,
            condition: MatchConditions = MatchConditions.IfMissing,
            etag: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None,
            tags: Optional[Dict[str, str]] = None,
            wait: bool = True,
            **kwargs
    ) -> Union[Future[StorageFile[None]], StorageFile[None]]:
        if overwrite:
            condition = MatchConditions.Unconditionally
        if wait:
            return self._upload(
                data,
                content_length=content_length,
                filename=filename,
                container=container,
                condition=condition,
                metadata=metadata,
                tags=tags,
                etag=etag,
                **kwargs
            )
        return self._executor.submit(
            self._upload,
            data,
            content_length=content_length,
            filename=filename,
            container=container,
            condition=condition,
            metadata=metadata,
            tags=tags,
            etag=etag,
            **kwargs
        )
        
    def _download(
            self,
            filename: str,
            *,
            content_range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            **kwargs
    ) -> StorageFile[IO[bytes]]:
        client = self._get_container_client(container)
        chunk_size = kwargs.pop('chunk_size', None)
        if chunk_size and validate and chunk_size > 4 * 1024 * 1024:
            raise ValueError("Validation only possible with max chunk size of 4mb.")
        elif not chunk_size:
            chunk_size = _DEFAULT_CHUNK_SIZE if not validate else 4 * 1024 * 1024

        def _download(request: HttpRequest, **kwargs) -> Tuple[HttpResponse, int, int, int]:
            response = client.send_request(request, stream=True, **kwargs)
            if response.status_code not in [200, 206]:
                raise HttpResponseError(response=response)
            response_start, response_end, filelength = parse_content_range(
                response.headers['Content-Range']
            )
            return response, response_start, response_end, filelength

        kwargs['version'] = self._config.api_version
        kwargs['if_match'] = prep_if_match(etag, condition)
        kwargs['if_none_match'] = prep_if_none_match(etag, condition)
        if validate:
            kwargs['range_get_content_crc64'] = True

        request_builder = functools.partial(
            build_download_blob_request,
            client.endpoint,
            filename,
            kwargs
        )
        request_start = 0 if content_range is None else content_range[0]
        request_end = chunk_size if content_range is None or content_range[1] is None or content_range[1] > chunk_size else content_range[1]
        range_header = f'bytes={request_start}-{request_end}'
        request = request_builder(range_header)
        response, response_start, response_end, filelength = _download(request, **kwargs)
        first_chunk = PartialStream(
            start=response_start,
            end=response_end,
            response=response
        )
        downloaded = response_end - response_start
        if content_range:
            if content_range[1]:
                expected_length = content_range[1] - content_range[0]
            else:
                expected_length = filelength - content_range[0]
        else:
            expected_length = filelength
        if downloaded < expected_length:
            download_end = filelength if content_range is None or content_range[1] is None else content_range[1]
            chunk_iter = range(response_end + 1, download_end, chunk_size)
            request_gen = (request_builder(f'bytes={r}-{r + chunk_size}') for r in chunk_iter)
            response_gen = (_download(r, **kwargs) for r in request_gen)
            stream = Stream(
                content_length=expected_length,
                content_range=f'bytes {request_start}-{download_end}/{filelength}',
                first_chunk=first_chunk,
                next_chunks=response_gen
            )
        else:
            stream = Stream(
                content_length=downloaded,
                content_range=f'bytes {response_start}-{response_end}/{filelength}',
                first_chunk=first_chunk
            )
        return StorageFile(
            filename=filename,
            container=container or self.default_container_name,
            content_length=filelength,
            last_modified = response.headers['Last-Modified'],
            etag = response.headers['ETag'],
            content_type = response.headers['Content-Type'],
            content_encoding = response.headers.get('Content-Encoding'),
            content_language = response.headers.get('Content-Language'),
            content_disposition = response.headers.get('Content-Disposition'),
            cache_control = response.headers.get('Cache-Control'),
            metadata = deserialize_metadata_header(response.headers),
            responsedata=response.headers,
            content=stream,
            endpoint=urljoin(client.endpoint, quote(filename))
        )
    @overload
    def download(
            self,
            filename: str,
            *,
            range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            chunk_size: int = _DEFAULT_CHUNK_SIZE,
            wait: Literal[True] = True,
            **kwargs
    ) -> StorageFile[IO[bytes]]:
        ...
    @overload
    def download(
            self,
            filename: str,
            *,
            range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            chunk_size: int = _DEFAULT_CHUNK_SIZE,
            wait: Literal[False],
            **kwargs
    ) -> Future[StorageFile[IO[bytes]]]:
        ...
    def download(
            self,
            filename: str,
            *,
            range: Optional[Tuple[int, Optional[int]]] = None,
            container: Optional[str] = None,
            condition: MatchConditions = MatchConditions.IfPresent,
            etag: Optional[str] = None,
            validate: bool = False,
            wait: bool = True,
            **kwargs
    ) -> Union[StorageFile[IO[bytes]], Future[StorageFile[IO[bytes]]]]:
        # Remove page number from path, filename-1.txt -> filename.txt
        # This shouldn't typically be necessary as browsers don't send hash fragments to servers
        if filename.find("#page=") > 0:
            path_parts = filename.rsplit("#page=", 1)
            filename = path_parts[0]
        if wait:
            return self._download(
                filename=filename,
                content_range=range,
                container=container,
                condition=condition,
                etag=etag,
                validate=validate,
                **kwargs
            )
        return self._executor.submit(
            self._download,
            filename=filename,
            content_range=range,
            container=container,
            condition=condition,
            etag=etag,
            validate=validate,
            **kwargs
        )

    def _create_container(self, name: str, **kwargs) -> None:
        container = self._get_container_client(name)
        kwargs['version'] = self._config.api_version
        request = build_create_container_request(
            container.endpoint,
            kwargs
        )
        response = self._client.send_request(request, **kwargs)
        if ((response.status_code == 201) or
            (response.status_code == 409 and response.headers.get(_ERROR_CODE) == 'ContainerAlreadyExists')):
            return
        self._containers.pop(name)
        raise HttpResponseError(response=response)
    
    def _delete_container(self, name: str, **kwargs) -> None:
        if name.lower() == self.default_container_name.lower():
            raise ValueError("Default container cannot be deleted.")
        container = self._get_container_client(name)
        kwargs['version'] = self._config.api_version
        request = build_delete_container_request(
            container.endpoint,
            kwargs
        )
        response = self._client.send_request(request, **kwargs)
        if ((response.status_code == 202) or
            (response.status_code == 404 and response.headers.get(_ERROR_CODE) == 'ContainerNotFound') or
            (response.status_code == 409 and response.headers.get(_ERROR_CODE) == 'ContainerBeingDeleted')):
            self._containers.pop(container, None)
            return
        raise HttpResponseError(response=response)