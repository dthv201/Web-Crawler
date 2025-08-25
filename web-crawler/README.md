````markdown
# Web Crawler

A simple Python web crawler built with **asyncio** and **aiohttp**.

## Features
- Accepts a **root URL** and a **recursion depth limit** from the command line.
- Crawls pages up to the specified depth using a breadth-first search (BFS).
- For each page, calculates the **ratio of same-domain links** to all links on that page.
- Outputs results to a **TSV file** with three columns:  
  `Url   depth   ratio`
- Uses **asynchronous requests** to maximize performance.

## Requirements
- Python 3.10 or later
- Dependencies listed in `requirements.txt`:
  - [`aiohttp`](https://docs.aiohttp.org/) – async HTTP client
  - [`beautifulsoup4`](https://www.crummy.com/software/BeautifulSoup/) – HTML parser

## Setup
1. Clone the repository:
   ```bash
   git clone <your_repo_url>
   cd web-crawler
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Git Bash:
   source venv/Scripts/activate
   # PowerShell:
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the crawler from the command line:
```bash
python crawler.py <root_url> <depth> [output_file]
```

- `<root_url>` → the starting page (e.g. `https://www.wikipedia.org`)  
- `<depth>` → recursion depth limit (0 = only root, 1 = root + its links, etc.)  
- `[output_file]` → optional; defaults to `crawl.tsv`

### Example
```bash
python crawler.py https://www.wikipedia.org 1 results.tsv
```

## Output
The crawler produces a tab-separated values (TSV) file. Each row represents one visited page:

```
Url     depth   ratio
https://www.wikipedia.org     0     0.42
https://en.wikipedia.org/     1     0.61
https://es.wikipedia.org/     1     0.58
```

- **Url** → the page visited  
- **depth** → how far it was from the root  
- **ratio** → fraction of links that share the same domain as the page  

---

````

👉 Save this as `README.md`, then commit:

```bash
git add README.md
git commit -m "docs: polish project README"
```


