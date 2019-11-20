# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import pytest
import json
import os
from uuid import uuid4
from random import randint
from knack.cli import CLIError
from azext_iot.operations import hub as subject
from azext_iot.common.utility import read_file_content, evaluate_literal
from ..conftest import build_mock_response, path_service_client, mock_target

config_id = "myconfig-{}".format(str(uuid4()).replace("-", ""))


@pytest.fixture
def sample_config_show(set_cwd):
    path = "test_config_modules_show.json"
    result = json.loads(read_file_content(path))
    return result


@pytest.fixture
def sample_config_edge_malformed(set_cwd):
    path = "test_edge_deployment_malformed.json"
    result = json.dumps(json.loads(read_file_content(path)))
    return result


@pytest.fixture(params=["file", "inlineA", "inlineB", "layered"])
def sample_config_edge(set_cwd, request):
    path = "test_edge_deployment.json"
    layered_path = "test_edge_deployment_layered.json"

    payload = None
    if request.param == "inlineA":
        payload = json.dumps(json.loads(read_file_content(path)))
    elif request.param == "inlineB":
        payload = json.dumps(json.loads(read_file_content(path))["content"])
    elif request.param == "file":
        payload = os.path.join(os.path.dirname(os.path.abspath(request.fspath)), path)
    elif request.param == "layered":
        payload = json.dumps(json.loads(read_file_content(layered_path)))

    return (request.param, payload)


@pytest.fixture(params=["file", "inlineA", "inlineB", None])
def sample_config_metrics(set_cwd, request):
    path = "test_config_generic_metrics.json"

    payload = None
    if request.param == "inlineA":
        payload = json.dumps(json.loads(read_file_content(path)))
    elif request.param == "inlineB":
        payload = json.dumps(json.loads(read_file_content(path))["metrics"])
    elif request.param == "file":
        payload = os.path.join(os.path.dirname(os.path.abspath(request.fspath)), path)

    return (request.param, payload)


@pytest.fixture(params=["moduleFile", "moduleInline", "deviceFile", "deviceInline"])
def sample_config_adm(set_cwd, request):
    path_device = "test_adm_device_content.json"
    path_module = "test_adm_module_content.json"

    payload = None
    if request.param == "moduleFile":
        payload = os.path.join(
            os.path.dirname(os.path.abspath(request.fspath)), path_module
        )
    elif request.param == "moduleInline":
        payload = json.dumps(json.loads(read_file_content(path_module)))
    elif request.param == "deviceFile":
        payload = os.path.join(
            os.path.dirname(os.path.abspath(request.fspath)), path_device
        )
    elif request.param == "deviceInline":
        payload = json.dumps(json.loads(read_file_content(path_device)))

    return (request.param, payload)


