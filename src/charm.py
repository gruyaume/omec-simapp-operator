#!/usr/bin/env python3
# Copyright 2022 Guillaume Belanger
# See LICENSE file for licensing details.

"""Charmed operator for the 5G SIMAPP service."""

import logging
from ipaddress import IPv4Address
from subprocess import check_output
from typing import Optional

from charms.observability_libs.v1.kubernetes_service_patch import KubernetesServicePatch
from lightkube.models.core_v1 import ServicePort
from ops.charm import ActionEvent, CharmBase, PebbleReadyEvent
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus
from ops.pebble import Layer

logger = logging.getLogger(__name__)

BASE_CONFIG_PATH = "/simapp/config"
CONFIG_FILE_NAME = "simapp.yaml"


class SIMAPPOperatorCharm(CharmBase):
    """Main class to describe juju event handling for the 5G SIMAPP operator."""

    def __init__(self, *args):
        super().__init__(*args)
        self._container_name = self._service_name = "simapp"
        self._container = self.unit.get_container(self._container_name)
        self.framework.observe(self.on.configure_network_action, self._on_configure_network_action)
        self.framework.observe(self.on.simapp_pebble_ready, self._on_simapp_pebble_ready)
        self._service_patcher = KubernetesServicePatch(
            charm=self,
            ports=[
                ServicePort(name="prometheus-exporter", port=9089),
                ServicePort(name="config-exporter", port=8080),
            ],
        )

    def _on_simapp_pebble_ready(self, event: PebbleReadyEvent) -> None:
        if not self._config_file_is_written:
            self.unit.status = BlockedStatus("Waiting for config file to be written")
            return

    @property
    def _config_file_is_written(self) -> bool:
        if not self._container.exists(f"{BASE_CONFIG_PATH}/{CONFIG_FILE_NAME}"):
            logger.info(f"Config file is not written: {CONFIG_FILE_NAME}")
            return False
        logger.info("Config file is written")
        return True

    def _on_configure_network_action(self, event: ActionEvent) -> None:
        if not self._container.can_connect():
            event.fail(message="Container is not ready")
            return
        if not self._config_file_is_written:
            event.fail(message="Config file is not written")
            return
        self._container.add_layer("simapp", self._pebble_layer, combine=True)
        self._container.replan()
        self.unit.status = ActiveStatus()

    @property
    def _pebble_layer(self) -> Layer:
        """Returns pebble layer for the charm.

        Returns:
            Layer: Pebble Layer
        """
        return Layer(
            {
                "summary": "simapp layer",
                "description": "pebble config layer for simapp",
                "services": {
                    "simapp": {
                        "override": "replace",
                        "startup": "enabled",
                        "command": "/simapp/bin/simapp",
                        "environment": self._environment_variables,
                    },
                },
            }
        )

    @property
    def _environment_variables(self) -> dict:
        return {
            "POD_IP": str(self._pod_ip),
        }

    @property
    def _pod_ip(self) -> Optional[IPv4Address]:
        """Get the IP address of the Kubernetes pod."""
        return IPv4Address(check_output(["unit-get", "private-address"]).decode().strip())


if __name__ == "__main__":
    main(SIMAPPOperatorCharm)
