# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import pytest

path_iot_hub_service_factory = "azext_iot.common._azure.iot_hub_service_factory"


@pytest.fixture()
def fixture_cmd(mocker):
    # Placeholder for later use
    mocker.patch(path_iot_hub_service_factory)
    cmd = mocker.MagicMock(name="cli cmd context")
    return cmd
