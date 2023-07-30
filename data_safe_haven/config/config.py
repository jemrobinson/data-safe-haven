"""Configuration file backed by blob storage"""
import pathlib
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any

import chili
import yaml
from yaml.parser import ParserError

from data_safe_haven import __version__
from data_safe_haven.exceptions import DataSafeHavenAzureError
from data_safe_haven.external import AzureApi
from data_safe_haven.functions import (
    alphanumeric,
    as_dict,
    b64decode,
    b64encode,
    validate_aad_guid,
    validate_azure_location,
    validate_azure_vm_sku,
    validate_email_address,
    validate_ip_address,
    validate_timezone,
)
from data_safe_haven.utility import (
    DecoderTypeChecked,
    EncoderTypeChecked,
    LoggingSingleton,
    SoftwarePackageCategory,
    TypeChecked,
)

from .backend_settings import BackendSettings

decoders: dict[Any, chili.TypeDecoder] = {
    list[TypeChecked[str]]: DecoderTypeChecked[list[str]](),
    TypeChecked[bool]: DecoderTypeChecked[bool](),
    TypeChecked[int]: DecoderTypeChecked[int](),
    TypeChecked[str]: DecoderTypeChecked[str](),
}

encoders: dict[Any, chili.TypeEncoder] = {
    list[TypeChecked[str]]: EncoderTypeChecked[list[str]](),
    TypeChecked[bool]: EncoderTypeChecked[bool](),
    TypeChecked[int]: EncoderTypeChecked[int](),
    TypeChecked[str]: EncoderTypeChecked[str](),
}


@dataclass
class ConfigSectionAzure:
    admin_group_id: TypeChecked[str] = TypeChecked[str]()
    location: TypeChecked[str] = TypeChecked[str]()
    subscription_id: TypeChecked[str] = TypeChecked[str]()
    tenant_id: TypeChecked[str] = TypeChecked[str]()

    def to_dict(self) -> dict[str, str]:
        self.validate()
        return as_dict(chili.encode(self, encoders=encoders))

    def validate(self) -> None:
        """Validate input parameters"""
        try:
            validate_aad_guid(str(self.admin_group_id))
        except Exception as exc:
            msg = f"Invalid value for 'admin_group_id' ({self.admin_group_id}).\n{exc}"
            raise ValueError(msg) from exc
        try:
            validate_azure_location(str(self.location))
        except Exception as exc:
            msg = f"Invalid value for 'location' ({self.location}).\n{exc}"
            raise ValueError(msg) from exc
        try:
            validate_aad_guid(str(self.subscription_id))
        except Exception as exc:
            msg = (
                f"Invalid value for 'subscription_id' ({self.subscription_id}).\n{exc}"
            )
            raise ValueError(msg) from exc
        try:
            validate_aad_guid(str(self.tenant_id))
        except Exception as exc:
            msg = f"Invalid value for 'tenant_id' ({self.tenant_id}).\n{exc}"
            raise ValueError(msg) from exc


@dataclass
class ConfigSectionBackend:
    key_vault_name: TypeChecked[str] = TypeChecked[str]()
    managed_identity_name: TypeChecked[str] = TypeChecked[str]()
    resource_group_name: TypeChecked[str] = TypeChecked[str]()
    storage_account_name: TypeChecked[str] = TypeChecked[str]()
    storage_container_name: TypeChecked[str] = TypeChecked[str]()

    def to_dict(self) -> dict[str, str]:
        self.validate()
        return as_dict(chili.encode(self, encoders=encoders))

    def validate(self) -> None:
        """Validate input parameters"""
        if not self.key_vault_name:
            msg = f"Invalid value for 'key_vault_name' ({self.key_vault_name})."
            raise ValueError(msg)
        if not self.managed_identity_name:
            msg = f"Invalid value for 'managed_identity_name' ({self.managed_identity_name})."
            raise ValueError(msg)
        if not self.resource_group_name:
            msg = (
                f"Invalid value for 'resource_group_name' ({self.resource_group_name})."
            )
            raise ValueError(msg)
        if not self.storage_account_name:
            msg = f"Invalid value for 'storage_account_name' ({self.storage_account_name})."
            raise ValueError(msg)
        if not self.storage_container_name:
            msg = f"Invalid value for 'storage_container_name' ({self.storage_container_name})."
            raise ValueError(msg)


