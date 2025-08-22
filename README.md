

````markdown
# Web Crawler

A simple Python web crawler built for practice.

## Features
- Takes a **root URL** and a **recursion depth** from the command line.
- Crawls pages up to the given depth.
- For each page, calculates the **ratio of same-domain links** it contains.
- Outputs results to a **TSV file** with columns: `Url   depth   ratio`.
- Uses **asyncio + aiohttp** for concurrency to maximize performance.

## Requirements
- Python 3.10+
- Dependencies listed in `requirements.txt`:
  - `aiohttp`
  - `beautifulsoup4`

## Setup
1. Clone the repository:
   ```bash
   git clone <your_repo_url>
   cd web-crawler
````

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

Run the crawler:

```bash
python crawler.py <root_url> <depth> [output_file]
```

Example:

```bash
python crawler.py https://www.wikipedia.org 1 results.tsv
```

## Output

The output TSV will contain lines like:

```
Url     depth   ratio
https://www.wikipedia.org     0     0.42
```

---

````

---

👉 After you save this as `README.md`, run:

```bash
git add README.md
git commit -m "docs: add project README"
````
