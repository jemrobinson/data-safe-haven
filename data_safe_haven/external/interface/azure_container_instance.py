"""Backend for a Data Safe Haven environment"""
# Standard library imports
import contextlib
import time
from typing import Optional

# Third party imports
import websocket
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (
    ContainerExecRequest,
    ContainerExecRequestTerminalSize,
)

# Local imports
from data_safe_haven.mixins import AzureMixin, LoggingMixin


class AzureContainerInstance(AzureMixin, LoggingMixin):
    """Interface for Azure container instances."""

    def __init__(
        self,
        container_group_name: str,
        resource_group_name: str,
        subscription_name: str,
    ):
        super().__init__(subscription_name=subscription_name)
        self.resource_group_name = resource_group_name
        self.container_group_name = container_group_name

    @staticmethod
    def wait(poller):
        while not poller.done():
            time.sleep(10)

    def restart(self, target_ip_address: Optional[str] = None):
        """Restart the container group"""
        # Connect to Azure clients
        aci_client = ContainerInstanceManagementClient(
            self.credential, self.subscription_id
        )
        if not target_ip_address:
            target_ip_address = aci_client.container_groups.get(
                self.resource_group_name, self.container_group_name
            ).ip_address.ip

        # Restart container group
        self.info(
            f"Restarting container group <fg=green>{self.container_group_name}</>...",
            no_newline=True,
        )
        while True:
            self.wait(
                aci_client.container_groups.begin_restart(
                    self.resource_group_name, self.container_group_name
                )
            )
            final_ip_address = aci_client.container_groups.get(
                self.resource_group_name, self.container_group_name
            ).ip_address.ip
            if final_ip_address == target_ip_address:
                break
        self.info(
            f"Restarted container group <fg=green>{self.container_group_name}</>.",
            overwrite=True,
        )

    def run_executable(self, container_name, executable_path):
        """
        Run a script or command on one of the containers.

        The command cannot take any arguments and must be a single expression.
        The most likely use-case is running a script already present in the container.
        """
        # Connect to Azure clients
        aci_client = ContainerInstanceManagementClient(
            self.credential, self.subscription_id
        )

        # Run command
        cnxn = aci_client.containers.execute_command(
            self.resource_group_name,
            self.container_group_name,
            container_name,
            ContainerExecRequest(
                command=executable_path,
                terminal_size=ContainerExecRequestTerminalSize(cols=80, rows=500),
            ),
        )

        # Get command output via websocket
        socket = websocket.create_connection(cnxn.web_socket_uri)
        socket.send(cnxn.password)
        output = []
        with contextlib.suppress(websocket.WebSocketConnectionClosedException):
            while result := socket.recv():
                for line in [line.strip() for line in result.splitlines()]:
                    output.append(line)
            socket.close()
        return output
