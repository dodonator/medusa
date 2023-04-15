import hashlib
import logging as log
import re
from pathlib import Path

import pandoc
from pandoc.types import Header, Pandoc


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


def get_title(pad_content: str) -> str:
    """Tries to extract title of pad from content.

    Args:
        pad_content (str): content of pad

    Returns:
        str: pad title
    """
    doc: Pandoc = pandoc.read(pad_content)
    meta: list = doc[0]
    meta_dict: dict = meta[0]
    title: str

    # tries to get title from meta data
    if "title" in meta_dict:
        title = pandoc.write(meta_dict.get("title")).strip()
        log.info(f"found title {title!r} in meta data")
        return title

    blocks: list = doc[1]
    header: list[Header] = [
        block for block in blocks if isinstance(block, Header) and block[0] == 1
    ]
    if header:
        # uses first h1 header as title
        title = pandoc.write(header[0]).strip()
        log.info(f"first header was {title!r}")

        source_pattern = r"[\-~#/ ]+"
        target_pattern = r"_"
        clean_title: str = re.sub(source_pattern, target_pattern, title)
        clean_title = clean_title.strip("_")
        return clean_title

    log.info("no title found")
    return ""
