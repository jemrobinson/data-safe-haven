"""Interact with users in an Azure Active Directory"""
from collections.abc import Sequence
from typing import Any

from data_safe_haven.external import GraphApi
from data_safe_haven.functions import password
from data_safe_haven.utility import LoggingSingleton

from .research_user import ResearchUser


class AzureADUsers:
    """Interact with users in an Azure Active Directory"""

    def __init__(
        self,
        graph_api: GraphApi,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.graph_api = graph_api
        self.logger = LoggingSingleton()

    def add(self, new_users: Sequence[ResearchUser]) -> None:
        """Add list of users to AzureAD"""
        # Get the default domain
        default_domain = next(
            domain["id"]
            for domain in self.graph_api.read_domains()
            if domain["isDefault"]
        )
        for user in new_users:
            request_json = {
                "accountEnabled": user.account_enabled,
                "displayName": user.display_name,
                "givenName": user.given_name,
                "surname": user.surname,
                "mailNickname": user.username,
                "passwordProfile": {"password": password(20)},
                "userPrincipalName": f"{user.username}@{default_domain}",
            }
            if user.email_address and user.phone_number:
                self.graph_api.create_user(
                    request_json, user.email_address, user.phone_number
                )
            self.logger.info(
                f"Ensured user '{user.preferred_username}' exists in AzureAD"
            )
        # Decorate all users with the Linux schema
        self.set_user_attributes()
        # # Ensure that all users belong to an associated group the same name and UID
        # for user in self.list():
        #     self.graph_api.create_group(user.username, user.uid_number)
        #     self.graph_api.add_user_to_group(user.username, user.username)
        #     # Also add the user to the research users group
        #     self.graph_api.add_user_to_group(user.username, self.researchers_group_name)

    def list(self) -> Sequence[ResearchUser]:  # noqa: A003
        user_list = self.graph_api.read_users()
        return [
            ResearchUser(
                account_enabled=user_details["accountEnabled"],
                email_address=user_details["mail"],
                given_name=user_details["givenName"],
                phone_number=(
                    user_details["businessPhones"][0]
                    if len(user_details["businessPhones"])
                    else None
                ),
                sam_account_name=(
                    user_details["onPremisesSamAccountName"]
                    if user_details["onPremisesSamAccountName"]
                    else user_details["mailNickname"]
                ),
                surname=user_details["surname"],
                user_principal_name=user_details["userPrincipalName"],
            )
            for user_details in user_list
            if (
                user_details["onPremisesSamAccountName"]
                or user_details["isGlobalAdmin"]
            )
        ]

    def remove(self, users: Sequence[ResearchUser]) -> None:
        """Disable a list of users in AzureAD"""
        # for user_to_remove in users:
        #     matched_users = [user for user in self.users if user == user_to_remove]
        #     if not matched_users:
        #         continue
        #     user = matched_users[0]
        #     try:
        #         if self.graph_api.remove_user_from_group(
        #             user.username, self.researchers_group_name
        #         ):
        #             self.logger.info(
        #                 f"Removed '{user.preferred_username}' from group '{self.researchers_group_name}'"
        #             )
        #         else:
        #             raise DataSafeHavenMicrosoftGraphError
        #     except DataSafeHavenMicrosoftGraphError:
        #         self.logger.error(
        #             f"Unable to remove '{user.preferred_username}' from group '{self.researchers_group_name}'"
        #         )
        pass

    def set(self, users: Sequence[ResearchUser]) -> None:  # noqa: A003
        """Set Guacamole users to specified list"""
        users_to_remove = [user for user in self.list() if user not in users]
        self.remove(users_to_remove)
        users_to_add = [user for user in users if user not in self.list()]
        self.add(users_to_add)

    def set_user_attributes(self) -> None:
        """Ensure that all users have Linux attributes"""
        # next_uid = max(
        #     [int(user.uid_number) + 1 if user.uid_number else 0 for user in self.users]
        #     + [10000]
        # )
        # for user in self.users:
        #     try:
        #         # Get username from userPrincipalName
        #         username = user.user_principal_name.split("@")[0]
        #         if not user.homedir:
        #             user.homedir = f"/home/{username}"
        #             self.logger.debug(
        #                 f"Added homedir {user.homedir} to user {user.preferred_username}"
        #             )
        #         if not user.shell:
        #             user.shell = "/bin/bash"
        #             self.logger.debug(
        #                 f"Added shell {user.shell} to user {user.preferred_username}"
        #             )
        #         if not user.uid_number:
        #             # Set UID to the next unused one
        #             user.uid_number = next_uid
        #             next_uid += 1
        #             self.logger.debug(
        #                 f"Added uid {user.uid_number} to user {user.preferred_username}"
        #             )
        #         if not user.username:
        #             user.username = username
        #             self.logger.debug(
        #                 f"Added username {user.username} to user {user.preferred_username}"
        #             )
        #         # Ensure that the remote user matches the local model
        #         patch_json = {
        #             GraphApi.linux_schema: {
        #                 "gidnumber": user.uid_number,
        #                 "homedir": user.homedir,
        #                 "shell": user.shell,
        #                 "uid": user.uid_number,
        #                 "user": user.username,
        #             }
        #         }
        #         self.graph_api.http_patch(
        #             f"{self.graph_api.base_endpoint}/users/{user.azure_oid}",
        #             json=patch_json,
        #         )
        #         self.logger.debug(f"Set Linux attributes for user {user.preferred_username}.")
        #     except Exception as exc:
        #         self.logger.error(
        #             f"Failed to set Linux attributes for user {user.preferred_username}.\n{str(exc)}"
        #         )
        pass