class TestConfigMetricShow:
    @pytest.fixture(params=[200])
    def serviceclient(
        self, mocker, fixture_ghcs, fixture_sas, request, sample_config_show
    ):
        service_client = mocker.patch(path_service_client)
        service_client.side_effect = [
            build_mock_response(mocker, payload=sample_config_show),
            build_mock_response(
                mocker, payload=[], headers={"x-ms-continuation": None}
            ),
        ]
        return service_client

    @pytest.mark.parametrize(
        "metric_id, content_type, metric_type",
        [
            ("appliedCount", "modulesContent", "system"),
            ("mymetric", "modulesContent", "user"),
            ("appliedCount", "moduleContent", "system"),
            ("mymetric", "moduleContent", "user"),
            ("appliedCount", "deviceContent", "system"),
            ("mymetric", "deviceContent", "user"),
        ],
    )
    def test_config_metric_show(
        self,
        fixture_cmd2,
        serviceclient,
        metric_id,
        content_type,
        metric_type,
        sample_config_show,
    ):
        from functools import partial

        target_method = (
            partial(subject.iot_edge_deployment_metric_show)
            if content_type == "modulesContent"
            else partial(subject.iot_hub_configuration_metric_show)
        )
        result = target_method(
            cmd=fixture_cmd2,
            config_id=config_id,
            metric_type=metric_type,
            metric_id=metric_id,
            hub_name=mock_target["entity"],
        )
        expected = sample_config_show

        metric_type_key = "systemMetrics" if metric_type == "system" else "metrics"
        assert result["metric"] == metric_id
        assert result["query"] == expected[metric_type_key]["queries"][metric_id]

        query_args = serviceclient.call_args_list[1]
        query_body = query_args[0][2]

        assert query_body["query"] == expected[metric_type_key]["queries"][metric_id]

    @pytest.mark.parametrize(
        "metric_id, content_type, metric_type",
        [
            ("doesnotexist0", "modules", "system"),
            ("doesnotexist1", "modules", "user"),
            ("doesnotexist2", "modules", "sometype"),
            ("doesnotexist3", "device", "system"),
            ("doesnotexist4", "device", "user"),
            ("doesnotexist5", "device", "sometype"),
            ("doesnotexist6", "module", "system"),
            ("doesnotexist7", "module", "user"),
            ("doesnotexist8", "module", "sometype"),
        ],
    )
    def test_config_metric_show_invalid_args(
        self, fixture_cmd2, serviceclient, metric_id, content_type, metric_type
    ):
        from functools import partial

        with pytest.raises(CLIError):
            target_method = (
                partial(subject.iot_edge_deployment_metric_show)
                if content_type == "modulesContent"
                else partial(subject.iot_hub_configuration_metric_show)
            )

            target_method(
                cmd=fixture_cmd2,
                config_id=config_id,
                metric_type=metric_type,
                metric_id=metric_id,
                hub_name=mock_target["entity"],
            )


class TestConfigShow:
    @pytest.fixture(params=[200])
    def serviceclient(
        self, mocker, fixture_ghcs, fixture_sas, request, sample_config_show
    ):
        service_client = mocker.patch(path_service_client)
        service_client.return_value = build_mock_response(
            mocker, request.param, sample_config_show
        )
        return service_client

    def test_config_show(self, serviceclient, fixture_cmd2):
        result = subject.iot_hub_configuration_show(
            fixture_cmd2, config_id=config_id, hub_name=mock_target["entity"]
        )

        args = serviceclient.call_args
        url = args[0][0].url
        method = args[0][0].method

        assert "{}/configurations/{}?".format(mock_target["entity"], config_id) in url
        assert method == "GET"
        assert isinstance(result, dict)

    def test_config_show_error(self, serviceclient_generic_error, fixture_cmd2):
        with pytest.raises(CLIError):
            subject.iot_hub_configuration_show(
                fixture_cmd2, config_id=config_id, hub_name=mock_target["entity"]
            )


