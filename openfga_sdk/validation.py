import re


def is_well_formed_ulid_string(ulid):
    regex = re.compile("^[0-7][0-9A-HJKMNP-TV-Z]{25}$")
    if not isinstance(ulid, str):
        return False
    match = regex.match(ulid)
    if match is None:
        return False
    return True
