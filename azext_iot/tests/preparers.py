# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk.preparers import (
    NoTrafficRecordingPreparer,
    SingleValueReplacer,
    ResourceGroupPreparer,
)
from azure.cli.testsdk.reverse_dependency import get_dummy_cli
from azure.cli.testsdk.exceptions import CliTestError
from . import PREFIX_TEST_IOTHUB

fake_iothub_cstring_template = (
    "HostName={}.azure-devices.net;SharedAccessKeyName=iothubowner;"
    "SharedAccessKey=K+5PFFSsLTxgueYNmGR+RZMHeAQCFAcqxRh6uTV4gmY="
)


class IotHubPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(
        self,
        name_prefix=PREFIX_TEST_IOTHUB,
        sku="S1",
        partitions="4",
        location="westus2",
        parameter_name="iothub_name",
        parameter_cstring_name="iothub_cstring",
        resource_group_parameter_name="resource_group",
        skip_delete=True,
        dev_setting_name="AZURE_CLI_TEST_DEV_IOTHUB_NAME",
        key="iothub",
    ):
        super(IotHubPreparer, self).__init__(name_prefix, 24)
        self.cli_ctx = get_dummy_cli()
        self.location = location
        self.sku = sku
        self.partitions = partitions
        self.resource_group_parameter_name = resource_group_parameter_name
        self.skip_delete = skip_delete
        self.parameter_name = parameter_name
        self.parameter_cstring_name = parameter_cstring_name
        self.key = key
        self.dev_setting_name = os.environ.get(dev_setting_name, None)

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        if not self.dev_setting_name:
            template = (
                "az iot hub create -n {} -g {} -l {} --sku {} --partition-count {}"
            )
            self.live_only_execute(
                self.cli_ctx, template.format(name, group, self.location, self.sku, self.partitions)
            )
            return {
                self.parameter_name: name,
                self.parameter_cstring_name: self._get_hub_cstring(name, group),
            }

        self.test_class_instance.kwargs[self.key] = name
        return {
            self.parameter_name: self.dev_setting_name,
            self.parameter_cstring_name: self._get_hub_cstring(name, group),
        }

    def remove_resource(self, name, **kwargs):
        if not self.skip_delete and not self.dev_setting_name:
            group = self._get_resource_group(**kwargs)
            self.live_only_execute(
                self.cli_ctx, "az iot hub delete -n {} -g {}".format(name, group)
            )

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = (
                "To create an IotHub a resource group is required. Please add "
                "decorator @{} in front of this IotHub preparer."
            )
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_hub_cstring(self, name, group):
        template = "az iot hub show-connection-string -n {} -g {}"
        result = self.live_only_execute(self.cli_ctx, template.format(name, group))
        return (
            result.get_output_in_json()["connectionString"]
            if result
            else fake_iothub_cstring_template.format(self.resource_moniker)
        )
