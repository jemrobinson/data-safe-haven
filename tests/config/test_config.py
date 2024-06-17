import pytest
from pydantic import ValidationError

from data_safe_haven.config import Config
from data_safe_haven.config.config import (
    ConfigSectionAzure,
    ConfigSectionSHM,
    ConfigSectionSRE,
    ConfigSubsectionRemoteDesktopOpts,
)
from data_safe_haven.exceptions import (
    DataSafeHavenConfigError,
    DataSafeHavenParameterError,
)
from data_safe_haven.external import AzureApi
from data_safe_haven.types import DatabaseSystem, SoftwarePackageCategory


class TestConfigSectionAzure:
    def test_constructor(self):
        ConfigSectionAzure(
            subscription_id="d5c5c439-1115-4cb6-ab50-b8e547b6c8dd",
            tenant_id="d5c5c439-1115-4cb6-ab50-b8e547b6c8dd",
        )


class TestConfigSectionSHM:
    def test_constructor(self):
        ConfigSectionSHM(
            entra_tenant_id="d5c5c439-1115-4cb6-ab50-b8e547b6c8dd",
            fqdn="shm.acme.com",
            timezone="UTC",
        )

    def test_update(self, shm_config_section):
        assert shm_config_section.fqdn == "shm.acme.com"
        shm_config_section.update(fqdn="shm.example.com")
        assert shm_config_section.fqdn == "shm.example.com"

    def test_update_validation(self, shm_config_section):
        with pytest.raises(
            ValidationError,
            match="Value error, Expected valid fully qualified domain name, for example 'example.com'.*not an FQDN",
        ):
            shm_config_section.update(fqdn="not an FQDN")


class TestConfigSubsectionRemoteDesktopOpts:
    def test_constructor(self):
        ConfigSubsectionRemoteDesktopOpts(allow_copy=True, allow_paste=True)

    def test_constructor_defaults(self):
        remote_desktop_config = ConfigSubsectionRemoteDesktopOpts()
        assert not all(
            (remote_desktop_config.allow_copy, remote_desktop_config.allow_paste)
        )

    def test_update(self, remote_desktop_config):
        assert not all(
            (remote_desktop_config.allow_copy, remote_desktop_config.allow_paste)
        )
        remote_desktop_config.update(allow_copy=True, allow_paste=True)
        assert all(
            (remote_desktop_config.allow_copy, remote_desktop_config.allow_paste)
        )


