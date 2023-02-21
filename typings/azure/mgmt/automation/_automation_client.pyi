from typing import Any, Optional
from azure.core.credentials import TokenCredential
from .operations import DscCompilationJobOperations, ModuleOperations

class AutomationClient(object):
    def __init__(
        self,
        credential: TokenCredential,
        subscription_id: str,
        base_url: Optional[str] = ...,
        **kwargs: Any
    ) -> None: ...
    @property
    def module(self) -> ModuleOperations: ...
    @property
    def dsc_compilation_job(self) -> DscCompilationJobOperations: ...