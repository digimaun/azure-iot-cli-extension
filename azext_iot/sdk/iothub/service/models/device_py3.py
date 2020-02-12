# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class Device(Model):
    """Device.

    :param device_id:
    :type device_id: str
    :param generation_id:
    :type generation_id: str
    :param etag:
    :type etag: str
    :param connection_state: Possible values include: 'Disconnected',
     'Connected'
    :type connection_state: str or ~service.models.enum
    :param status: Possible values include: 'enabled', 'disabled'
    :type status: str or ~service.models.enum
    :param status_reason:
    :type status_reason: str
    :param connection_state_updated_time:
    :type connection_state_updated_time: datetime
    :param status_updated_time:
    :type status_updated_time: datetime
    :param last_activity_time:
    :type last_activity_time: datetime
    :param cloud_to_device_message_count:
    :type cloud_to_device_message_count: int
    :param authentication:
    :type authentication: ~service.models.AuthenticationMechanism
    :param capabilities:
    :type capabilities: ~service.models.DeviceCapabilities
    :param device_scope:
    :type device_scope: str
    """

    _attribute_map = {
        'device_id': {'key': 'deviceId', 'type': 'str'},
        'generation_id': {'key': 'generationId', 'type': 'str'},
        'etag': {'key': 'etag', 'type': 'str'},
        'connection_state': {'key': 'connectionState', 'type': 'str'},
        'status': {'key': 'status', 'type': 'str'},
        'status_reason': {'key': 'statusReason', 'type': 'str'},
        'connection_state_updated_time': {'key': 'connectionStateUpdatedTime', 'type': 'iso-8601'},
        'status_updated_time': {'key': 'statusUpdatedTime', 'type': 'iso-8601'},
        'last_activity_time': {'key': 'lastActivityTime', 'type': 'iso-8601'},
        'cloud_to_device_message_count': {'key': 'cloudToDeviceMessageCount', 'type': 'int'},
        'authentication': {'key': 'authentication', 'type': 'AuthenticationMechanism'},
        'capabilities': {'key': 'capabilities', 'type': 'DeviceCapabilities'},
        'device_scope': {'key': 'deviceScope', 'type': 'str'},
    }

    def __init__(self, *, device_id: str=None, generation_id: str=None, etag: str=None, connection_state=None, status=None, status_reason: str=None, connection_state_updated_time=None, status_updated_time=None, last_activity_time=None, cloud_to_device_message_count: int=None, authentication=None, capabilities=None, device_scope: str=None, **kwargs) -> None:
        super(Device, self).__init__(**kwargs)
        self.device_id = device_id
        self.generation_id = generation_id
        self.etag = etag
        self.connection_state = connection_state
        self.status = status
        self.status_reason = status_reason
        self.connection_state_updated_time = connection_state_updated_time
        self.status_updated_time = status_updated_time
        self.last_activity_time = last_activity_time
        self.cloud_to_device_message_count = cloud_to_device_message_count
        self.authentication = authentication
        self.capabilities = capabilities
        self.device_scope = device_scope
