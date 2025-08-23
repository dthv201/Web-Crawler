import sys
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def same_domain_retio(page_url: str, links: list[str]) -> float:
    page_host = urlparse(page_url).netloc
    hosts = [urlparse(l).netloc for l in links]
    if not hosts:
        return 0.0
    
    same_domain = sum(1 for h in hosts if h == page_host)
    return same_domain / len(hosts)


def extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        try:
            absu = urljoin(base_url, a['href'].split('#')[0]) # Make the link absolute
            parts = urlparse(absu)
            if parts.scheme in ('http', 'https'):
                links.append(absu)
        except Exception as e:
            print(f"Error extracting link from {base_url}: {e}")
            pass
    return links

# Fetch HTML content from a URL
async def fetch_html(url: str, timeout: int =15 ) -> str | None:
    try:
        
        async with aiohttp.ClientSession(headers={"User-Agent": "SimpleCrawler/1.0"}) as s:
            async with s.get(url, timeout=timeout) as r:
                ctype = (r.headers.get("Content-Type" or "")).lower()
                if "text/html" not in ctype:
                    return None
                return await r.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
           
def main():
    arg_count = len(sys.argv) - 1

    if arg_count not in (2, 3):
        print("Usage: python crawler.py <URL> <depth> [out.tsv]")
        raise SystemExit(1)

    root = sys.argv[1]
    try:
        depth = int(sys.argv[2])
    except ValueError:
        print("Depth must be an integer")
        raise SystemExit(1)

    out = sys.argv[3] if arg_count == 3 else "crawl.tsv"
    print(f"OK: root={root}, depth={depth}, out={out}")

    html = asyncio.run(fetch_html(root))
    # Check if HTML was fetched successfully
    print("HTML?", html is not None)
    
    if html:
        links = extract_links(html, root)
        print(f"Found {len(links)} links; first 5:\n", "\n".join(links[:5]))
        ratio = same_domain_retio(root, links)
        print("Ratio:", ratio)

if __name__ == "__main__":
    main()
