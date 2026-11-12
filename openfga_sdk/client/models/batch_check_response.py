from openfga_sdk.client.models.batch_check_single_response import (
    ClientBatchCheckSingleResponse,
)


class ClientBatchCheckResponse:
    def __init__(
        self,
        result: list[ClientBatchCheckSingleResponse],
        checks_sent: int | None = None,
    ) -> None:
        self._result = result
        self._checks_sent = checks_sent

    @property
    def result(self) -> list[ClientBatchCheckSingleResponse]:
        """
        Return result
        """
        return self._result

    @result.setter
    def result(self, result: list[ClientBatchCheckSingleResponse]) -> None:
        """
        Set result
        """
        self._result = result

    @property
    def checks_sent(self) -> int | None:
        """
        Return how many checks this call sent. Set only when merge_equivalent_checks is on.
        """
        return self._checks_sent

    @checks_sent.setter
    def checks_sent(self, checks_sent: int | None) -> None:
        """
        Set checks_sent
        """
        self._checks_sent = checks_sent
