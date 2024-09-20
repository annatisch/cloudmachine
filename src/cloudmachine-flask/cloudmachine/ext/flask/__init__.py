# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Optional, Union, Dict, Any, Literal, List
import sys
import os
import functools

from contextlib import contextmanager
import click
from flask import g, session, current_app

from ._version import VERSION
from ..._client import CloudMachineStorage
from ...resources import CloudMachineDeployment

__version__ = VERSION


class User:
    storage: CloudMachineStorage

    @property
    def storage(self) -> CloudMachineStorage:
        if not current_app:
            raise RuntimeError("CloudMachine only availble within an app context.")
        return CloudMachineStorage()


class CloudMachineSession:
    _storage: CloudMachineStorage
    _db: object
    _fs: object
    _messaging: object
    _vault: object
    _authenticated: bool = False

    def __init__(self):
        self._storage = None

    def close(self):
        if self._storage:
            self._storage.close()

    @property
    def storage(self) -> CloudMachineStorage:
        if not current_app:
            raise RuntimeError("CloudMachine only availble within an app context.")
        if not self._storage:
            raise RuntimeError("CloudMachine has not been configured with a Storage resource.")
        return CloudMachineStorage(self._storage)
    
    @property
    def user(self) -> User:
        if not current_app:
            raise RuntimeError("CloudMachine only availble within an app context.")
        if not self.authenticated:
            raise RuntimeError("CloudMachine is not current user-authenticated.")
        return User()


class CloudMachine:
    def __init__(
            self,
            app = None,
            *,
            name: str,
            location: Optional[str] = None,
            deployment: Optional[CloudMachineDeployment] = None,
            local: bool = True
    ):
        # read config file to determine endpoints for each resource.
        self._resources = deployment or CloudMachineDeployment(name=name, location=location)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self._create_session)
        app.teardown_appcontext(self._close_session)
        init_cmd = functools.partial(init_infra, self._resources)
        app.cli.add_command(click.Command('init-infra', callback=init_cmd))

    def _create_session(*args) -> None:
        #print("create args", args)
        if not hasattr(g, 'cloudmachine'):
            g.cloudmachine = CloudMachineSession()

    def _close_session(*args) -> None:
        #print("close args", args)
        if hasattr(g, 'cloudmachine'):
            g.cloudmachine.close()


def init_infra(resources) -> None:
    resources.write(os.getcwd())