@dataclass
class ConfigSectionPulumi:
    encryption_key_id: TypeChecked[str] = TypeChecked[str]()
    encryption_key_name: TypeChecked[str] = TypeChecked[str](
        default="pulumi-encryption-key"
    )
    stacks: dict[str, str] = field(default_factory=dict)
    storage_container_name: TypeChecked[str] = TypeChecked[str](default="pulumi")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return as_dict(chili.encode(self, encoders=encoders))

    def validate(self) -> None:
        """Validate input parameters"""
        if not isinstance(self.encryption_key_id, str) or not self.encryption_key_id:
            msg = f"Invalid value for 'encryption_key_id' ({self.encryption_key_id})."
            raise ValueError(msg)


@dataclass
class ConfigSectionSHM:
    aad_tenant_id: TypeChecked[str] = TypeChecked[str]()
    admin_email_address: TypeChecked[str] = TypeChecked[str]()
    admin_ip_addresses: list[TypeChecked[str]] = field(default_factory=list)
    fqdn: TypeChecked[str] = TypeChecked[str]()
    name: TypeChecked[str] = TypeChecked[str]()
    timezone: TypeChecked[str] = TypeChecked[str]()

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return as_dict(chili.encode(self, encoders=encoders))

    def validate(self) -> None:
        """Validate input parameters"""
        try:
            validate_aad_guid(str(self.aad_tenant_id))
        except Exception as exc:
            msg = f"Invalid value for 'aad_tenant_id' ({self.aad_tenant_id}).\n{exc}"
            raise ValueError(msg) from exc
        try:
            validate_email_address(str(self.admin_email_address))
        except Exception as exc:
            msg = f"Invalid value for 'admin_email_address' ({self.admin_email_address}).\n{exc}"
            raise ValueError(msg) from exc
        try:
            for ip in self.admin_ip_addresses:
                validate_ip_address(str(ip))
        except Exception as exc:
            msg = f"Invalid value for 'admin_ip_addresses' ({self.admin_ip_addresses}).\n{exc}"
            raise ValueError(msg) from exc
        if not isinstance(self.fqdn, str) or not self.fqdn:
            msg = f"Invalid value for 'fqdn' ({self.fqdn})."
            raise ValueError(msg)
        if not isinstance(self.name, str) or not self.name:
            msg = f"Invalid value for 'name' ({self.name})."
            raise ValueError(msg)
        try:
            validate_timezone(str(self.timezone))
        except Exception as exc:
            msg = f"Invalid value for 'timezone' ({self.timezone}).\n{exc}"
            raise ValueError(msg) from exc


@dataclass
class ConfigSubsectionRemoteDesktopOpts:
    allow_copy: TypeChecked[bool] = TypeChecked[bool]()
    allow_paste: TypeChecked[bool] = TypeChecked[bool]()

    def summarise(self) -> None:
        """Log a summary of this object"""
        # State whether copying text out of the SRE is allowed
        logger = LoggingSingleton()
        logger.info(
            f"[bold]Copying text out of the SRE[/] will be [green]{'allowed' if self.allow_copy else 'forbidden'}[/]."
        )
        # State whether pasting text into the SRE is allowed
        logger.info(
            f"[bold]Pasting text into the SRE[/] will be [green]{'allowed' if self.allow_paste else 'forbidden'}[/]."
        )

    def validate(self) -> None:
        """Validate input parameters"""
        if not isinstance(self.allow_copy, bool):
            msg = f"Invalid value for 'allow_copy' ({self.allow_copy})."
            raise ValueError(msg)
        if not isinstance(self.allow_paste, bool):
            msg = f"Invalid value for 'allow_paste' ({self.allow_paste})."
            raise ValueError(msg)


@dataclass
class ConfigSubsectionResearchDesktopOpts:
    sku: str = ""

    def summarise(self) -> None:
        """Log a summary of this object"""
        LoggingSingleton().info(
            f"[bold]Copying text out of the SRE[/] will be [green]{'allowed' if self.sku else 'forbidden'}[/]."
        )

    def validate(self) -> None:
        """Validate input parameters"""
        try:
            validate_azure_vm_sku(str(self.sku))
        except Exception as exc:
            msg = f"Invalid value for 'sku' ({self.sku}).\n{exc}"
            raise ValueError(msg) from exc


