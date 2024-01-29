"""Pulumi dynamic component for managing bcrypt passwords."""
from typing import Any

from pulumi import Input, Output, ResourceOptions
from pulumi.dynamic import CreateResult, DiffResult, Resource

from data_safe_haven.functions import bcrypt_encode, bcrypt_salt, sha256hash
from .dsh_resource_provider import DshResourceProvider


class BcryptPasswordProps:
    """Props for the BcryptPassword class"""

    def __init__(
        self,
        password: Input[str],
    ) -> None:
        self.password = Output.secret(password)


class BcryptPasswordProvider(DshResourceProvider):
    def create(self, props: dict[str, Any]) -> CreateResult:
        """Create compiled desired state file."""
        outputs = dict(**props)
        # Set salt if it does not exist
        if not outputs.get("salt", None):
            outputs["salt"] = bcrypt_salt()
        outputs["encoded"] = bcrypt_encode(outputs["password"], outputs["salt"])
        return CreateResult(
            f"BcryptPassword-{sha256hash(outputs['password'])}",
            outs=outputs,
        )

    def delete(self, id_: str, props: dict[str, Any]) -> None:
        """The Python SDK does not support configuration deletion"""
        # Use `id` as a no-op to avoid ARG002 while maintaining function signature
        id((id_, props))

    def diff(
        self,
        id_: str,
        old_props: dict[str, Any],
        new_props: dict[str, Any],
    ) -> DiffResult:
        """Calculate diff between old and new state"""
        # Use `id` as a no-op to avoid ARG002 while maintaining function signature
        id(id_)
        # If the password has changed then the encoded form must have changed too
        if new_props["password"] != old_props["password"]:
            old_props["encoded"] = None
        print(f"diff::old_props: {old_props}")
        print(f"diff::new_props: {new_props}")
        diff_ = self.partial_diff(old_props, new_props, [])
        print(f"diff::diff.changes {diff_.changes}")
        print(f"diff::diff.replaces {diff_.replaces}")
        print(f"diff::diff.stables {diff_.stables}")
        print(f"diff::diff.delete_before_replace {diff_.delete_before_replace}")
        return diff_
        # return self.partial_diff(old_props, new_props, [])


class BcryptPassword(Resource):
    encoded: Output[str]
    password: Output[str]
    salt: Output[str]
    _resource_type_name = "dsh:common:BcryptPassword"  # set resource type

    def __init__(
        self,
        name: str,
        props: BcryptPasswordProps,
        opts: ResourceOptions | None = None,
    ):
        super().__init__(
            BcryptPasswordProvider(),
            name,
            {"encoded": None, "salt": None, **vars(props)},
            opts,
        )
