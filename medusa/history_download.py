import json
from pathlib import Path
from typing import TextIO
from urllib.parse import ParseResult, urlparse

from medusa.medusa import download

working_dir: Path = Path("/home/dodo/dev/Python/medusa/medusa/")
history_file: Path = working_dir / Path("history.json")

url_str: str = "https://md.chaosdorf.de"
url: ParseResult = urlparse(url=url_str)

stream: TextIO
with history_file.open(mode="r") as stream:
    content: str = stream.read()
    data: dict = json.loads(content)

pad: dict
for pad in data:
    # generate pad url
    pad_id: str | None = pad.get("id")
    if pad_id is None:
        continue
    pad_url: str = f"{url.geturl()}/{pad_id}"

    # download pad
    pad_content: str = download(pad_url)

    # save pad content to FS
    filename: str = f"{pad_id}.md"
    filepath: Path = working_dir / Path(filename)

    stream: TextIO
    with filepath.open(mode="w") as stream:
        stream.write(pad_content)
