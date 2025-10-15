from openfga_sdk.client.models.batch_check_single_response import (
    ClientBatchCheckSingleResponse,
)


class ClientBatchCheckResponse:
    def __init__(
        self,
        result: list[ClientBatchCheckSingleResponse],
    ) -> None:
        self._result = result

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
