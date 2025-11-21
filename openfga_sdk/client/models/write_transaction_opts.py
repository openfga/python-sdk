class WriteTransactionOpts:
    """
    OpenFGA client write transaction info
    """

    def __init__(
        self,
        disabled: bool = False,
        max_per_chunk: int = 1,
        max_parallel_requests: int = 10,
    ) -> None:
        self._disabled = disabled
        self._max_per_chunk = max_per_chunk
        self._max_parallel_requests = max_parallel_requests

    @property
    def disabled(self) -> bool:
        """
        Return disabled
        """
        return self._disabled

    @disabled.setter
    def disabled(
        self,
        value: bool,
    ) -> None:
        """
        Set disabled
        """
        self._disabled = value

    @property
    def max_per_chunk(self) -> int:
        """
        Return max per chunk
        """
        return self._max_per_chunk

    @max_per_chunk.setter
    def max_per_chunk(
        self,
        value: int,
    ) -> None:
        """
        Set max_per_chunk
        """
        self._max_per_chunk = value

    @property
    def max_parallel_requests(self) -> int:
        """
        Return max parallel requests
        """
        return self._max_parallel_requests

    @max_parallel_requests.setter
    def max_parallel_requests(
        self,
        value: int,
    ) -> None:
        """
        Set max_parallel_requests
        """
        self._max_parallel_requests = value
