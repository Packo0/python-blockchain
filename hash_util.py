import hashlib as hl
import json


def has_string_256(string):
    return hl.sha256(string).hexdigest()


def hash_block(block):
    """Hashes a block and returns a string representation of it.

    Arguments:
      :block: The block that should be hashed.
    """
    return has_string_256(json.dumps(block, sort_keys=True).encode())
