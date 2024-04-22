"""Pulumi component for SRE traffic filtering"""

from collections.abc import Mapping

from pulumi import ComponentResource, Input, ResourceOptions
from pulumi_azure_native import containerinstance, network, resources

from data_safe_haven.infrastructure.common import (
    get_id_from_subnet,
)


class SRETrafficFilterProps:
    """Properties for SRETrafficFilterComponent"""

    def __init__(
        self,
        location: Input[str],
        subnet: Input[network.GetSubnetResult],
    ) -> None:
        self.location = location
        self.subnet_id = subnet.apply(get_id_from_subnet)


class SRETrafficFilterComponent(ComponentResource):
    """Deploy SRE traffic filter with Pulumi"""

    def __init__(
        self,
        name: str,
        stack_name: str,
        props: SRETrafficFilterProps,
        opts: ResourceOptions | None = None,
        tags: Input[Mapping[str, Input[str]]] | None = None,
    ) -> None:
        super().__init__("dsh:sre:TrafficFilterComponent", name, {}, opts)
        child_opts = ResourceOptions.merge(opts, ResourceOptions(parent=self))
        child_tags = tags if tags else {}

        # Deploy resource group
        resource_group = resources.ResourceGroup(
            f"{self._name}_resource_group",
            location=props.location,
            resource_group_name=f"{stack_name}-rg-traffic-filter",
            opts=child_opts,
            tags=child_tags,
        )

        # Define a container group with Squid
        containerinstance.ContainerGroup(
            f"{self._name}_container_group_traffic_filter",
            container_group_name=f"{stack_name}-container-group-traffic-filter",
            containers=[
                containerinstance.ContainerArgs(
                    image="ubuntu/squid:6.1-23.10_beta",
                    name="squid"[:63],
                    ports=[
                        containerinstance.ContainerPortArgs(
                            port=80,
                            protocol=containerinstance.ContainerNetworkProtocol.TCP,
                        )
                    ],
                    resources=containerinstance.ResourceRequirementsArgs(
                        requests=containerinstance.ResourceRequestsArgs(
                            cpu=0.5,
                            memory_in_gb=0.5,
                        ),
                    ),
                ),
            ],
            ip_address=containerinstance.IpAddressArgs(
                ports=[
                    containerinstance.PortArgs(
                        port=80,
                        protocol=containerinstance.ContainerGroupNetworkProtocol.TCP,
                    )
                ],
                type=containerinstance.ContainerGroupIpAddressType.PRIVATE,
            ),
            os_type=containerinstance.OperatingSystemTypes.LINUX,
            resource_group_name=resource_group.name,
            restart_policy=containerinstance.ContainerGroupRestartPolicy.ALWAYS,
            sku=containerinstance.ContainerGroupSku.STANDARD,
            subnet_ids=[
                containerinstance.ContainerGroupSubnetIdArgs(id=props.subnet_id)
            ],
            volumes=[],
            opts=ResourceOptions.merge(
                child_opts,
                ResourceOptions(
                    delete_before_replace=True, replace_on_changes=["containers"]
                ),
            ),
            tags=child_tags,
        )