class TestConfigCreate:
    @pytest.fixture(params=[200])
    def serviceclient(self, mocker, fixture_ghcs, fixture_sas, request):
        service_client = mocker.patch(path_service_client)
        service_client.return_value = build_mock_response(mocker, request.param, {})
        return service_client

    @pytest.mark.parametrize(
        "config_id, hub_name, target_condition, priority, labels",
        [
            (
                "UPPERCASEID",
                mock_target["entity"],
                "tags.building=43 and tags.environment='test'",
                randint(0, 100),
                '{"key1":"value1"}',
            ),
            (
                "lowercaseid",
                mock_target["entity"],
                "tags.building=43 and tags.environment='test'",
                randint(0, 100),
                None,
            ),
            ("mixedCaseId", mock_target["entity"], None, None, None),
        ],
    )
    def test_config_create_edge(
        self,
        fixture_cmd2,
        serviceclient,
        sample_config_edge,
        sample_config_metrics,
        config_id,
        hub_name,
        target_condition,
        priority,
        labels,
    ):
        subject.iot_edge_deployment_create(
            cmd=fixture_cmd2,
            config_id=config_id,
            hub_name=hub_name,
            content=sample_config_edge[1],
            target_condition=target_condition,
            priority=priority,
            labels=labels,
            metrics=sample_config_metrics[1],
            layered=(sample_config_edge[0] == "layered")
        )

        args = serviceclient.call_args
        url = args[0][0].url
        method = args[0][0].method
        body = args[0][2]

        assert "{}/configurations/{}?".format(hub_name, config_id.lower()) in url
        assert method == "PUT"
        assert body["id"] == config_id.lower()
        assert body["contentType"] == "assignment"
        assert body.get("targetCondition") == target_condition
        assert body.get("priority") == priority
        assert body.get("labels") == evaluate_literal(labels, dict)

        if sample_config_edge[0] == "inlineA" or sample_config_edge[0] == "layered":
            assert (
                body["content"]["modulesContent"]
                == json.loads(sample_config_edge[1])["content"]["modulesContent"]
            )
        elif sample_config_edge[0] == "inlineB":
            assert (
                body["content"]["modulesContent"]
                == json.loads(sample_config_edge[1])["modulesContent"]
            )
        else:
            assert (
                body["content"]["modulesContent"]
                == json.loads(read_file_content(sample_config_edge[1]))["content"][
                    "modulesContent"
                ]
            )

        self._assert_config_metrics_request(sample_config_metrics, body)

    @pytest.mark.parametrize(
        "config_id, hub_name, target_condition, priority, labels",
        [
            (
                "lowercaseid",
                mock_target["entity"],
                "tags.building=43 and tags.environment='test'",
                randint(0, 100),
                None,
            )
        ],
    )
    def test_config_create_edge_malformed(
        self,
        fixture_cmd2,
        serviceclient,
        sample_config_edge_malformed,
        config_id,
        hub_name,
        target_condition,
        priority,
        labels,
    ):
        with pytest.raises(CLIError) as exc:
            subject.iot_edge_deployment_create(
                cmd=fixture_cmd2,
                config_id=config_id,
                hub_name=hub_name,
                content=sample_config_edge_malformed,
                target_condition=target_condition,
                priority=priority,
                labels=labels,
            )

        exception_obj = json.loads(str(exc.value))
        assert "validationErrors" in exception_obj
        for error_element in exception_obj["validationErrors"]:
            assert "description" in error_element
            assert "contentPath" in error_element
            assert "schemaPath" in error_element

    @pytest.mark.parametrize(
        "config_id, hub_name, target_condition, priority, labels",
        [
            (
                "UPPERCASEID",
                mock_target["entity"],
                "tags.building=43 and tags.environment='test'",
                randint(0, 100),
                '{"key1":"value1"}',
            ),
            (
                "lowercaseid",
                mock_target["entity"],
                "tags.building=43 and tags.environment='test'",
                randint(0, 100),
                None,
            ),
            ("mixedCaseId", mock_target["entity"], None, None, None),
        ],
    )
    def test_config_create_adm(
        self,
        fixture_cmd2,
        serviceclient,
        sample_config_adm,
        sample_config_metrics,
        config_id,
        hub_name,
        target_condition,
        priority,
        labels,
    ):
        subject.iot_hub_configuration_create(
            cmd=fixture_cmd2,
            config_id=config_id,
            hub_name=hub_name,
            content=sample_config_adm[1],
            target_condition=target_condition,
            priority=priority,
            labels=labels,
            metrics=sample_config_metrics[1],
        )

        args = serviceclient.call_args
        url = args[0][0].url
        method = args[0][0].method
        body = args[0][2]

        assert "{}/configurations/{}?".format(hub_name, config_id.lower()) in url
        assert method == "PUT"
        assert body["id"] == config_id.lower()
        assert body["contentType"] == "assignment"
        assert body.get("targetCondition") == target_condition
        assert body.get("priority") == priority
        assert body.get("labels") == evaluate_literal(labels, dict)

        contentKey = (
            "moduleContent"
            if sample_config_adm[0].startswith("module")
            else "deviceContent"
        )

        if sample_config_adm[0].endswith("Inline"):
            assert (
                body["content"][contentKey]
                == json.loads(sample_config_adm[1])["content"][contentKey]
            )
        elif sample_config_adm[0].endswith("File"):
            assert (
                body["content"][contentKey]
                == json.loads(read_file_content(sample_config_adm[1]))["content"][
                    contentKey
                ]
            )

        self._assert_config_metrics_request(sample_config_metrics, body)

    def _assert_config_metrics_request(self, sample_config_metrics, body):
        if sample_config_metrics[0]:
            if sample_config_metrics[0] == "inlineA":
                assert (
                    body["metrics"] == json.loads(sample_config_metrics[1])["metrics"]
                )
            elif sample_config_metrics[0] == "inlineB":
                assert body["metrics"] == json.loads(sample_config_metrics[1])
            else:
                assert (
                    body["metrics"]
                    == json.loads(read_file_content(sample_config_metrics[1]))[
                        "metrics"
                    ]
                )
        else:
            assert body["metrics"] == {}

    @pytest.mark.parametrize(
        "config_id, hub_name, target_condition, priority, labels",
        [
            (
                "lowercaseid",
                mock_target["entity"],
                "tags.building=43 and tags.environment='test'",
                randint(0, 100),
                None,
            )
        ],
    )
    def test_config_create_adm_invalid(
        self,
        fixture_cmd2,
        serviceclient,
        sample_config_edge,
        config_id,
        hub_name,
        target_condition,
        priority,
        labels,
    ):
        with pytest.raises(CLIError) as exc:
            subject.iot_hub_configuration_create(
                cmd=fixture_cmd2,
                config_id=config_id,
                hub_name=hub_name,
                content=sample_config_edge[1],
                target_condition=target_condition,
                priority=priority,
                labels=labels,
            )

        assert (
            str(exc.value)
            == "Automatic device configuration payloads require property: deviceContent or moduleContent"
        )

    @pytest.mark.parametrize(
        "config_id, hub_name, target_condition, priority, labels",
        [
            (
                "lowercaseid",
                mock_target["entity"],
                "tags.building=43 and tags.environment='test'",
                randint(0, 100),
                None,
            )
        ],
    )
    def test_config_create_error(
        self,
        fixture_cmd2,
        serviceclient_generic_error,
        sample_config_edge,
        config_id,
        hub_name,
        target_condition,
        priority,
        labels,
    ):
        with pytest.raises(CLIError):
            subject.iot_edge_deployment_create(
                cmd=fixture_cmd2,
                config_id=config_id,
                hub_name=hub_name,
                content=sample_config_edge[1],
                target_condition=target_condition,
                priority=priority,
                labels=labels,
            )


