from argparse import ArgumentParser
from pathlib import Path
from crawler import pad_id_from_url, extract_urls

output_path: Path = Path.cwd() / Path("pads")

if not output_path.exists():
    output_path.mkdir()

parser = ArgumentParser(description="Crawls the HedgeDoc.")
parser.add_argument("root", help="HegdeDoc base url")
parser.add_argument(
    "-s", "--start", required=False, default="navigation", help="start pad"
)
parser.add_argument(
    "-o", "--output", required=False, default="urls.json", help="output file (json)"
)

args = parser.parse_args()
root = args.root
pad_id = args.start
output_file = args.output

start_url = f"{root}/{pad_id}"

urls_to_check: set = set((start_url,))
checked_urls: set = set()

while urls_to_check:
    current_url = urls_to_check.pop()
    pad_id: str = pad_id_from_url(current_url)
    more_urls: set = set(extract_urls(root, pad_id)) - checked_urls
    print(f"extracted {len(more_urls)} from {pad_id}")
    urls_to_check.update(more_urls)

    checked_urls.add(current_url)

print(f"extracted {len(checked_urls)} urls in total")
