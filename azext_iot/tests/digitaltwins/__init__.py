# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest
from azext_iot.tests.generators import generate_generic_id
from azext_iot.tests.settings import DynamoSettings
from azure.cli.testsdk import LiveScenarioTest
from azext_iot.common.embedded_cli import EmbeddedCLI


MOCK_RESOURCE_TAGS = "a=b c=d"
MOCK_RESOURCE_TAGS_DICT = {"a": "b", "c": "d"}
MOCK_DEAD_LETTER_SECRET = (
    "https://accountname.blob.core.windows.net/containerName?sasToken"
)
REGION_RESOURCE_LIMIT = 10
REGION_LIST = ["westus2", "westus", "eastus", "eastus2euap"]


def generate_resource_id():
    return "dtcli-{}".format(generate_generic_id())


class DTLiveScenarioTest(LiveScenarioTest):
    role_map = {
        "owner": "Azure Digital Twins Data Owner",
        "reader": "Azure Digital Twins Data Reader",
    }

    def __init__(self, test_scenario, required_capacity=1):
        assert test_scenario

        super(DTLiveScenarioTest, self).__init__(test_scenario)
        self.settings = DynamoSettings(
            opt_env_set=["azext_iot_testrg", "azext_dt_region"]
        )
        self.required_capacity = required_capacity
        self.embedded_cli = EmbeddedCLI()
        self._bootup_scenario()

    def _bootup_scenario(self):
        self._is_provider_registered()
        self._init_basic_env_vars()
        self.tracked_instances = []

    def _is_provider_registered(self):
        result = self.cmd(
            "provider show --namespace 'Microsoft.DigitalTwins' --query 'registrationState'"
        )
        if '"registered"' in result.output.lower():
            return

        pytest.skip(
            "Microsoft.DigitalTwins provider not registered. "
            "Run 'az provider register --namespace Microsoft.DigitalTwins'"
        )

    def _init_basic_env_vars(self):
        self._force_region = self.settings.env.azext_dt_region
        if self._force_region and not self.is_region_available(self._force_region):
            raise RuntimeError(
                "Forced region: {} does not have capacity.".format(self._force_region)
            )

        self.region = (
            self._force_region if self._force_region else self.get_available_region()
        )
        self.rg = self.settings.env.azext_iot_testrg
        if not self.rg:
            pytest.skip(
                "Digital Twins CLI tests requires at least 'azext_iot_testrg' for resource deployment."
            )
        self.rg_region = self.embedded_cli.invoke(
            "group show --name {}".format(self.rg)
        ).as_json()["location"]

    @property
    def current_user(self):
        return self.embedded_cli.invoke("account show").as_json()["user"]["name"]

    @property
    def current_subscription(self):
        return self.embedded_cli.invoke("account show").as_json()["id"]

    def is_region_available(self, region, capacity=None):
        if not capacity:
            capacity = self.required_capacity
        region_capacity = self.calculate_region_capacity
        return (region_capacity.get(region, 0) + capacity) <= REGION_RESOURCE_LIMIT

    @property
    def calculate_region_capacity(self) -> dict:
        instances = self.instances = self.embedded_cli.invoke("dt list").as_json()
        capacity_map = {}
        for instance in instances:
            cap_val = capacity_map.get(instance["location"], 0)
            cap_val = cap_val + 1
            capacity_map[instance["location"]] = cap_val

        for region in REGION_LIST:
            if region not in capacity_map:
                capacity_map[region] = 0

        return capacity_map

    def get_available_region(self, capacity=None, skip_regions: list = None) -> str:
        if not skip_regions:
            skip_regions = []
        if not capacity:
            capacity = self.required_capacity
        region_capacity = self.calculate_region_capacity
        for region in region_capacity:
            if region_capacity[region] + capacity <= REGION_RESOURCE_LIMIT:
                if region not in skip_regions:
                    return region

        raise RuntimeError(
            "There are no available regions with capacity: {} for provision DT instances in subscription: {}".format(
                capacity, self.current_subscription
            )
        )

    def track_instance(self, instance: dict):
        self.tracked_instances.append((instance["name"], instance["resourceGroup"]))

    def tearDown(self):
        for instance in self.tracked_instances:
            self.embedded_cli.invoke(
                "dt delete -n {} -g {} -y --no-wait".format(instance[0], instance[1])
            )
