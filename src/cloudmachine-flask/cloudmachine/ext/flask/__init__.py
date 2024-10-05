# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Optional, Union, Dict, Any, Literal, List, overload
import sys
import os
import functools

from contextlib import contextmanager
import click
from flask import g, session, current_app

from ._version import VERSION

from cloudmachine._client import (
    CloudMachineClient,
    CloudMachineStorage,
    load_dev_environment,
    file_uploaded
)
from cloudmachine.resources import CloudMachineDeployment, init_project

__version__ = VERSION


from blinker import Namespace
cloudmachine_signals = Namespace()

data_uploaded = cloudmachine_signals.signal('data-uploaded')


# class User:
#     storage: CloudMachineStorage

#     @property
#     def storage(self) -> CloudMachineStorage:
#         if not current_app:
#             raise RuntimeError("CloudMachine only availble within an app context.")
#         return CloudMachineStorage()


class CloudMachineSession:

    def __init__(self, local: bool):
        self._client = CloudMachineClient(local=local)

    def close(self):
        self._client.close()

    @property
    def storage(self) -> CloudMachineStorage:
        if not current_app:
            raise RuntimeError("CloudMachineSession only availble within an app context.")
        return self._client.storage

    # @property
    # def user(self) -> User:
    #     if not current_app:
    #         raise RuntimeError("CloudMachine only availble within an app context.")
    #     if not self.authenticated:
    #         raise RuntimeError("CloudMachine is not current user-authenticated.")
    #     return User()


class CloudMachine:
    @overload
    def __init__(
            self,
            app = None,
            *,
            name: str,
            envlabel: Optional[str] = None,
            location: Optional[str] = None,
            host: Literal["local", "appservice", "containerapp"] = "local"
    ):
        ...
    @overload
    def __init__(
            self,
            app = None,
            *,
            deployment: Optional[CloudMachineDeployment] = None,
            local: bool = True
    ):
        ...
    def __init__(self, app = None, **kwargs):
        self.host = kwargs.get('host', 'local')
        # read config file to determine endpoints for each resource.
        self.deployment = kwargs.get('deployment') or CloudMachineDeployment(
            name=kwargs['name'],
            location=kwargs.get('location'))
        self.name = self.deployment.name.lower()
        self.envlabel = kwargs.get('envlabel')
        self._session: Optional[CloudMachineSession] = None
        if app is not None:
            self.init_app(app)

    @property
    def session(self) -> CloudMachineSession:
        if not current_app:
            raise RuntimeError("CloudMachineSession only availble within an app context.")
        if not self._session:
            self._session = CloudMachineSession(self.host)
        return self._session

    def init_app(self, app):
        if 'init-infra' in sys.argv:
            init_cmd = functools.partial(init_infra, self.name, self.host, self.envlabel, self.deployment)
            app.cli.add_command(click.Command('init-infra', callback=init_cmd))
        else:
            if self.host == 'local':
                load_dev_environment(self.name)
        app.before_request(self._create_session)
        app.teardown_appcontext(self._close_session)
        
    def _create_session(self, *args) -> None:
        if not hasattr(g, 'cloudmachine'):
            g.cloudmachine = CloudMachineSession(self.host)

    def _close_session(self, *args) -> None:
        if hasattr(g, 'cloudmachine'):
            g.cloudmachine.close()


def init_infra(name, host, envlabel, resources) -> None:
    init_project(os.getcwd(), name, host, envlabel)
    resources.write(os.getcwd())
