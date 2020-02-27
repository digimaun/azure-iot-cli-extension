# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from azext_iot.iothub.providers.device_identity import DeviceIdentityProvider
from azext_iot.iothub.providers.device_stream import DeviceStreamProvider


logger = get_logger(__name__)


def get_device_metrics(cmd, hub_name=None, resource_group_name=None, login=None):
    device_provider = DeviceIdentityProvider(cmd=cmd, hub_name=hub_name, rg=resource_group_name, login=login)
    return device_provider.get_device_stats()


def get_device_stream(cmd, device_id, stream_name, port=3234, hub_name=None, resource_group_name=None, login=None):
    import six
    import socket

    HOST = '127.0.0.1'  # Standard loopback interface address

    port = int(port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)

    #stream_provider = DeviceStreamProvider(cmd=cmd, hub_name=hub_name, rg=resource_group_name, login=login)
    #stream_meta_response = stream_provider.get_device_stream(device_id=device_id, stream_name=stream_name).response

    #stream_headers = stream_meta_response.headers
    #stream_url = stream_headers["iothub-streaming-url"]
    #stream_authtoken = stream_headers["iothub-streaming-auth-token"]
    #stream_ip = stream_headers["iothub-streaming-ip-address"]
    #stream_accepted = stream_headers["iothub-streaming-is-accepted"]
    #import pdb; pdb.set_trace()
