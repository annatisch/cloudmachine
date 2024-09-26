#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import re

from setuptools import find_packages, setup

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "cloudmachine"
PACKAGE_PPRINT_NAME = "Cloud Machine"

# a-b-c => a/b/c
package_folder_path = PACKAGE_NAME.replace("-", "/")


# Version extraction inspired from 'requests'
with open(os.path.join(package_folder_path, "_version.py"), "r") as fd:
    version = re.search(
        r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

if not version:
    raise RuntimeError("Cannot find version information")

setup(
    name=PACKAGE_NAME,
    version=version,
    description="Microsoft {} for Python".format(
        PACKAGE_PPRINT_NAME
    ),
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azpysdkhelp@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "pytyped": ["py.typed"],
    },
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=1.0.0",
        "azure-storage-blob>=2.1.0"
    ],
    extras_require={
        "flask": [
            "cloudmachine-flask>=0.0.1a1",
        ],
        "quart": [
            "cloudmachine-quart>=0.0.1a1",
        ],
        # django
        # fastapi
    },
    entry_points={
        'console_scripts': [
            "cloudmachine = cloudmachine._command:command"
        ],
    },
)
