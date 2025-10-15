class ClientAssertion:
    """
    ClientAssertion flattens the input necessary for an Assertion
    """

    def __init__(
        self,
        user: str,
        relation: str,
        object: str,
        expectation: bool,
    ) -> None:
        self._user = user
        self._relation = relation
        self._object = object
        self._expectation = expectation

    @property
    def user(self) -> str:
        """
        Return user
        """
        return self._user

    @user.setter
    def user(self, user: str) -> None:
        """
        Set user
        """
        self._user = user

    @property
    def relation(self) -> str:
        """
        Return relation
        """
        return self._relation

    @relation.setter
    def relation(self, relation: str) -> None:
        """
        Set relation
        """
        self._relation = relation

    @property
    def object(self) -> str:
        """
        Return object
        """
        return self._object

    @object.setter
    def object(self, object: str) -> None:
        """
        Set object
        """
        self._object = object

    @property
    def expectation(self) -> bool:
        """
        Return expectation
        """
        return self._expectation

    @expectation.setter
    def expectation(self, expectation: bool) -> None:
        """
        Set expectation
        """
        self._expectation = expectation
