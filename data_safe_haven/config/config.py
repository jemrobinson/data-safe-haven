"""Configuration file backed by blob storage"""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import (
    BaseModel,
    Field,
)

from data_safe_haven.functions import sanitise_sre_name
from data_safe_haven.serialisers import AzureSerialisableModel, ContextBase
from data_safe_haven.types import (
    AzureVmSku,
    DatabaseSystem,
    EmailAddress,
    Fqdn,
    Guid,
    IpAddress,
    SoftwarePackageCategory,
    TimeZone,
    UniqueList,
)
from data_safe_haven.utility import (
    LoggingSingleton,
)


class ConfigSectionAzure(BaseModel, validate_assignment=True):
    subscription_id: Guid
    tenant_id: Guid


class ConfigSectionSHM(BaseModel, validate_assignment=True):
    entra_tenant_id: Guid
    fqdn: Fqdn

    def update(
        self,
        *,
        entra_tenant_id: str | None = None,
        fqdn: str | None = None,
    ) -> None:
        """Update SHM settings

        Args:
            entra_tenant_id: Entra ID tenant containing users
            fqdn: Fully-qualified domain name to use for this SHM
        """
        logger = LoggingSingleton()
        # Set Entra tenant ID
        if entra_tenant_id:
            self.entra_tenant_id = entra_tenant_id
        logger.info(
            f"[bold]Entra tenant ID[/] will be [green]{self.entra_tenant_id}[/]."
        )
        # Set fully-qualified domain name
        if fqdn:
            self.fqdn = fqdn
        logger.info(
            f"[bold]Fully-qualified domain name[/] will be [green]{self.fqdn}[/]."
        )


class ConfigSubsectionRemoteDesktopOpts(BaseModel, validate_assignment=True):
    allow_copy: bool = False
    allow_paste: bool = False

    def update(
        self, *, allow_copy: bool | None = None, allow_paste: bool | None = None
    ) -> None:
        """Update SRE remote desktop settings

        Args:
            allow_copy: Allow/deny copying text out of the SRE
            allow_paste: Allow/deny pasting text into the SRE
        """
        # Set whether copying text out of the SRE is allowed
        if allow_copy:
            self.allow_copy = allow_copy
        LoggingSingleton().info(
            f"[bold]Copying text out of the SRE[/] will be [green]{'allowed' if self.allow_copy else 'forbidden'}[/]."
        )
        # Set whether pasting text into the SRE is allowed
        if allow_paste:
            self.allow_paste = allow_paste
        LoggingSingleton().info(
            f"[bold]Pasting text into the SRE[/] will be [green]{'allowed' if self.allow_paste else 'forbidden'}[/]."
        )


class ConfigSectionSRE(BaseModel, validate_assignment=True):
    admin_email_address: EmailAddress
    admin_ip_addresses: list[IpAddress] = Field(..., default_factory=list[IpAddress])
    databases: UniqueList[DatabaseSystem] = Field(
        ..., default_factory=list[DatabaseSystem]
    )
    data_provider_ip_addresses: list[IpAddress] = Field(
        ..., default_factory=list[IpAddress]
    )
    remote_desktop: ConfigSubsectionRemoteDesktopOpts = Field(
        ..., default_factory=ConfigSubsectionRemoteDesktopOpts
    )
    research_user_ip_addresses: list[IpAddress] = Field(
        ..., default_factory=list[IpAddress]
    )
    software_packages: SoftwarePackageCategory = SoftwarePackageCategory.NONE
    timezone: TimeZone = "Etc/UTC"
    workspace_skus: list[AzureVmSku] = Field(..., default_factory=list[AzureVmSku])

    def update(
        self,
        *,
        admin_email_address: str | None = None,
        admin_ip_addresses: list[str] | None = None,
        data_provider_ip_addresses: list[IpAddress] | None = None,
        databases: list[DatabaseSystem] | None = None,
        software_packages: SoftwarePackageCategory | None = None,
        timezone: TimeZone | None = None,
        user_ip_addresses: list[IpAddress] | None = None,
        workspace_skus: list[AzureVmSku] | None = None,
    ) -> None:
        """Update SRE settings

        Args:
            admin_email_address: Email address shared by all administrators
            admin_ip_addresses: List of IP addresses belonging to administrators
            databases: List of database systems to deploy
            data_provider_ip_addresses: List of IP addresses belonging to data providers
            software_packages: Whether to allow packages from external repositories
            timezone: Timezone in pytz format (eg. Europe/London)
            user_ip_addresses: List of IP addresses belonging to users
            workspace_skus: List of VM SKUs for workspaces
        """
        logger = LoggingSingleton()
        # Set admin email address
        if admin_email_address:
            self.admin_email_address = admin_email_address
        logger.info(
            f"[bold]Admin email address[/] will be [green]{self.admin_email_address}[/]."
        )
        # Set admin IP addresses
        if admin_ip_addresses:
            self.admin_ip_addresses = admin_ip_addresses
        logger.info(
            f"[bold]IP addresses used by administrators[/] will be [green]{self.admin_ip_addresses}[/]."
        )
        # Set data provider IP addresses
        if data_provider_ip_addresses:
            self.data_provider_ip_addresses = data_provider_ip_addresses
        logger.info(
            f"[bold]IP addresses used by data providers[/] will be [green]{self.data_provider_ip_addresses}[/]."
        )
        # Set which databases to deploy
        if databases:
            self.databases = sorted(set(databases))
            if len(self.databases) != len(databases):
                logger.warning("Discarding duplicate values for 'database'.")
        logger.info(
            f"[bold]Databases available to users[/] will be [green]{[database.value for database in self.databases]}[/]."
        )
        # Select which software packages can be installed by users
        if software_packages:
            self.software_packages = software_packages
        logger.info(
            f"[bold]Software packages[/] from [green]{self.software_packages.value}[/] sources will be installable."
        )
        # Set timezone
        if timezone:
            self.timezone = timezone
        logger.info(f"[bold]Timezone[/] will be [green]{self.timezone}[/].")
        # Set user IP addresses
        if user_ip_addresses:
            self.research_user_ip_addresses = user_ip_addresses
        logger.info(
            f"[bold]IP addresses used by users[/] will be [green]{self.research_user_ip_addresses}[/]."
        )
        # Set workspace desktop SKUs
        if workspace_skus:
            self.workspace_skus = workspace_skus
        logger.info(f"[bold]Workspace SKUs[/] will be [green]{self.workspace_skus}[/].")


