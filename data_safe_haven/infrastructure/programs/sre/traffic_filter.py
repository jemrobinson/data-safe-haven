"""Pulumi component for SRE traffic filtering"""

from collections.abc import Mapping

from pulumi import ComponentResource, Input, ResourceOptions
from pulumi_azure_native import resources


class SRETrafficFilterProps:
    """Properties for SRETrafficFilterComponent"""

    def __init__(
        self,
        location: Input[str],
    ) -> None:
        self.location = location


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
        resources.ResourceGroup(
            f"{self._name}_resource_group",
            location=props.location,
            resource_group_name=f"{stack_name}-rg-traffic-filter",
            opts=child_opts,
            tags=child_tags,
        )