@dataclass
class ConfigSectionSRE:
    data_provider_ip_addresses: list[TypeChecked[str]] = field(default_factory=list)
    index: TypeChecked[int] = TypeChecked[int](default=0)
    remote_desktop: ConfigSubsectionRemoteDesktopOpts = field(
        default_factory=ConfigSubsectionRemoteDesktopOpts
    )
    # NB. Unless our Python version has https://github.com/python/cpython/pull/32056
    # included, we cannot use defaultdict here.
    research_desktops: dict[str, ConfigSubsectionResearchDesktopOpts] = field(
        default_factory=dict
    )
    research_user_ip_addresses: list[TypeChecked[str]] = field(default_factory=list)
    software_packages: SoftwarePackageCategory = SoftwarePackageCategory.NONE

    def set_research_desktops(self, research_desktops: list[str]) -> None:
        if sorted(research_desktops) != sorted(self.research_desktops.keys()):
            self.research_desktops.clear()
            for idx, vm_sku in enumerate(research_desktops):
                self.research_desktops[
                    f"workspace-{idx:02d}"
                ] = ConfigSubsectionResearchDesktopOpts(sku=vm_sku)

    def summarise(self) -> None:
        """Log a summary of this object"""
        logger = LoggingSingleton()
        # Set data provider IP addresses
        logger.info(
            f"[bold]IP addresses used by data providers[/] will be [green]{self.data_provider_ip_addresses}[/]."
        )
        # Get remote_desktop to self-summarise
        self.remote_desktop.summarise()
        # Get list of research desktop SKUs
        LoggingSingleton().info(
            f"[bold]Research desktops[/] will be [green]{[v.sku for v in self.research_desktops.values()]}[/]."
        )
        # Select which software packages can be installed by users
        LoggingSingleton().info(
            f"[bold]Software packages[/] from [green]{self.software_packages}[/] sources will be installable."
        )
        # Set user IP addresses
        LoggingSingleton().info(
            f"[bold]IP addresses used by users[/] will be [green]{self.research_user_ip_addresses}[/]."
        )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return as_dict(chili.encode(self, encoders=encoders))

    def validate(self) -> None:
        """Validate input parameters"""
        try:
            for ip in self.data_provider_ip_addresses:
                validate_ip_address(str(ip))
        except Exception as exc:
            msg = f"Invalid value for 'data_provider_ip_addresses' ({self.data_provider_ip_addresses}).\n{exc}"
            raise ValueError(msg) from exc
        self.remote_desktop.validate()
        for research_desktop in self.research_desktops.values():
            research_desktop.validate()
        try:
            for ip in self.research_user_ip_addresses:
                validate_ip_address(str(ip))
        except Exception as exc:
            msg = f"Invalid value for 'research_user_ip_addresses' ({self.research_user_ip_addresses}).\n{exc}"
            raise ValueError(msg) from exc


@dataclass
class ConfigSectionTags:
    deployment: str = ""
    deployed_by: str = "Python"
    project: str = "Data Safe Haven"
    version: str = __version__

    def to_dict(self) -> dict[str, str]:
        self.validate()
        return as_dict(chili.encode(self))

    def validate(self) -> None:
        """Validate input parameters"""
        if not self.deployment:
            msg = f"Invalid value for 'deployment' ({self.deployment})."
            raise ValueError(msg)


