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

    @patch("ops.model.Container.push")
    def test_given_use_default_config_when_on_config_changed_then_default_config_is_written(
        self, patch_push
    ):
        self.harness.set_can_connect(container="simapp", val=True)

        self.harness.update_config({"use-default-config": True})

        patch_push.assert_called_with(
            path="/simapp/config/simapp.yaml",
            source='configuration:\n  device-groups:\n  - imsis:\n    - "208930100007487"\n    - "208930100007488"\n    - "208930100007489"\n    - "208930100007490"\n    - "208930100007491"\n    - "208930100007492"\n    - "208930100007493"\n    - "208930100007494"\n    - "208930100007495"\n    - "208930100007496"\n    - "208930100007497"\n    - "208930100007498"\n    - "208930100007499"\n    - "208930100007500"\n    ip-domain-expanded:\n      dnn: internet\n      dns-primary: 8.8.8.8\n      mtu: 1460\n      ue-dnn-qos:\n        bitrate-unit: bps\n        dnn-mbr-downlink: 200000000\n        dnn-mbr-uplink: 20000000\n        traffic-class:\n          arp: 6\n          name: platinum\n          pdb: 300\n          pelr: 6\n          qci: 9\n      ue-ip-pool: 172.250.1.0/16\n    ip-domain-name: pool1\n    name: 5g-gnbsim-user-group1\n    site-info: aiab\n  - imsis:\n    - "208930100007501"\n    - "208930100007502"\n    - "208930100007503"\n    - "208930100007504"\n    - "208930100007505"\n    - "208930100007506"\n    - "208930100007507"\n    - "208930100007508"\n    - "208930100007509"\n    - "208930100007510"\n    ip-domain-expanded:\n      dnn: internet\n      dns-primary: 8.8.8.8\n      mtu: 1460\n      ue-dnn-qos:\n        bitrate-unit: bps\n        dnn-mbr-downlink: 400000000\n        dnn-mbr-uplink: 10000000\n        traffic-class:\n          arp: 6\n          name: platinum\n          pdb: 300\n          pelr: 6\n          qci: 8\n      ue-ip-pool: 172.250.1.0/16\n    ip-domain-name: pool2\n    name: 5g-gnbsim-user-group2\n    site-info: aiab2\n  network-slices:\n  - application-filtering-rules:\n    - action: permit\n      endpoint: 0.0.0.0/0\n      priority: 250\n      rule-name: ALLOW-ALL\n    name: default\n    site-device-group:\n    - 5g-gnbsim-user-group1\n    - 5g-gnbsim-user-group2\n    site-info:\n      gNodeBs:\n      - name: aiab-gnb1\n        tac: 1\n      - name: aiab-gnb2\n        tac: 2\n      plmn:\n        mcc: "208"\n        mnc: "93"\n      site-name: aiab\n      upf:\n        upf-name: upf\n        upf-port: 8805\n    slice-id:\n      sd: "010203"\n      sst: 1\n  provision-network-slice: false\n  sub-provision-endpt:\n    addr: webui\n    port: 5000\n  subscribers:\n  - key: 5122250214c33e723a5dd523fc145fc0\n    op: ""\n    opc: 981d464c7c52eb6e5036234984ad0bcf\n    plmnId: "20893"\n    sequenceNumber: 16f3b3f70fc2\n    ueId-end: "208930100007500"\n    ueId-start: "208930100007487"\n  - key: 5122250214c33e723a5dd523fc145fc0\n    op: ""\n    opc: 981d464c7c52eb6e5036234984ad0bcf\n    plmnId: "20893"\n    sequenceNumber: 16f3b3f70fc2\n    ueId-end: "208930100007599"\n    ueId-start: "208930100007501"\ninfo:\n  description: SIMAPP initial local configuration\n  http-version: 1\n  version: 1.0.0\nlogger:\n  APP:\n    ReportCaller: false\n    debugLevel: info\n',  # noqa: E501
        )

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
            self.harness.model.unit.status,
            BlockedStatus(
                "Use `juju scp` to copy the config file to the unit and run the `configure-network` action"  # noqa: E501, W505
            ),
        )
