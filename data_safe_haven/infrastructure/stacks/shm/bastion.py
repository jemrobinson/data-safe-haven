"""Pulumi component for SHM monitoring"""

from collections.abc import Mapping

from pulumi import ComponentResource, Input, Output, ResourceOptions
from pulumi_azure_native import network


class SHMBastionProps:
    """Properties for SHMBastionComponent"""

    def __init__(
        self,
        location: Input[str],
        resource_group_name: Input[str],
        subnet: Input[network.GetSubnetResult],
    ) -> None:
        # self.automation_account_name = automation_account_name
        self.location = location
        self.resource_group_name = resource_group_name
        self.subnet_id = Output.from_input(subnet).apply(lambda s: s.id if s.id else "")


class SHMBastionComponent(ComponentResource):
    """Deploy SHM bastion with Pulumi"""

    def __init__(
        self,
        name: str,
        stack_name: str,
        props: SHMBastionProps,
        opts: ResourceOptions | None = None,
        tags: Input[Mapping[str, Input[str]]] | None = None,
    ) -> None:
        super().__init__("dsh:shm:BastionComponent", name, {}, opts)
        child_opts = ResourceOptions.merge(opts, ResourceOptions(parent=self))
        child_tags = tags if tags else {}

        # Deploy IP address
        public_ip = network.PublicIPAddress(
            f"{self._name}_pip_bastion",
            public_ip_address_name=f"{stack_name}-pip-bastion",
            public_ip_allocation_method=network.IPAllocationMethod.STATIC,
            resource_group_name=props.resource_group_name,
            sku=network.PublicIPAddressSkuArgs(
                name=network.PublicIPAddressSkuName.STANDARD
            ),
            opts=child_opts,
            tags=child_tags,
        )

        # Deploy bastion host
        bastion_host = network.BastionHost(
            f"{self._name}_bastion_host",
            bastion_host_name=f"{stack_name}-bas",
            ip_configurations=[
                network.BastionHostIPConfigurationArgs(
                    public_ip_address=network.SubResourceArgs(id=public_ip.id),
                    subnet=network.SubResourceArgs(id=props.subnet_id),
                    name=f"{stack_name}-bas-ipcfg",
                    private_ip_allocation_method=network.IPAllocationMethod.DYNAMIC,
                )
            ],
            resource_group_name=props.resource_group_name,
            opts=child_opts,
            tags=child_tags,
        )

        # Register outputs
        self.bastion_host = bastion_host