"""Command-line application for deploying a Secure Research Environment from project files"""
# Standard library imports
import pathlib

# Third party imports
from cleo import Command
import yaml

# Local imports
from data_safe_haven.config import Config, DotFileSettings
from data_safe_haven.exceptions import (
    DataSafeHavenException,
    DataSafeHavenInputException,
)
from data_safe_haven.pulumi import PulumiInterface
from data_safe_haven.mixins import LoggingMixin
from data_safe_haven.provisioning import ContainerProvisioner, PostgreSQLProvisioner


class DeploySRECommand(LoggingMixin, Command):
    """
    Deploy a Secure Research Environment using local configuration and project files

    sre
        {name : Name of SRE to deploy}
        {--c|allow-copy= : Allow copying of text from the SRE (default: False)}
        {--p|allow-paste= : Allow pasting of text into the SRE (default: False)}
        {--o|output= : Path to an output log file}
    """

    def handle(self) -> None:
        try:
            # Set up logging for anything called by this command
            self.initialise_logging(self.io.verbosity, self.option("output"))

            # Use dotfile settings to load the job configuration
            try:
                settings = DotFileSettings()
            except DataSafeHavenInputException:
                raise DataSafeHavenInputException(
                    "Unable to load project settings. Please run this command from inside the project directory."
                )
            config = Config(settings.name, settings.subscription_name)
            self.add_missing_values(config)

            # Deploy infrastructure with Pulumi
            infrastructure = PulumiInterface(
                config, "SRE", sre_name=self.argument("name")
            )
            infrastructure.deploy()
            # # infrastructure.update_config()
            print(f"sre_name: {infrastructure.output('sre_name')}")
            print(f"sre_index: {infrastructure.output('sre_index')}")

            # Add Pulumi output information to the config file
            with open(infrastructure.local_stack_path, "r") as f_stack:
                stack_yaml = yaml.safe_load(f_stack)
            config.pulumi.stack = stack_yaml

            # Upload config to blob storage
            config.upload()

            # # Provision Guacamole
            # # -------------------

            # # Provision the Guacamole PostgreSQL server
            # postgres_provisioner = PostgreSQLProvisioner(
            #     config,
            #     config.pulumi.outputs.guacamole.resource_group_name,
            #     config.pulumi.outputs.guacamole.postgresql_server_name,
            #     infrastructure.secret("guacamole-postgresql-password"),
            # )
            # connections = infrastructure.output("vm_details")
            # connection_data = {
            #     "connections": [
            #         {
            #             "connection_name": connection,
            #             "disable_copy": (not config.settings.allow_copy),
            #             "disable_paste": (not config.settings.allow_paste),
            #             "ip_address": ip_address,
            #             "timezone": config.settings.timezone,
            #         }
            #         for (connection, ip_address) in connections
            #     ]
            # }
            # postgres_script_path = (
            #     pathlib.Path(__file__).parent.parent
            #     / "resources"
            #     / "guacamole"
            #     / "postgresql"
            # )
            # postgres_provisioner.execute_scripts(
            #     [
            #         postgres_script_path / "init_db.sql",
            #         postgres_script_path / "update_connections.mustache.sql",
            #     ],
            #     mustache_values=connection_data,
            # )

            # # Restart the Guacamole container group
            # guacamole_provisioner = ContainerProvisioner(
            #     config,
            #     config.pulumi.outputs.guacamole.resource_group_name,
            #     config.pulumi.outputs.guacamole.container_group_name,
            # )
            # guacamole_provisioner.restart()
        except DataSafeHavenException as exc:
            for (
                line
            ) in f"Could not deploy Secure Research Environment.\n{str(exc)}".split(
                "\n"
            ):
                self.error(line)

    def add_missing_values(self, config: Config) -> None:
        """Request any missing config values and add them to the config"""
        # Create a config entry for this SRE if it does not exist
        sre_name = self.argument("name")
        if sre_name not in config.sre.keys():
            highest_index = max([0] + [sre.index for sre in config.sre.values()])
            config.sre[sre_name].index = highest_index + 1

        # Set whether copying is allowed
        config.sre[sre_name].allow_copy = True if self.option("allow-copy") else False

        # Set whether pasting is allowed
        config.sre[sre_name].allow_paste = True if self.option("allow-paste") else False