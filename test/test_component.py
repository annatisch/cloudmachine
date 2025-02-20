from dataclasses import dataclass
from typing import Any
import pytest

from azure.cloudmachine.resources.storage.blobs import BlobStorage
from azure.cloudmachine.resources.storage.blobs.container import BlobContainer
from azure.cloudmachine import (
    Parameter,
    AzureApp,
    AzureInfrastructure,
    resource,
    client,
    MISSING
)

def test_component_resource_config():
    p = Parameter("StorageAccount")
    r = BlobStorage(account=p)

    with pytest.raises(RuntimeError):
        r.parent.name()
    
    assert r.endpoint(config_store={"StorageAccount": "foo"}) == "https://foo.blob.core.windows.net/"
    assert r.parent.name(config_store={"StorageAccount": "foo"}) == "foo"

    p = Parameter("DefaultStorageAccount", default="foobar")
    r = BlobStorage(account=p)
    assert r.parent.name() == "foobar"
    assert r.endpoint() == "https://foobar.blob.core.windows.net/"

    r = BlobStorage.reference(account=p)
    r.parent.name()

def test_component_infra_invalid():
    with pytest.raises(RuntimeError):
        class Foo:
            test = resource()

    with pytest.raises(RuntimeError):
        class Foo:
            test: int = resource()

    with pytest.raises(ValueError):
        class Foo:
            test: BlobStorage = resource(default=BlobStorage(), default_factory=BlobStorage)

    class Foo:
        test: BlobStorage = resource(default_factory=BlobStorage)
    
    foo = Foo()
    with pytest.raises(TypeError):
        foo.test = 3
    with pytest.raises(TypeError):
        foo.test = BlobContainer()

def test_component_infra_basic():

    class Infra(AzureInfrastructure):
        test: BlobStorage = resource()

    assert Infra.test == BlobStorage()
    assert Infra.test._infra is None
    assert Infra.test._infra_type is None
    infra = Infra()
    with pytest.raises(RuntimeError):
        infra.test.parent.name()
    assert infra.test._infra == infra
    assert infra.test._infra_type is Infra
    assert infra.test.parent._infra == infra
    assert infra.test.parent._infra_type is Infra

    infra = Infra(test=BlobStorage(account='foo'))
    assert infra.test._infra == infra
    assert infra.test._infra_type is Infra
    assert infra.test.parent._infra == infra
    assert infra.test.parent._infra_type is Infra

    infra.test = BlobStorage(account='bar')
    assert infra.test._infra == infra
    assert infra.test._infra_type is Infra
    assert infra.test.parent._infra == infra
    assert infra.test.parent._infra_type is Infra


def test_component_infra_hybrid():
    class TestInfra(AzureInfrastructure):
        number: int
        string: str = "teststring"
        resource: BlobContainer = resource()

        def some_func(self) -> str:
            return self.string

    with pytest.raises(TypeError):
        TestInfra()

    infra = TestInfra(number=7)
    assert infra.number == 7
    assert infra.string == "teststring"
    assert infra.some_func() == "teststring"
    assert infra.resource == BlobContainer()


def test_component_infra_defaults():

    class TestInfra(AzureInfrastructure):
        data: BlobStorage = resource(default=MISSING)
    
    with pytest.raises(TypeError):
        TestInfra()

    infra = TestInfra(data=BlobStorage.reference(account='foo'))
    assert infra.data == BlobStorage.reference(account='foo')

    class TestInfra(AzureInfrastructure):
        data: BlobStorage = resource(default_factory=BlobStorage)

    infra = TestInfra()
    assert infra.data == BlobStorage()

    class TestInfra(AzureInfrastructure):
        data: BlobStorage = resource(default=BlobStorage(account='foo'))
    
    infra = TestInfra()
    assert infra.data == BlobStorage(account='foo')


def test_component_infra_config():
    name = Parameter('AccountName')
    rg = Parameter('ResourceGroup', default='sharedrg')

    class Infra(AzureInfrastructure):
        test: BlobStorage = resource(
            default=BlobStorage.reference(account=name, resource_group=rg))

    infra = Infra()
    assert infra.test.resource_group() == 'sharedrg'
    assert infra.test.parent.resource_group() == 'sharedrg'
    assert infra.test.resource_group(config_store={'ResourceGroup': 'foo'}) == 'foo'
    with pytest.raises(RuntimeError):
        infra.test.parent.name()
    assert infra.test.parent.name(config_store={'AccountName': 'foo'}) == 'foo'

    infra = Infra(config_store={'AccountName': 'bar', 'ResourceGroup': 'baz'})
    assert infra._config_store == {'AccountName': 'bar', 'ResourceGroup': 'baz'}
    assert infra.test.resource_group() == 'baz'
    assert infra.test.parent.name() == 'bar'
