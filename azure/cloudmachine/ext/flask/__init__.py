# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Optional, Literal, overload, Union
import sys
import os
import functools

import click
from flask import g, current_app, Flask

from ._version import VERSION

from ..._client import (
    CloudMachineClient,
    load_dev_environment,
)
from ..._resources._client_settings import ClientSettings
from ...provisioning import (
    CloudMachineDeployment,
    init_project,
    provision_project,
    shutdown_project,
    deploy_project
)

__version__ = VERSION


class CloudMachine(CloudMachineClient):
    label: Optional[str]

    def __init__(
            self,
            app = None,
            *,
            label: Optional[str] = None,
            deployment: Optional[CloudMachineDeployment] = None,
            openai: Optional[Union[ClientSettings, str]] = None,
            data: Optional[Union[ClientSettings, str]] = None,
            messaging: Optional[Union[ClientSettings, str]] = None,
            storage: Optional[Union[ClientSettings, str]] = None,
            search: Optional[Union[ClientSettings, str]] = None,
            documentai: Optional[Union[ClientSettings, str]] = None,
    ):
        super().__init__(
            deployment=deployment,
            openai=openai,
            data=data,
            messaging=messaging,
            storage=storage,
            search=search,
            documentai=documentai
        )
        self.label = label
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.label = self.label or app.config.get('AZURE_CLOUDMACHINE_LABEL')
        for client_settings in self._settings.values():
            if client_settings is not None:
                client_settings.add_config_store(app.config)

        if 'cm' in sys.argv:
            cmd_infra = functools.partial(cm_infra, self)
            cmd_provision = functools.partial(cm_provision_local, self)
            cmd_deploy = functools.partial(cm_provision_remote, self)
            cmd_down = functools.partial(cm_down, self)
            app.cli.add_command(
                click.Group(
                    'cm',
                    commands=[
                        click.Command('infra', callback=cmd_infra,),
                        click.Command('provision', callback=cmd_provision),
                        click.Command('deploy', callback=cmd_deploy),
                        click.Command('down', callback=cmd_down)
                    ]
                )
            )
        else:
            if self.deployment:
                #if self.deployment.host == 'local':
                #os.environ.update(self.deployment.app_settings)
                app.config.update(load_dev_environment(self.deployment.name))
                if self.deployment.monitor:
                    try:
                        from azure.monitor.opentelemetry import configure_azure_monitor
                        from azure.identity import ManagedIdentityCredential
                    except ImportError as e:
                        raise ImportError(
                            "Telemetry has been enabled in CloudMachine, "
                            "but `azure-monitor-opentelemetry not installed.") from e
                    configure_azure_monitor(
                        credential=ManagedIdentityCredential()
                    )
                    # if 'openai' in self._settings:
                    #     from opentelemetry.instrumentation.openai import OpenAIInstrumentor
                    #     # This tracks OpenAI SDK requests:
                    #     OpenAIInstrumentor().instrument()

        # app.before_request(self._create_session)
        # app.teardown_appcontext(self._close_session)
        
    # def _create_session(self, *args) -> None:
    #     if not hasattr(g, 'cloudmachine'):
    #         g.cloudmachine = CloudMachineSession()

    # def _close_session(self, *args) -> None:
    #     if hasattr(g, 'cloudmachine'):
    #         g.cloudmachine.close()


def cm_infra(cm: CloudMachine) -> None:
    init_project(
        os.getcwd(),
        cm.deployment,
        cm.label,
        metadata={'cloudmachine-flask': VERSION}
    )
    cm.deployment.write(os.getcwd())

def cm_provision_local(cm: CloudMachine) -> None:
    provision_project(cm.deployment, cm.label)

def cm_down(cm: CloudMachine) -> None:
    shutdown_project(cm.deployment, cm.label)

def cm_provision_remote(cm: CloudMachine) -> None:
    deploy_project(cm.deployment, cm.label)
