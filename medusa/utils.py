import hashlib
from pathlib import Path


def hash_file(path: Path):
    """Creates file checksum using md5.

    Args:
        path (Path): path to file

    Returns:
        hashlib._Hash: md5 checksum
    """
    buffer_size: int = 256
    md5 = hashlib.md5()

    with path.open("rb") as stream:
        while True:
            data = stream.read(buffer_size)
            if not data:
                break
            md5.update(data)

    return md5
