#!/usr/bin/env python
# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import os.path
from io import open
from setuptools import setup, find_packages


EXTENSION_REF_NAME = "azext_iot"

# Version extraction inspired from 'requests'
with open(os.path.join(EXTENSION_REF_NAME, "constants.py"), "r", encoding="utf-8") as fd:
    constants_raw = fd.read()
    VERSION = re.search(
        r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', constants_raw, re.MULTILINE
    ).group(1)

    PACKAGE_NAME = re.search(
        r'^EXTENSION_NAME\s*=\s*[\'"]([^\'"]*)[\'"]', constants_raw, re.MULTILINE
    ).group(1)


if not VERSION:
    raise RuntimeError("Cannot find version information")

if not PACKAGE_NAME:
    raise RuntimeError("Cannot find package information")


# The following dependencies are needed by the IoT extension.
# Most of these are leveraged from Az CLI Core.
# 'msrestazure>=0.4.29,<2.0.0',
# 'paho-mqtt==1.3.1',
# 'jmespath==0.9.3',
# 'pyyaml==3.13'
# 'knack>=0.3.1'
# 'jsonschema==3.0.2'

# There is also a dependency for uamqp for amqp based commands
# though that is installed out of band (managed by the extension)
# for compatibility reasons.

DEPENDENCIES = ["paho-mqtt==1.3.1", "jsonschema==3.0.2", "setuptools"]


CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "License :: OSI Approved :: MIT License",
]

with open("HISTORY.rst", "r", encoding="utf-8") as f:
    HISTORY = f.read()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="Provides the data plane command layer for Azure IoT Hub, IoT Edge and IoT Device Provisioning Service",
    long_description="Authoritative IoT data plane extension for Azure CLI. "
    + "\n\n"
    + HISTORY,
    license="MIT",
    author="Microsoft",
    author_email="iotupx@microsoft.com",  # +@digimaun
    url="https://github.com/azure/azure-iot-cli-extension",
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "*tests", "scripts"]),
    package_data={
        EXTENSION_REF_NAME: [
            "azext_metadata.json",
            "digicert.pem",
            "assets/edge-deploy-2.0.schema.json",
        ]
    },
    install_requires=DEPENDENCIES,
)