class SHMConfig(AzureSerialisableModel):
    config_type: ClassVar[str] = "SHMConfig"
    filename: ClassVar[str] = "shm.yaml"
    azure: ConfigSectionAzure
    shm: ConfigSectionSHM

    def is_complete(self) -> bool:
        if not all((self.azure, self.shm)):
            return False
        return True

    @classmethod
    def template(cls: type[Self]) -> SHMConfig:
        """Create object without validation to allow "replace me" prompts."""
        return SHMConfig.model_construct(
            azure=ConfigSectionAzure.model_construct(
                subscription_id="Azure subscription ID",
                tenant_id="Azure tenant ID",
            ),
            shm=ConfigSectionSHM.model_construct(
                entra_tenant_id="Entra tenant ID",
                fqdn="TRE domain name",
            ),
        )


class Config(AzureSerialisableModel):
    config_type: ClassVar[str] = "Config"
    filename: ClassVar[str] = "config.yaml"
    azure: ConfigSectionAzure
    shm: ConfigSectionSHM
    sre: ConfigSectionSRE

    def is_complete(self) -> bool:
        if not all((self.azure, self.shm, self.sre)):
            return False
        return True

    @classmethod
    def sre_from_remote(cls: type[Self], context: ContextBase, sre_name: str) -> Self:
        """Load a Config from Azure storage."""
        return cls.from_remote(context, filename=cls.sre_filename_from_name(sre_name))

    @classmethod
    def sre_filename_from_name(cls: type[Self], sre_name: str) -> str:
        """Construct a canonical filename."""
        return f"sre-{sanitise_sre_name(sre_name)}.yaml"

    @classmethod
    def template(cls) -> Config:
        """Create object without validation to allow "replace me" prompts."""
        return Config.model_construct(
            azure=ConfigSectionAzure.model_construct(
                subscription_id="Azure subscription ID",
                tenant_id="Azure tenant ID",
            ),
            shm=ConfigSectionSHM.model_construct(
                admin_ip_addresses=["Admin IP addresses"],
                entra_tenant_id="Entra tenant ID",
                fqdn="TRE domain name",
                timezone="Timezone",
            ),
            sre=ConfigSectionSRE.model_construct(
                admin_email_address="Admin email address",
                databases=["List of database systems to enable"],
                data_provider_ip_addresses=["Data provider IP addresses"],
                remote_desktop=ConfigSubsectionRemoteDesktopOpts.model_construct(
                    allow_copy="Whether to allow copying text out of the environment",
                    allow_paste="Whether to allow pasting text into the environment",
                ),
                workspace_skus=[
                    "Azure VM SKUs - see cloudprice.net for list of valid SKUs"
                ],
                research_user_ip_addresses=["Research user IP addresses"],
                software_packages=SoftwarePackageCategory.ANY,
            ),
        )
