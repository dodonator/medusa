import logging
from pathlib import Path

from converter import Converter
from crawler import Crawler
from utils import get_title

logging.basicConfig(filename="crawler.log", filemode="w", level=logging.DEBUG)

root = r"https://md.chaosdorf.de"
start = "navigation"

pad_dir: Path = Path.cwd() / Path("pads")
vault_dir: Path = Path.cwd() / Path("obsidian_vault")

crawler = Crawler(root, pad_dir)
pads = crawler.crawl(start)

for pad in pads:
    crawler.download(pad)

converter = Converter(root, pad_dir, vault_dir)
converter.convert()

# rename pads in vault
for pad in vault_dir.glob("*.md"):
    pad_content = pad.read_text(encoding="UTF-8")
    title: str = get_title(pad_content)
    if title:
        new_filename: str = f"{title}.md"
        new_path: Path = vault_dir / Path(new_filename)
        new_path.write_text(pad_content)
        pad.unlink()
