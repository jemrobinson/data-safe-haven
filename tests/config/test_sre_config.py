import pytest
from pydantic import ValidationError

from data_safe_haven.config import SREConfig
from data_safe_haven.config.config_sections import (
    ConfigSectionAzure,
    ConfigSectionSRE,
)
from data_safe_haven.context import Context
from data_safe_haven.exceptions import (
    DataSafeHavenParameterError,
)
from data_safe_haven.external import AzureApi
from data_safe_haven.types import SoftwarePackageCategory


class TestConfig:
    def test_constructor(
        self, azure_config: ConfigSectionAzure, sre_config_section: ConfigSectionSRE
    ) -> None:
        config = SREConfig(
            azure=azure_config,
            sre=sre_config_section,
        )
        assert config.is_complete()

    def test_constructor_invalid(self, azure_config: ConfigSectionAzure) -> None:
        with pytest.raises(
            ValidationError,
            match=r"1 validation error for SREConfig\nsre\n  Field required.*",
        ):
            SREConfig(azure=azure_config)

    def test_template(self) -> None:
        config = SREConfig.template()
        assert isinstance(config, SREConfig)
        assert (
            config.azure.subscription_id
            == "ID of the Azure subscription that the SRE will be deployed to"
        )

    def test_template_validation(self) -> None:
        config = SREConfig.template()
        with pytest.raises(DataSafeHavenParameterError):
            SREConfig.from_yaml(config.to_yaml())

    def test_from_yaml(self, sre_config, sre_config_yaml) -> None:
        config = SREConfig.from_yaml(sre_config_yaml)
        assert config == sre_config
        assert isinstance(config.sre.software_packages, SoftwarePackageCategory)

    def test_from_remote(
        self, mocker, context: Context, sre_config: SREConfig, sre_config_yaml: str
    ) -> None:
        mock_method = mocker.patch.object(
            AzureApi, "download_blob", return_value=sre_config_yaml
        )
        config = SREConfig.from_remote(context)

        assert config == sre_config
        mock_method.assert_called_once_with(
            SREConfig.default_filename,
            context.resource_group_name,
            context.storage_account_name,
            context.storage_container_name,
        )

    def test_to_yaml(self, sre_config: SREConfig, sre_config_yaml: str) -> None:
        assert sre_config.to_yaml() == sre_config_yaml

    def test_upload(self, mocker, context, sre_config) -> None:
        mock_method = mocker.patch.object(AzureApi, "upload_blob", return_value=None)
        sre_config.upload(context)

        mock_method.assert_called_once_with(
            sre_config.to_yaml(),
            SREConfig.default_filename,
            context.resource_group_name,
            context.storage_account_name,
            context.storage_container_name,
        )