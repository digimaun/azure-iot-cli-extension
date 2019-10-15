# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import io
import os

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.reverse_dependency import get_dummy_cli
from azure.cli.core.commands.client_factory import get_subscription_id
from azure_devtools.scenario_tests import GeneralNameReplacer
from contextlib import contextmanager


PREFIX_DEVICE = "test-device-"
PREFIX_EDGE_DEVICE = "test-edge-device-"
PREFIX_DEVICE_MODULE = "test-module-"
PREFIX_CONFIG = "test-config-"
PREFIX_EDGE_CONFIG = "test-edgedeploy-"
PREFIX_TEST_IOTHUB = "testiotext"
PREFIX_TEST_RG = "iot.cli.test.automation."

# Replaced mock values
MOCKED_SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"


@contextmanager
def capture_output():
    class stream_buffer_tee(object):
        def __init__(self):
            self.stdout = sys.stdout
            self.buffer = io.StringIO()

        def write(self, message):
            self.stdout.write(message)
            self.buffer.write(message)

        def flush(self):
            self.stdout.flush()
            self.buffer.flush()

        def get_output(self):
            return self.buffer.getvalue()

        def close(self):
            self.buffer.close()

    _stdout = sys.stdout
    buffer_tee = stream_buffer_tee()
    sys.stdout = buffer_tee
    try:
        yield buffer_tee
    finally:
        sys.stdout = _stdout
        buffer_tee.close()


class IoTScenarioTest(ScenarioTest):
    def __init__(self, test_scenario):
        assert test_scenario
        os.environ["AZURE_CORE_COLLECT_TELEMETRY"] = "no"
        sub_id = get_subscription_id(get_dummy_cli())

        IoTTokenReplacer = GeneralNameReplacer()
        IoTTokenReplacer.register_name_pair(sub_id, MOCKED_SUBSCRIPTION_ID)

        super(IoTScenarioTest, self).__init__(
            test_scenario,
            recording_processors=[IoTTokenReplacer],
        )

        self.entity_name = None
        self.entity_cstring = None
        self.entity_rg = None

        self.device_ids = []
        self.config_ids = []

    def configure(self, rg, name, cstring=None):
        self.entity_name = name
        self.entity_rg = rg
        if cstring:
            self.entity_cstring = cstring

    def _is_configured(self):
        return all([self.entity_rg, self.entity_name])

    def generate_device_names(self, count=1, edge=False):
        device_prefix = PREFIX_DEVICE if not edge else PREFIX_EDGE_DEVICE
        names = ["{}{}".format(device_prefix, i) for i in range(count)]

        self.device_ids.extend(names)
        return names

    def generate_module_names(self, count=1):
        return ["{}{}".format(PREFIX_DEVICE_MODULE, i) for i in range(count)]

    def generate_config_names(self, count=1, edge=False):
        config_prefix = PREFIX_CONFIG if not edge else PREFIX_EDGE_CONFIG
        names = ["{}{}".format(config_prefix, i) for i in range(count)]
        self.config_ids.extend(names)
        return names

    # TODO: @digimaun - Maybe put a helper like this in the shared lib, when you create it?
    def command_execute_assert(self, command, asserts):
        from . import capture_output

        with capture_output() as buffer:
            self.cmd(command, checks=None)
            output = buffer.get_output()

        for a in asserts:
            assert a in output

    # Using tearDown will screw up the recording context.
    def cleanUp(self):
        if not self._is_configured():
            raise RuntimeError("Clean up requires a prior configure(...) call!")

        if self.device_ids:
            if self.entity_cstring:
                device = self.device_ids.pop()
                self.cmd(
                    "iot hub device-identity delete -d {} --login {}".format(
                        device, self.entity_cstring
                    ),
                    checks=self.is_empty(),
                )

            for device in self.device_ids:
                self.cmd(
                    "iot hub device-identity delete -d {} -n {} -g {}".format(
                        device, self.entity_name, self.entity_rg
                    ),
                    checks=self.is_empty(),
                )

        if self.config_ids:
            if self.entity_cstring:
                config = self.config_ids.pop()
                self.cmd(
                    "iot hub configuration delete -c {} --login {}".format(
                        config, self.entity_cstring
                    ),
                    checks=self.is_empty(),
                )

            for config in self.config_ids:
                self.cmd(
                    "iot hub configuration delete -c {} -n {} -g {}".format(
                        config, self.entity_name, self.entity_rg
                    ),
                    checks=self.is_empty(),
                )
