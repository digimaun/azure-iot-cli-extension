# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.util import CLIError
from azext_iot.common.shared import SdkType
from azext_iot.common.utility import unpack_msrest_error
from azext_iot.iothub.providers.base import IoTHubProvider, CloudError


logger = get_logger(__name__)


class DeviceStreamProvider(IoTHubProvider):
    def get_device_stream(self, device_id, stream_name):
        service_sdk = self.get_sdk(SdkType.service_sdk)
        return service_sdk.twin.get_device_stream(id=device_id, stream_name=stream_name)
