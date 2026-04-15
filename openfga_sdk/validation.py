import re


_ULID_REGEX = re.compile("^[0-7][0-9A-HJKMNP-TV-Z]{25}$")


def is_well_formed_ulid_string(ulid):
    if not isinstance(ulid, str):
        return False
    match = _ULID_REGEX.match(ulid)
    if match is None:
        return False
    return True
