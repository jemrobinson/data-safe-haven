"""Pulumi dynamic component for files uploaded to an Azure FileShare."""
# Standard library imports
from contextlib import suppress
from typing import Dict, Optional

# Third party imports
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.fileshare import ShareDirectoryClient, ShareFileClient
from pulumi import Input, Output, ResourceOptions
from pulumi.dynamic import CreateResult, DiffResult, Resource

# Local imports
from data_safe_haven.exceptions import DataSafeHavenAzureException

from .dsh_resource_provider import DshResourceProvider


class FileShareFileProps:
    """Props for the FileShareFile class"""

    def __init__(
        self,
        destination_path: Input[str],
        file_contents: Input[str],
        share_name: Input[str],
        storage_account_key: Input[str],
        storage_account_name: Input[str],
    ):
        self.destination_path = destination_path
        self.file_contents = file_contents
        self.share_name = share_name
        self.storage_account_key = storage_account_key
        self.storage_account_name = storage_account_name


class FileShareFileProvider(DshResourceProvider):
    @staticmethod
    def file_exists(file_client: ShareFileClient):
        try:
            file_client.get_file_properties()
            return True
        except ResourceNotFoundError:
            return False

    @staticmethod
    def get_file_client(
        storage_account_name: str,
        storage_account_key: str,
        share_name: str,
        destination_path: str,
    ):
        tokens = destination_path.split("/")
        directory = "/".join(tokens[:-1])
        file_name = tokens[-1]
        if directory:
            directory_client = ShareDirectoryClient(
                account_url=f"https://{storage_account_name}.file.core.windows.net",
                share_name=share_name,
                directory_path=directory,
                credential=storage_account_key,
            )
            if not directory_client.exists():
                directory_client.create_directory()
            return directory_client.get_file_client(file_name)
        return ShareFileClient(
            account_url=f"https://{storage_account_name}.file.core.windows.net",
            share_name=share_name,
            file_path=file_name,
            credential=storage_account_key,
        )

    @staticmethod
    def refresh(props: Dict[str, str]) -> Dict[str, str]:
        with suppress(Exception):
            file_client = FileShareFileProvider.get_file_client(
                props["storage_account_name"],
                props["storage_account_key"],
                props["share_name"],
                props["destination_path"],
            )
            if not FileShareFileProvider.file_exists(file_client):
                props["file_name"] = None
        return dict(**props)

    def create(self, props: Dict[str, str]) -> CreateResult:
        """Create file in target storage account with specified contents."""
        outs = dict(**props)
        try:
            file_client = self.get_file_client(
                props["storage_account_name"],
                props["storage_account_key"],
                props["share_name"],
                props["destination_path"],
            )
            file_client.upload_file(props["file_contents"].encode("utf-8"))
            outs["file_name"] = file_client.file_name
        except Exception as exc:
            raise DataSafeHavenAzureException(
                f"Failed to upload data to <fg=green>{file_client.file_name}</> in <fg=green>{props['share_name']}</>.\n{str(exc)}"
            ) from exc
        return CreateResult(
            f"filesharefile-{props['destination_path'].replace('/', '-')}",
            outs=outs,
        )

    def delete(self, id_: str, props: Dict[str, str]):
        """Delete a file from the target storage account"""
        try:
            file_client = self.get_file_client(
                props["storage_account_name"],
                props["storage_account_key"],
                props["share_name"],
                props["destination_path"],
            )
            if self.file_exists(file_client):
                file_client.delete_file()
        except Exception as exc:
            raise DataSafeHavenAzureException(
                f"Failed to delete file <fg=green>{file_client.file_name}</> in <fg=green>{props['share_name']}</>.\n{str(exc)}"
            ) from exc

    def diff(
        self,
        id_: str,
        old_props: Dict[str, str],
        new_props: Dict[str, str],
    ) -> DiffResult:
        """Calculate diff between old and new state"""
        # Exclude "storage_account_key" which should not trigger a diff
        return self.partial_diff(old_props, new_props, ["storage_account_key"])


class FileShareFile(Resource):
    file_name: Output[str]

    def __init__(
        self,
        name: str,
        props: FileShareFileProps,
        opts: Optional[ResourceOptions] = None,
    ):
        self._resource_type_name = "dsh:FileShareFile"  # set resource type
        super().__init__(
            FileShareFileProvider(), name, {"file_name": None, **vars(props)}, opts
        )