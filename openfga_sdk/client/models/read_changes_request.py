class ClientReadChangesRequest:
    """
    ClientReadChangesRequest encapsulates the parameters required to read changes
    """

    def __init__(
        self,
        type: str,
        start_time: str | None = None,
    ):
        self._type = type
        self._startTime = start_time

    @property
    def type(self) -> str:
        """
        Return type
        """
        return self._type

    @type.setter
    def type(
        self,
        value: str,
    ) -> None:
        """
        Set type
        """
        self._type = value

    @property
    def start_time(self) -> str | None:
        """
        Return startTime
        """
        return self._startTime

    @start_time.setter
    def start_time(
        self,
        value: str | None,
    ) -> None:
        """
        Set startTime
        """
        self._startTime = value
