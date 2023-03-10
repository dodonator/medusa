from crawler import Crawler

root = "https://md.chaosdorf.de"
start = "navigation"

crawler = Crawler(root)
pads = crawler.crawl(start)
print(pads)
for pad in pads:
    crawler.download(pad)