class TestConfigDelete:
    @pytest.fixture(params=[(200, 204)])
    def serviceclient(self, mocker, fixture_ghcs, fixture_sas, request):
        service_client = mocker.patch(path_service_client)
        etag = str(uuid4())
        service_client.expected_etag = etag
        side_effect = [
            build_mock_response(mocker, request.param[0], {"etag": etag}),
            build_mock_response(mocker, request.param[1]),
        ]
        service_client.side_effect = side_effect
        return service_client

    def test_config_delete(self, serviceclient, fixture_cmd2):
        subject.iot_hub_configuration_delete(
            fixture_cmd2, config_id=config_id, hub_name=mock_target["entity"]
        )
        args = serviceclient.call_args
        url = args[0][0].url
        method = args[0][0].method
        headers = args[0][1]

        assert method == "DELETE"
        assert "{}/configurations/{}?".format(mock_target["entity"], config_id) in url
        assert headers["If-Match"] == '"{}"'.format(serviceclient.expected_etag)

    @pytest.mark.parametrize("expected_error", [CLIError])
    def test_config_delete_invalid_args(
        self, fixture_cmd2, serviceclient_generic_invalid_or_missing_etag, expected_error
    ):
        with pytest.raises(expected_error):
            subject.iot_hub_configuration_delete(
                fixture_cmd2, config_id=config_id, hub_name=mock_target["entity"]
            )

    def test_config_delete_error(self, fixture_cmd2, serviceclient_generic_error):
        with pytest.raises(CLIError):
            subject.iot_hub_configuration_delete(
                fixture_cmd2, config_id=config_id, hub_name=mock_target["entity"]
            )