class Config:
    def __init__(self) -> None:
        # Initialise config sections
        self.azure_: ConfigSectionAzure | None = None
        self.backend_: ConfigSectionBackend | None = None
        self.pulumi_: ConfigSectionPulumi | None = None
        self.shm_: ConfigSectionSHM | None = None
        self.tags_: ConfigSectionTags | None = None
        self.sres: dict[str, ConfigSectionSRE] = defaultdict(ConfigSectionSRE)
        # Read backend settings
        settings = BackendSettings()
        self.name = settings.name
        self.subscription_name = settings.subscription_name
        self.azure.location = settings.location
        self.azure.admin_group_id = settings.admin_group_id
        self.backend_storage_container_name = "config"
        # Set derived names
        self.shm_name_ = alphanumeric(self.name).lower()
        self.filename = f"config-{self.shm_name_}.yaml"
        self.backend_resource_group_name = f"shm-{self.shm_name_}-rg-backend"
        self.backend_storage_account_name = (
            f"shm{self.shm_name_[:14]}backend"  # maximum of 24 characters allowed
        )
        self.work_directory = settings.config_directory / self.shm_name_
        self.azure_api = AzureApi(subscription_name=self.subscription_name)
        # Attempt to load YAML dictionary from blob storage
        yaml_input = {}
        with suppress(DataSafeHavenAzureError, ParserError):
            yaml_input = yaml.safe_load(
                self.azure_api.download_blob(
                    self.filename,
                    self.backend_resource_group_name,
                    self.backend_storage_account_name,
                    self.backend_storage_container_name,
                )
            )
        # Attempt to decode each config section
        if yaml_input:
            if "azure" in yaml_input:
                self.azure_ = chili.decode(
                    yaml_input["azure"], ConfigSectionAzure, decoders=decoders
                )
            if "backend" in yaml_input:
                self.backend_ = chili.decode(
                    yaml_input["backend"], ConfigSectionBackend, decoders=decoders
                )
            if "pulumi" in yaml_input:
                self.pulumi_ = chili.decode(
                    yaml_input["pulumi"], ConfigSectionPulumi, decoders=decoders
                )
            if "shm" in yaml_input:
                self.shm_ = chili.decode(
                    yaml_input["shm"], ConfigSectionSHM, decoders=decoders
                )
            if "sre" in yaml_input:
                for sre_name, sre_details in dict(yaml_input["sre"]).items():
                    self.sres[sre_name] = chili.decode(
                        sre_details,
                        ConfigSectionSRE,
                        decoders=decoders,
                    )

    @property
    def azure(self) -> ConfigSectionAzure:
        if not self.azure_:
            self.azure_ = ConfigSectionAzure()
        return self.azure_

    @property
    def backend(self) -> ConfigSectionBackend:
        if not self.backend_:
            self.backend_ = ConfigSectionBackend(
                key_vault_name=f"shm-{self.shm_name_[:9]}-kv-backend",
                managed_identity_name=f"shm-{self.shm_name_}-identity-reader-backend",
                resource_group_name=self.backend_resource_group_name,
                storage_account_name=self.backend_storage_account_name,
                storage_container_name=self.backend_storage_container_name,
            )
        return self.backend_

    @property
    def pulumi(self) -> ConfigSectionPulumi:
        if not self.pulumi_:
            self.pulumi_ = ConfigSectionPulumi()
        return self.pulumi_

    @property
    def shm(self) -> ConfigSectionSHM:
        if not self.shm_:
            self.shm_ = ConfigSectionSHM(name=self.shm_name_)
        return self.shm_

    @property
    def tags(self) -> ConfigSectionTags:
        if not self.tags_:
            self.tags_ = ConfigSectionTags(deployment=self.name)
        return self.tags_

    def __str__(self) -> str:
        """String representation of the Config object"""
        contents: dict[str, Any] = {}
        if self.azure_:
            contents["azure"] = self.azure.to_dict()
        if self.backend_:
            contents["backend"] = self.backend.to_dict()
        if self.pulumi_:
            contents["pulumi"] = self.pulumi.to_dict()
        if self.shm_:
            contents["shm"] = self.shm.to_dict()
        if self.sres:
            contents["sre"] = {k: v.to_dict() for k, v in self.sres.items()}
        if self.tags:
            contents["tags"] = self.tags.to_dict()
        return str(yaml.dump(contents, indent=2))

    def read_stack(self, name: str, path: pathlib.Path) -> None:
        """Add a Pulumi stack file to config"""
        with open(path, encoding="utf-8") as f_stack:
            pulumi_cfg = f_stack.read()
        self.pulumi.stacks[name] = b64encode(pulumi_cfg)

    def remove_sre(self, name: str) -> None:
        """Remove SRE config section by name"""
        if name in self.sres.keys():
            del self.sres[name]

    def remove_stack(self, name: str) -> None:
        """Remove Pulumi stack section by name"""
        if name in self.pulumi.stacks.keys():
            del self.pulumi.stacks[name]

    def sre(self, name: str) -> ConfigSectionSRE:
        """Return the config entry for this SRE creating it if it does not exist"""
        if name not in self.sres.keys():
            highest_index = max([0] + [int(sre.index) for sre in self.sres.values()])
            self.sres[name].index = highest_index + 1
        return self.sres[name]

    def write_stack(self, name: str, path: pathlib.Path) -> None:
        """Write a Pulumi stack file from config"""
        pulumi_cfg = b64decode(self.pulumi.stacks[name])
        with open(path, "w", encoding="utf-8") as f_stack:
            f_stack.write(pulumi_cfg)

    def upload(self) -> None:
        """Upload config to Azure storage"""
        self.azure_api.upload_blob(
            str(self),
            self.filename,
            self.backend_resource_group_name,
            self.backend_storage_account_name,
            self.backend_storage_container_name,
        )