class TestConfigSectionSRE:
    def test_constructor(self, remote_desktop_config):
        sre_config = ConfigSectionSRE(
            admin_email_address="admin@example.com",
            admin_ip_addresses=["1.2.3.4"],
            databases=[DatabaseSystem.POSTGRESQL],
            data_provider_ip_addresses=["2.3.4.5"],
            remote_desktop=remote_desktop_config,
            workspace_skus=["Standard_D2s_v4"],
            research_user_ip_addresses=["3.4.5.6"],
            software_packages=SoftwarePackageCategory.ANY,
        )
        assert sre_config.admin_email_address == "admin@example.com"
        assert sre_config.admin_ip_addresses[0] == "1.2.3.4/32"
        assert sre_config.databases[0] == DatabaseSystem.POSTGRESQL
        assert sre_config.data_provider_ip_addresses[0] == "2.3.4.5/32"
        assert sre_config.remote_desktop == remote_desktop_config
        assert sre_config.workspace_skus[0] == "Standard_D2s_v4"
        assert sre_config.research_user_ip_addresses[0] == "3.4.5.6/32"
        assert sre_config.software_packages == SoftwarePackageCategory.ANY


    def test_constructor_defaults(self, remote_desktop_config):
        sre_config = ConfigSectionSRE(admin_email_address="admin@example.com")
        assert sre_config.admin_email_address == "admin@example.com"
        assert sre_config.admin_ip_addresses == []
        assert sre_config.databases == []
        assert sre_config.data_provider_ip_addresses == []
        assert sre_config.remote_desktop == remote_desktop_config
        assert sre_config.workspace_skus == []
        assert sre_config.research_user_ip_addresses == []
        assert sre_config.software_packages == SoftwarePackageCategory.NONE

    def test_all_databases_must_be_unique(self):
        with pytest.raises(ValueError, match="All items must be unique."):
            ConfigSectionSRE(
                databases=[DatabaseSystem.POSTGRESQL, DatabaseSystem.POSTGRESQL],
            )

    def test_update(self):
        sre_config = ConfigSectionSRE(admin_email_address="admin@example.com")
        assert sre_config.admin_email_address == "admin@example.com"
        assert sre_config.admin_ip_addresses == []
        assert sre_config.databases == []
        assert sre_config.data_provider_ip_addresses == []
        assert sre_config.workspace_skus == []
        assert sre_config.research_user_ip_addresses == []
        assert sre_config.software_packages == SoftwarePackageCategory.NONE
        sre_config.update(
            admin_email_address="admin@example.org",
            admin_ip_addresses=["1.2.3.4"],
            data_provider_ip_addresses=["2.3.4.5"],
            databases=[DatabaseSystem.MICROSOFT_SQL_SERVER],
            workspace_skus=["Standard_D8s_v4"],
            software_packages=SoftwarePackageCategory.ANY,
            user_ip_addresses=["3.4.5.6"],
        )
        assert sre_config.admin_email_address == "admin@example.org"
        assert sre_config.admin_ip_addresses == ["1.2.3.4/32"]
        assert sre_config.databases == [DatabaseSystem.MICROSOFT_SQL_SERVER]
        assert sre_config.data_provider_ip_addresses == ["2.3.4.5/32"]
        assert sre_config.workspace_skus == ["Standard_D8s_v4"]
        assert sre_config.research_user_ip_addresses == ["3.4.5.6/32"]
        assert sre_config.software_packages == SoftwarePackageCategory.ANY


class TestConfig:
    def test_constructor(self, azure_config, shm_config_section):
        config = Config(
            azure=azure_config,
            shm=shm_config_section,
        )
        assert not config.sres

    @pytest.mark.parametrize("require_sres,expected", [(False, True), (True, False)])
    def test_is_complete_no_sres(self, config_no_sres, require_sres, expected):
        assert config_no_sres.is_complete(require_sres=require_sres) is expected

    @pytest.mark.parametrize("require_sres", [False, True])
    def test_is_complete_sres(self, config_sres, require_sres):
        assert config_sres.is_complete(require_sres=require_sres)

    def test_sre(self, config_sres):
        sre1, sre2 = config_sres.sre("sre1"), config_sres.sre("sre2")
        assert sre1 != sre2

    def test_sre_invalid(self, config_sres):
        with pytest.raises(DataSafeHavenConfigError) as exc:
            config_sres.sre("sre3")
            assert "SRE sre3 does not exist" in exc

    def test_template(self):
        config = Config.template()
        assert isinstance(config, Config)
        assert config.azure.subscription_id == "Azure subscription ID"

    def test_template_validation(self):
        config = Config.template()
        with pytest.raises(DataSafeHavenParameterError):
            Config.from_yaml(config.to_yaml())

    def test_from_yaml(self, config_sres, config_yaml):
        config = Config.from_yaml(config_yaml)
        assert config == config_sres
        assert isinstance(
            config.sres["sre1"].software_packages, SoftwarePackageCategory
        )

    def test_from_remote(self, mocker, context, config_sres, config_yaml):
        mock_method = mocker.patch.object(
            AzureApi, "download_blob", return_value=config_yaml
        )
        config = Config.from_remote(context)

        assert config == config_sres
        mock_method.assert_called_once_with(
            Config.filename,
            context.resource_group_name,
            context.storage_account_name,
            context.storage_container_name,
        )

    def test_to_yaml(self, config_sres, config_yaml):
        assert config_sres.to_yaml() == config_yaml

    def test_upload(self, mocker, context, config_sres):
        mock_method = mocker.patch.object(AzureApi, "upload_blob", return_value=None)
        config_sres.upload(context)

        mock_method.assert_called_once_with(
            config_sres.to_yaml(),
            Config.filename,
            context.resource_group_name,
            context.storage_account_name,
            context.storage_container_name,
        )
