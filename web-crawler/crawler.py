from collections.abc import Set
import sys
import os
import asyncio
from typing import List, Tuple
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

async def crawl_dfs(root: str, max_depth: int) -> List[Tuple[str, int, float]]:
    results: List[Tuple[str, int, float]] = []

    frontier: asyncio.LifoQueue[tuple[str, int]] = asyncio.LifoQueue()
    await frontier.put((root, 0))

    visited: set[str] = {root}
    visited_lock = asyncio.Lock()

    max_conc = max(10, (os.cpu_count() or 2) * 5)

    async def maybe_enqueue(url: str, depth: int):
        async with visited_lock:
            if url in visited:
                return
            visited.add(url)
        await frontier.put((url, depth))

    async def worker():
        while True:
            try:
                url, depth = await asyncio.wait_for(frontier.get(), timeout=1.0)
            except asyncio.TimeoutError:
                return

            html = await fetch_html(url) 

            if not html:
                results.append((url, depth, 0.0))
                frontier.task_done()
                continue

            links = extract_links(html, url)          
            ratio = round(same_domain_ratio(url, links), 6)  
            results.append((url, depth, ratio))

            if depth < max_depth and links:
                for l in reversed(links):
                    await maybe_enqueue(l, depth + 1)

            frontier.task_done()

    workers = [asyncio.create_task(worker()) for _ in range(max_conc)]
    await frontier.join()
    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

    return results
async def crawl_bfs(root: str, max_depth: int) -> list[tuple[str, int, float]]:
    visited: set[str] = {root}
    results: list[tuple[str, int, float]] = []
    frontier: list[tuple[str, int]] = [(root, 0)]

    # reasonable concurrency cap; I/O-bound so > CPUs is fine
    max_conc = max(20, (os.cpu_count() or 2) * 5)
    sem = asyncio.Semaphore(max_conc)

    headers = {"User-Agent": "SimpleCrawler/1.0 (+interview exercise)"}
    async with aiohttp.ClientSession(headers=headers) as session:
        while frontier:
            next_frontier: list[tuple[str, int]] = []
            tasks: list[asyncio.Task] = []

            async def work(u: str, d: int):
                async with sem:
                    html: str | None = None
                    try:
                        async with session.get(u, timeout=15) as r:
                            ctype = (r.headers.get("Content-Type") or "").lower()
                            if "text/html" in ctype:
                                html = await r.text()
                    except Exception:
                        html = None

                    if not html:
                        results.append((u, d, 0.0))
                        return

                    links = extract_links(html, u)
                    ratio = round(same_domain_ratio(u, links), 6)
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
# Write to file
def write_tsv(rows: list[tuple[str, int, float]], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Url\tdepth\tratio\n")
        for url, depth, ratio in rows:
            f.write(f"{url}\t{depth}\t{ratio}\n")

# parser
def extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        try:
            absu = urljoin(base_url, a["href"]).split("#")[0]
            parts = urlparse(absu)
            if parts.scheme in ("http", "https"):
                links.append(absu)
        except Exception:
            pass
    return links

# The calc ratio of same-domain links
def same_domain_ratio(page_url: str, links: list[str]) -> float:
    page_host = urlparse(page_url).netloc
    hosts = [urlparse(l).netloc for l in links]
    if not hosts:
        return 0.0
    same = sum(1 for h in hosts if h == page_host)
    return same / len(hosts)


import os
import asyncio
import aiohttp
from typing import List, Tuple, Set, Callable


async def fetch_html(url: str, timeout: int = 15) -> str | None:
    try:
        async with aiohttp.ClientSession(headers={"User-Agent": "SimpleCrawler/1.0"}) as s:
            async with s.get(url, timeout=timeout) as r:
                ctype = (r.headers.get("Content-Type") or "").lower()
                if "text/html" not in ctype:
                    return None
                return await r.text()
    except Exception:
        return None


def main():
    # --- CLI parsing ---
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

    # --- quick sanity check (fetch root once) ---
    html = asyncio.run(fetch_html(root))
    print(f"Fetch root HTML: {'OK' if html else 'NO HTML'}")

    # --- full crawl ---
    rows = asyncio.run(crawl_bfs(root, depth))
    write_tsv(rows, out)
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
