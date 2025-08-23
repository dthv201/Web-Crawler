import sys
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os
import asyncio
# Step 6 — Add concurrency (utilize the machine)
import os
import asyncio

async def crawl(root: str, max_depth: int) -> list[tuple[str,int,float]]:
    visited = {root}
    results: list[tuple[str,int,float]] = []
    frontier: list[tuple[str,int]] = [(root, 0)]
    max_conc = max(20, (os.cpu_count() or 2) * 5)
    sem = asyncio.Semaphore(max_conc)

    async with aiohttp.ClientSession(headers={"User-Agent": "SimpleCrawler/1.0"}) as s:
        while frontier:
            next_frontier: list[tuple[str,int]] = []
            tasks = []

            async def work(u: str, d: int):
                async with sem:
                    html = None
                    try:
                        async with s.get(u, timeout=15) as r:
                            if "text/html" in (r.headers.get("Content-Type") or "").lower():
                                html = await r.text()
                    except Exception:
                        pass

                    if not html:
                        results.append((u, d, 0.0)); return

                    links = extract_links(html, u)
                    ratio = round(same_domain_retio(u, links), 6)
                    results.append((u, d, ratio))

                    if d < max_depth:
                        for l in links:
                            if l not in visited:
                                visited.add(l)
                                next_frontier.append((l, d + 1))

            for url, d in frontier:
                tasks.append(asyncio.create_task(work(url, d)))

            await asyncio.gather(*tasks)
            frontier = next_frontier

    return results



# Crawl with depth (BFS) and “visited”
async def crawl_sync_style(root: str, max_depth: int)-> list[tuple[str, int, float]]:
    visited = {root}
    results: list[tuple[str, int, float]] = []
    frontier: list[tuple[str,int]] = [(root, 0)]

    async with aiohttp.ClientSession(headers={"User-Agent": "SimpleCrawler/1.0"}) as session:
        while frontier:
            next_frontier: list[tuple[str,int]] = []
            for url, depth in frontier:
                html = None
                try:
                    async with session.get(url, timeout=15) as response:
                        if "text/html" not in (response.headers.get("Content-Type") or "").lower():
                            html = await response.text()
                except Exception:
                    pass
                if not html:
                    results.append((url, depth, 0.0))
                    continue

                links = extract_links(html, url)
                ratio = round(same_domain_retio(url, links), 6)
                results.append((url, depth, ratio))

                if depth < max_depth:
                    for l in links:
                        if l not in visited:
                            visited.add(l)
                            next_frontier.append((l, depth + 1))
            frontier = next_frontier

    return results

# compute the same-domain ratio for that single page.
def same_domain_retio(page_url: str, links: list[str]) -> float:
    page_host = urlparse(page_url).netloc
    hosts = [urlparse(l).netloc for l in links]
    if not hosts:
        return 0.0
    
    same_domain = sum(1 for h in hosts if h == page_host)
    return same_domain / len(hosts)

# extract all <a href="..."> links from that HTML.
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
        rows = asyncio.run(crawl(root, depth))
        print("Crawled", len(rows), "pages")


if __name__ == "__main__":
    main()
