import logging
from pathlib import Path

from converter import Converter
from crawler import Crawler
from utils import get_title

logging.basicConfig(filename="crawler.log", filemode="w", level=logging.DEBUG)

ROOT = r"https://md.chaosdorf.de"
START = "navigation"

pad_dir: Path = Path.cwd() / Path("pads")
vault_dir: Path = Path.cwd() / Path("obsidian_vault")

crawler: Crawler = Crawler(ROOT, pad_dir)
pads: set[str] = crawler.crawl(START)

pad_id: str
for pad_id in pads:
    crawler.download(pad_id)

converter: Converter = Converter(ROOT, pad_dir, vault_dir)
converter.convert()

# rename pads in vault
pad_path: Path
for pad_path in vault_dir.glob("*.md"):
    pad_content: str = pad_path.read_text(encoding="UTF-8")
    title: str = get_title(pad_content)

    if title:
        new_filename: str = f"{title}.md"
        new_path: Path = vault_dir / Path(new_filename)
        new_path.write_text(pad_content)
        pad_path.unlink()
