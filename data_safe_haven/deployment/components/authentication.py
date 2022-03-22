# Standard library imports
from typing import Optional

# Third party imports
from pulumi import ComponentResource, Input, Output, ResourceOptions
from pulumi_azure_native import containerinstance, dbforpostgresql, network, storage


class AuthenticationProps:
    """Properties for AuthenticationComponent"""

    def __init__(
        self,
        ip_address_container: Input[str],
        openldap_password: Input[str],
        resource_group_name: Input[str],
        root_dn: Input[str],
        storage_account_name: Input[str],
        storage_account_resource_group: Input[str],
        virtual_network_name: Input[str],
        virtual_network_resource_group: Input[str],
        subnet_name: Optional[Input[str]] = "OpenLDAPSubnet",
    ):
        self.ip_address_container = ip_address_container
        self.openldap_password = openldap_password
        self.resource_group_name = resource_group_name
        self.root_dn = root_dn
        self.storage_account_name = storage_account_name
        self.storage_account_resource_group = storage_account_resource_group
        self.subnet_name = subnet_name
        self.virtual_network_name = virtual_network_name
        self.virtual_network_resource_group = virtual_network_resource_group


class AuthenticationComponent(ComponentResource):
    """Deploy authentication with Pulumi"""

    def __init__(
        self, name: str, props: AuthenticationProps, opts: ResourceOptions = None
    ):
        super().__init__("dsh:authentication:AuthenticationComponent", name, {}, opts)
        child_opts = ResourceOptions(parent=self)

        # Retrieve existing resources
        snet_openldap = network.get_subnet(
            subnet_name=props.subnet_name,
            resource_group_name=props.virtual_network_resource_group,
            virtual_network_name=props.virtual_network_name,
        )
        storage_account_keys = storage.list_storage_account_keys(
            account_name=props.storage_account_name,
            resource_group_name=props.storage_account_resource_group,
        )

        # Define configuration file shares
        file_share_openldap_ldifs = storage.FileShare(
            "file_share_authentication_openldap_ldifs",
            access_tier="TransactionOptimized",
            account_name=props.storage_account_name,
            resource_group_name=props.storage_account_resource_group,
            share_name="authentication-openldap-ldifs",
            share_quota=1024,
            opts=child_opts,
        )
        file_share_openldap_scripts = storage.FileShare(
            "file_share_authentication_openldap_scripts",
            access_tier="TransactionOptimized",
            account_name=props.storage_account_name,
            resource_group_name=props.storage_account_resource_group,
            share_name="authentication-openldap-scripts",
            share_quota=1024,
            opts=child_opts,
        )

        # Define a network profile
        network_profile_authentication = network.NetworkProfile(
            "network_profile_authentication",
            container_network_interface_configurations=[
                network.ContainerNetworkInterfaceConfigurationArgs(
                    ip_configurations=[
                        network.IPConfigurationProfileArgs(
                            name="ipconfigauthentication",
                            subnet=network.SubnetArgs(
                                id=snet_openldap.id,
                            ),
                        )
                    ],
                    name="networkinterfaceconfigauthentication",
                )
            ],
            network_profile_name=f"np-{self._name}-authentication",
            resource_group_name=props.virtual_network_resource_group,
            opts=child_opts,
        )

        # Define the container group with guacd and openldap
        container_group = containerinstance.ContainerGroup(
            "container_group_authentication",
            container_group_name=f"container-{self._name}-authentication",
            containers=[
                containerinstance.ContainerArgs(
                    image="bitnami/openldap:latest",  # containers are tagged daily
                    name=f"container-{self._name}-authentication-openldap",
                    environment_variables=[
                        containerinstance.EnvironmentVariableArgs(
                            name="BITNAMI_DEBUG", value="true"
                        ),
                        containerinstance.EnvironmentVariableArgs(
                            name="LDAP_ADMIN_PASSWORD", secure_value=props.openldap_password
                        ),
                        containerinstance.EnvironmentVariableArgs(
                            name="LDAP_ADMIN_USERNAME", value="admin"
                        ),
                        containerinstance.EnvironmentVariableArgs(
                            name="LDAP_CUSTOM_LDIF_DIR", value="/opt/ldifs"
                        ),
                        containerinstance.EnvironmentVariableArgs(
                            name="LDAP_ENABLE_TLS", value="no"
                        ),
                        containerinstance.EnvironmentVariableArgs(
                            name="LDAP_LDAPS_PORT_NUMBER", value="1636"
                        ),
                        containerinstance.EnvironmentVariableArgs(
                            name="LDAP_PORT_NUMBER", value="1389"
                        ),
                        containerinstance.EnvironmentVariableArgs(
                            name="LDAP_ROOT", value=props.root_dn
                        ),
                    ],
                    ports=[
                        containerinstance.ContainerPortArgs(
                            port=1389,
                            protocol="TCP",
                        ),
                        containerinstance.ContainerPortArgs(
                            port=1636,
                            protocol="TCP",
                        ),
                    ],
                    resources=containerinstance.ResourceRequirementsArgs(
                        requests=containerinstance.ResourceRequestsArgs(
                            cpu=1,
                            memory_in_gb=1.5,
                        ),
                    ),
                    volume_mounts=[
                        containerinstance.VolumeMountArgs(
                            mount_path="/opt/ldifs",
                            name="authentication-openldap-ldifs",
                            read_only=False,
                        ),
                        containerinstance.VolumeMountArgs(
                            mount_path="/docker-entrypoint-initdb.d/",
                            name="authentication-openldap-scripts",
                            read_only=False,
                        ),
                    ],
                ),
                containerinstance.ContainerArgs(
                    image="osixia/phpldapadmin:0.9.0",
                    name=f"container-{self._name}-authentication-phpldapadmin",
                    environment_variables=[
                        containerinstance.EnvironmentVariableArgs(
                            name="CONTAINER_LOG_LEVEL",
                            value="5",
                        ),
                        containerinstance.EnvironmentVariableArgs(
                            name="PHPLDAPADMIN_HTTPS",
                            value="false",
                        ),
                        containerinstance.EnvironmentVariableArgs(
                            name="PHPLDAPADMIN_LDAP_HOSTS",
                            value="#PYTHON2BASH:[{'localhost': [{'server': [{'tls': False}, {'port': 1389}]}]}]",
                        ),
                        containerinstance.EnvironmentVariableArgs(
                            name="PHPLDAPADMIN_TRUST_PROXY_SSL",
                            value="true",
                        ),
                    ],
                    ports=[
                        containerinstance.ContainerPortArgs(
                            port=80,  # note this is not used but all container groups must expose port 80
                            protocol="TCP",
                        ),
                    ],
                    resources=containerinstance.ResourceRequirementsArgs(
                        requests=containerinstance.ResourceRequestsArgs(
                            cpu=1,
                            memory_in_gb=1.5,
                        ),
                    ),
                ),
            ],
            ip_address=containerinstance.IpAddressArgs(
                ip=props.ip_address_container,
                ports=[
                    containerinstance.PortArgs(
                        port=80,
                        protocol="TCP",
                    )
                ],
                type="Private",
            ),
            network_profile=containerinstance.ContainerGroupNetworkProfileArgs(
                id=network_profile_authentication.id,
            ),
            os_type="Linux",
            resource_group_name=props.resource_group_name,
            restart_policy="Always",
            sku="Standard",
            volumes=[
                containerinstance.VolumeArgs(
                    azure_file=containerinstance.AzureFileVolumeArgs(
                        share_name=file_share_openldap_ldifs.name,
                        storage_account_key=storage_account_keys.keys[0].value,
                        storage_account_name=props.storage_account_name,
                    ),
                    name="authentication-openldap-ldifs",
                ),
                containerinstance.VolumeArgs(
                    azure_file=containerinstance.AzureFileVolumeArgs(
                        share_name=file_share_openldap_scripts.name,
                        storage_account_key=storage_account_keys.keys[0].value,
                        storage_account_name=props.storage_account_name,
                    ),
                    name="authentication-openldap-scripts",
                ),
            ],
            opts=child_opts,
        )

        # Register outputs
        self.container_group_name = container_group.name
        self.file_share_openldap_ldifs_name = file_share_openldap_ldifs.name
        self.file_share_openldap_scripts_name = file_share_openldap_scripts.name
        self.private_ip_address = Output.from_input(props.ip_address_container)
        self.resource_group_name = Output.from_input(props.resource_group_name)
        self.subdomain = "authentication"
