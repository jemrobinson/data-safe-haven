"""Pulumi component for SRE traffic filtering"""

from collections.abc import Mapping

from pulumi import ComponentResource, Input, Output, ResourceOptions
from pulumi_azure_native import containerinstance, network, resources, storage

from data_safe_haven.infrastructure.common import (
    SREIpRanges,
    get_id_from_subnet,
    get_ip_address_from_container_group,
)
from data_safe_haven.infrastructure.components import (
    FileShareFile,
    FileShareFileProps,
)
from data_safe_haven.resources import resources_path
from data_safe_haven.utility import FileReader


class SRETrafficFilterProps:
    """Properties for SRETrafficFilterComponent"""

    def __init__(
        self,
        location: Input[str],
        route_table_name: Input[str],
        route_table_resource_group_name: Input[str],
        sre_index: Input[int],
        storage_account_key: Input[str],
        storage_account_name: Input[str],
        storage_account_resource_group_name: Input[str],
        subnet: Input[network.GetSubnetResult],
    ) -> None:
        subnet_ranges = Output.from_input(sre_index).apply(lambda idx: SREIpRanges(idx))
        self.location = location
        self.route_table_name = route_table_name
        self.route_table_resource_group_name = route_table_resource_group_name
        self.storage_account_key = storage_account_key
        self.storage_account_name = storage_account_name
        self.storage_account_resource_group_name = storage_account_resource_group_name
        self.subnet_id = subnet.apply(get_id_from_subnet)
        self.iprange_all = subnet_ranges.apply(lambda s: s.vnet)


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

        # Define configuration file share
        file_share = storage.FileShare(
            f"{self._name}_file_share",
            access_tier="TransactionOptimized",
            account_name=props.storage_account_name,
            resource_group_name=props.storage_account_resource_group_name,
            share_name="traffic-filter-squid",
            share_quota=1,
            signed_identifiers=[],
            opts=child_opts,
        )

        # Overwrite Squid config file
        squid_conf_reader = FileReader(
            resources_path / "traffic_filter" / "squid.mustache.conf"
        )
        FileShareFile(
            f"{self._name}_file_share_squid_conf",
            FileShareFileProps(
                destination_path=squid_conf_reader.name,
                file_contents=Output.all(
                    iprange_all=props.iprange_all,
                ).apply(
                    lambda mustache_values: squid_conf_reader.file_contents(
                        mustache_values
                    )
                ),
                share_name=file_share.name,
                storage_account_key=props.storage_account_key,
                storage_account_name=props.storage_account_name,
            ),
            opts=ResourceOptions.merge(child_opts, ResourceOptions(parent=file_share)),
        )

        # Upload Squid allowlists
        sre_all_allowlist_reader = FileReader(
            resources_path / "traffic_filter" / "sre_all.allowlist"
        )
        FileShareFile(
            f"{self._name}_file_share_sre_all_allowlist",
            FileShareFileProps(
                destination_path=sre_all_allowlist_reader.name,
                file_contents=sre_all_allowlist_reader.file_contents(),
                share_name=file_share.name,
                storage_account_key=props.storage_account_key,
                storage_account_name=props.storage_account_name,
            ),
            opts=ResourceOptions.merge(child_opts, ResourceOptions(parent=file_share)),
        )

        # Define a container group with Squid
        container_group = containerinstance.ContainerGroup(
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
                            cpu=1,
                            memory_in_gb=1,
                        ),
                    ),
                    volume_mounts=[
                        containerinstance.VolumeMountArgs(
                            mount_path="/etc/squid/",
                            name="squid-etc-squid-custom",
                            read_only=True,
                        ),
                    ],
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
            volumes=[
                containerinstance.VolumeArgs(
                    azure_file=containerinstance.AzureFileVolumeArgs(
                        share_name=file_share.name,
                        storage_account_key=props.storage_account_key,
                        storage_account_name=props.storage_account_name,
                    ),
                    name="squid-etc-squid-custom",
                ),
            ],
            opts=ResourceOptions.merge(
                child_opts,
                ResourceOptions(
                    delete_before_replace=True, replace_on_changes=["containers"]
                ),
            ),
            tags=child_tags,
        )

        # Define a route via the traffic filter
        network.Route(
            f"{self._name}_route",
            address_prefix="0.0.0.0/0",
            # name="ViaTrafficFilter_name",
            next_hop_ip_address=get_ip_address_from_container_group(container_group),
            next_hop_type=network.RouteNextHopType.VIRTUAL_APPLIANCE,
            resource_group_name=props.route_table_resource_group_name,
            route_name="ViaTrafficFilter",
            route_table_name=props.route_table_name,
            opts=child_opts,
        )
