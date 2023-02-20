# Copyright 2022 Guillaume Belanger
# See LICENSE file for licensing details.

import unittest
from unittest.mock import Mock, patch

from ops import testing
from ops.model import ActiveStatus, BlockedStatus

from charm import SIMAPPOperatorCharm


class TestCharm(unittest.TestCase):
    @patch(
        "charm.KubernetesServicePatch",
        lambda charm, ports: None,
    )
    def setUp(self):
        self.namespace = "whatever"
        self.harness = testing.Harness(SIMAPPOperatorCharm)
        self.harness.set_model_name(name=self.namespace)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    @patch("ops.model.Container.exists")
    def test_given_config_file_is_not_written_when_configure_network_action_then_event_fails(
        self,
        patch_exists,
    ):
        patch_exists.return_value = False
        self.harness.set_can_connect(container="simapp", val=True)

        mock_event = Mock()
        self.harness.charm._on_configure_network_action(event=mock_event)

        mock_event.fail.assert_called_with(message="Config file is not written")

    @patch("ops.model.Container.exists")
    def test_given_cant_connect_to_workload_when_configure_network_action_then_event_fails(
        self,
        patch_exists,
    ):
        patch_exists.return_value = True
        self.harness.set_can_connect(container="simapp", val=False)

        mock_event = Mock()
        self.harness.charm._on_configure_network_action(event=mock_event)

        mock_event.fail.assert_called_with(message="Container is not ready")

    @patch("charm.check_output")
    @patch("ops.model.Container.exists")
    def test_given_can_connect_to_workload_and_config_file_is_written_when_configure_network_action_then_pebble_layer_is_created(  # noqa: E501
        self,
        patch_exists,
        patch_check_output,
    ):
        pod_ip = "1.2.3.4"
        patch_check_output.return_value = pod_ip.encode()
        patch_exists.return_value = True
        self.harness.set_can_connect(container="simapp", val=True)

        mock_event = Mock()
        self.harness.charm._on_configure_network_action(event=mock_event)

        expected_plan = {
            "services": {
                "simapp": {
                    "startup": "enabled",
                    "override": "replace",
                    "command": "/simapp/bin/simapp",
                    "environment": {"POD_IP": "1.2.3.4"},
                }
            }
        }

        updated_plan = self.harness.get_container_pebble_plan("simapp").to_dict()

        self.assertEqual(expected_plan, updated_plan)

    @patch("ops.model.Container.exec", new=Mock())
    @patch("charm.check_output")
    @patch("ops.model.Container.exists")
    def test_given_can_connect_to_workload_and_config_file_is_written_when_configure_network_action_then_status_is_active(  # noqa: E501
        self,
        patch_exists,
        patch_check_output,
    ):
        patch_check_output.return_value = b"1.2.3.4"
        patch_exists.return_value = True
        self.harness.set_can_connect(container="simapp", val=True)

        mock_event = Mock()
        self.harness.charm._on_configure_network_action(event=mock_event)

        self.assertEqual(self.harness.model.unit.status, ActiveStatus())

    def test_given_config_file_not_written_when_pebble_ready_then_status_is_blocked(self):
        self.harness.container_pebble_ready(container_name="simapp")

        self.assertEqual(
            self.harness.model.unit.status, BlockedStatus("Waiting for config file to be written")
        )
