# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
shared: Define shared data types(enums); hub and dps connection string functions.

"""

from enum import Enum


class SdkType(Enum):
    """
    Target SDK for interop.
    """
    device_query_sdk = 0
    modules_sdk = 1
    device_twin_sdk = 2
    device_msg_sdk = 3
    custom_sdk = 4
    dps_sdk = 5
    device_sdk = 6
    service_sdk = 7
    pnp_sdk = 8


class EntityStatusType(Enum):
    """
    Resource status.
    """
    disabled = 'disabled'
    enabled = 'enabled'


class SettleType(Enum):
    """
    Settlement state of C2D message.
    """
    complete = 'complete'
    abandon = 'abandon'
    reject = 'reject'


class DeviceAuthType(Enum):
    """
    Device Authorization type.
    """
    shared_private_key = 'shared_private_key'
    x509_thumbprint = 'x509_thumbprint'
    x509_ca = 'x509_ca'


class KeyType(Enum):
    """
    Shared private key.
    """
    primary = 'primary'
    secondary = 'secondary'


class AttestationType(Enum):
    """
    Type of atestation (TMP or certificate based).
    """
    tpm = 'tpm'
    x509 = 'x509'
    symmetricKey = 'symmetricKey'


class ProtocolType(Enum):
    """
    Device message protocol.
    """
    http = 'http'
    mqtt = 'mqtt'


class AckType(Enum):
    """
    Type of request for acknowledgement of c2d message.
    """
    positive = 'positive'
    negative = 'negative'
    full = 'full'


class QueryType(Enum):
    """
    Type of request for acknowledgement of c2d message.
    """
    twin = 'twin'
    job = 'job'


class MetricType(Enum):
    """
    Type of request for acknowledgement of c2d message.
    """
    system = 'system'
    user = 'user'


class ReprovisionType(Enum):
    """
    Type of re-provisioning for device data to different IoT Hub.
    """
    reprovisionandmigratedata = 'reprovisionandmigratedata'
    reprovisionandresetdata = 'reprovisionandresetdata'
    never = 'never'


class AllocationType(Enum):
    """
    Type of allocation for device assigned to the Hub.
    """
    hashed = 'hashed'
    geolatency = 'geolatency'
    static = 'static'


class DistributedTracingSamplingModeType(Enum):
    """
    Enable distributed tracing to add correlation IDs to messages.
    """
    off = 'off'
    on = 'on'


class PnPModelType(Enum):
    """
    Type of PnP Model.
    """
    any = 'any'
    interface = 'Interface'
    capabilityModel = 'capabilityModel'


class ModelSourceType(Enum):
    """
    Type of source to get model definition.
    """
    public = 'public'
    private = 'private'
    device = 'device'
