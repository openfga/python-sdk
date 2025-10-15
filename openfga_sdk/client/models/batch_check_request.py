from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem


class ClientBatchCheckRequest:
    """
    ClientBatchCheckRequest encapsulates the parameters for a BatchCheck request
    """

    def __init__(
        self,
        checks: list[ClientBatchCheckItem],
    ) -> None:
        self._checks = checks

    @property
    def checks(self) -> list[ClientBatchCheckItem]:
        """
        Return checks
        """
        return self._checks

    @checks.setter
    def checks(self, checks: list[ClientBatchCheckItem]) -> None:
        """
        Set checks
        """
        self._checks = checks
