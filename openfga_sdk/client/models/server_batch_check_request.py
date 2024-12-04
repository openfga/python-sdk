
from openfga_sdk.client.models import ServerBatchCheckItem
class ServerBatchCheckRequest:
    """
    """

    def __init__(self, checks: list[ServerBatchCheckItem]):
        self._checks = checks

    @property
    def checks(self):
        return self._checks
    
    @checks.setter
    def checks(self, checks):
        self._checks = checks