# class TestConfigUpdate:
#     @pytest.fixture(params=[200])
#     def serviceclient(self, mocker, fixture_ghcs, fixture_sas, request):
#         service_client = mocker.patch(path_service_client)
#         service_client.return_value = build_mock_response(mocker, request.param, {})
#         return service_client

#     @pytest.mark.parametrize(
#         "req",
#         [
#             (generate_device_config(scenario="update")),
#             (
#                 generate_device_config(
#                     scenario="update", content_type="device", include_metrics=True
#                 )
#             ),
#         ],
#     )
#     def test_config_update(self, serviceclient, req):
#         req_copy = copy.deepcopy(req)
#         subject.iot_hub_configuration_update(
#             fixture_cmd,
#             config_id=req["id"],
#             hub_name=mock_target["entity"],
#             parameters=req_copy,
#         )
#         args = serviceclient.call_args
#         url = args[0][0].url
#         method = args[0][0].method
#         body = args[0][2]

#         assert "{}/configurations/{}?".format(mock_target["entity"], req["id"]) in url
#         assert method == "PUT"
#         assert body["id"] == req["id"]

#         assert body["content"] == req["content"]

#         if req.get("metrics"):
#             assert body["metrics"] == req["metrics"]

#         assert body["contentType"] == "assignment"
#         assert body["targetCondition"] == req.get("targetCondition")
#         assert body["priority"] == req.get("priority")
#         assert body.get("labels") == req.get("labels")

#         headers = args[0][1]
#         assert headers["If-Match"] == '"{}"'.format(req["etag"])

#     @pytest.mark.parametrize(
#         "req", [(generate_device_config(scenario="update", etag=""))]
#     )
#     def test_config_update_invalid_args(self, serviceclient, req):
#         with pytest.raises(CLIError):
#             subject.iot_hub_configuration_update(
#                 fixture_cmd,
#                 config_id=config_id,
#                 hub_name=mock_target["entity"],
#                 parameters=req,
#             )

#     @pytest.mark.parametrize("req", [(generate_device_config(scenario="update"))])
#     def test_config_update_error(self, serviceclient_generic_error, req):
#         with pytest.raises(CLIError):
#             subject.iot_hub_configuration_update(
#                 fixture_cmd,
#                 config_id=config_id,
#                 hub_name=mock_target["entity"],
#                 parameters=req,
#             )


# class TestConfigList:
#     @pytest.fixture(params=[(200, 10)])
#     def serviceclient(self, mocker, fixture_ghcs, fixture_sas, request):
#         service_client = mocker.patch(path_service_client)
#         result = []
#         size = request.param[1]
#         for _ in range(size):
#             result.append(generate_device_config(scenario="update"))
#         for _ in range(size):
#             result.append(
#                 generate_device_config(content_type="device", scenario="update")
#             )
#         service_client.expected_size = size
#         service_client.return_value = build_mock_response(
#             mocker, request.param[0], result, {"x-ms-continuation": None}
#         )
#         return service_client

#     @pytest.mark.parametrize("top", [1, 10])
#     def test_config_list(self, serviceclient, top):
#         result = subject.iot_hub_configuration_list(
#             fixture_cmd, hub_name=mock_target["entity"], top=top
#         )
#         args = serviceclient.call_args
#         url = args[0][0].url
#         assert json.dumps(result)
#         assert len(result) == top
#         assert "{}/configurations?".format(mock_target["entity"]) in url
#         assert "top={}".format(top) in url

#     @pytest.mark.parametrize("top", [1, 10])
#     def test_deployment_list(self, serviceclient, top):
#         result = subject.iot_edge_deployment_list(
#             fixture_cmd, hub_name=mock_target["entity"], top=top
#         )
#         args = serviceclient.call_args
#         url = args[0][0].url
#         assert json.dumps(result)
#         assert len(result) == top
#         assert "{}/configurations?".format(mock_target["entity"]) in url
#         assert "top={}".format(top) in url

