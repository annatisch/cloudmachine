# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import json

from ._version import VERSION

__version__ = VERSION

from ._client import CloudMachineStorage

__all__ = [
    "CloudMachineStorage"
]


def load_dev_environment():
    azd_dir = os.path.join(os.getcwd(), ".azure")
    if not os.path.isdir(azd_dir):
        raise RuntimeError("No '.azure' directory found in current working dir. Please run 'azd init' with the Minimal template.")

    try:
        azd_env_name = os.environ['AZURE_ENV_NAME']
    except KeyError:
        with open(os.path.join(azd_dir, "config.json")) as azd_config:
            azd_env_name = json.load(azd_config)["defaultEnvironment"]
    from dotenv import load_dotenv
    env_loaded = load_dotenv(os.path.join(azd_dir, azd_env_name, ".env"), overwrite=True)
    if not env_loaded:
        raise RuntimeError("No cloudmachine infrastructure loaded. Please run 'azd provision' to provision cloudmachine resources.")
