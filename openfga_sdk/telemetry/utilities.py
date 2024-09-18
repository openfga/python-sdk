def doesInstanceHaveCallable(instance: object, callableName: str) -> bool:
    instanceCallable = getattr(instance, callableName, None)

    if instanceCallable is None:
        return False

    return callable(instanceCallable)