#     @pytest.mark.parametrize("top", [-1, 0])
#     def test_config_list_invalid_args(self, serviceclient, top):
#         with pytest.raises(CLIError):
#             subject.iot_hub_configuration_list(
#                 fixture_cmd, hub_name=mock_target["entity"], top=top
#             )

#     def test_config_list_error(self, serviceclient_generic_error):
#         with pytest.raises(CLIError):
#             subject.iot_hub_configuration_list(
#                 fixture_cmd, hub_name=mock_target["entity"]
#             )


# class TestConfigApply:
#     @pytest.fixture(params=[200])
#     def serviceclient(self, mocker, fixture_ghcs, fixture_sas, request):
#         service_client = mocker.patch(path_service_client)
#         service_client.side_effect = [
#             build_mock_response(mocker),
#             build_mock_response(mocker, payload=[]),
#         ]
#         return service_client

#     @pytest.mark.parametrize(
#         "req",
#         [
#             (generate_device_config()),
#             (generate_device_config(content_short_form=True)),
#             (generate_device_config(content_from_file=True)),
#         ],
#     )
#     def test_config_apply(self, serviceclient, req):
#         result = subject.iot_edge_set_modules(
#             fixture_cmd,
#             device_id,
#             hub_name=mock_target["entity"],
#             content=req["content"],
#         )
#         args = serviceclient.call_args_list[0]
#         body = args[0][2]

#         if os.path.exists(req["content"]):
#             js = json.loads(str(read_file_content(req["content"])))
#             req["content"] = str(json.dumps(js))

#         if req.get("content_short_form"):
#             if req["schemaVersion"] == "1.0" and req["content_type"] == "modules":
#                 assert (
#                     body["modulesContent"]
#                     == json.loads(req["content"])["moduleContent"]
#                 )
#             else:
#                 assert body == json.loads(req["content"])
#         else:
#             if req["schemaVersion"] == "1.0" and req["content_type"] == "modules":
#                 assert (
#                     body["modulesContent"]
#                     == json.loads(req["content"])["content"]["moduleContent"]
#                 )
#             else:
#                 assert body == json.loads(req["content"])["content"]

#         mod_list_args = serviceclient.call_args_list[1]
#         url = mod_list_args[0][0].url
#         method = mod_list_args[0][0].method

#         assert method == "GET"
#         assert "{}/devices/{}/modules?".format(mock_target["entity"], device_id) in url
#         assert result is not None

#     @pytest.mark.parametrize(
#         "req, arg",
#         [
#             (generate_device_config(), "mangle"),
#             (generate_device_config(content_type="device"), ""),
#         ],
#     )
#     def test_config_apply_invalid_args(self, serviceclient, req, arg):
#         with pytest.raises(CLIError):
#             if arg == "mangle":
#                 req["content"] = req["content"].replace(
#                     '"modulesContent":', '"somethingelse":'
#                 )
#             subject.iot_edge_set_modules(
#                 fixture_cmd,
#                 device_id,
#                 hub_name=mock_target["entity"],
#                 content=req["content"],
#             )

#     @pytest.mark.parametrize("req", [(generate_device_config())])
#     def test_config_apply_error(self, serviceclient_generic_error, req):
#         with pytest.raises(CLIError):
#             subject.iot_edge_set_modules(
#                 fixture_cmd,
#                 device_id,
#                 hub_name=mock_target["entity"],
#                 content=req["content"],
#             )

#     @pytest.mark.parametrize(
#         "req", [(generate_device_config(content_type="malformed_modules"))]
#     )
#     def test_config_apply_schema_validation_error(self, serviceclient, req):
#         with pytest.raises(CLIError):
#             subject.iot_edge_set_modules(
#                 fixture_cmd,
#                 device_id,
#                 hub_name=mock_target["entity"],
#                 content=req["content"],
#             )
