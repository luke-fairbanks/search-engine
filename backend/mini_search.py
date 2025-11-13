#!/usr/bin/env python3

"""
mini_search.py — debug TLS build
- Uses certifi CA bundle automatically if installed
- --insecure to skip TLS verification (dev only)
- robots.txt fetched via our fetch() with the same SSL context
"""

from __future__ import annotations
import argparse, collections, contextlib, dataclasses, html, io, json, math, os, queue, random, re, sys, time
import urllib.parse, urllib.request, urllib.error, urllib.robotparser
from html.parser import HTMLParser
from typing import Dict, List, Tuple, Iterable, Set, Optional
import ssl

def make_ssl_context(insecure: bool, verbose: bool) -> ssl.SSLContext:
    if insecure:
        if verbose:
            print("[tls] insecure mode enabled: certificate verification DISABLED")
        return ssl._create_unverified_context()
    # Try certifi first (helps on macOS/Homebrew Pythons)
    cafile: Optional[str] = None
    try:
        import certifi  # type: ignore
        cafile = certifi.where()
    except Exception:
        cafile = None
    if cafile:
        if verbose:
            print(f"[tls] using certifi bundle: {cafile}")
        return ssl.create_default_context(cafile=cafile)
    # Fallback to system defaults
    if verbose:
        print("[tls] using system default CA bundle")
    return ssl.create_default_context()

def norm_url(u: str, base: str | None = None) -> str:
    try:
        if base:
            u = urllib.parse.urljoin(base, u)
        pu = urllib.parse.urlsplit(u)
        netloc = pu.netloc.lower()
        if (pu.scheme == "http" and netloc.endswith(":80")) or (pu.scheme == "https" and netloc.endswith(":443")):
            netloc = netloc.rsplit(":", 1)[0]
        path = pu.path or "/"
        path = urllib.parse.urljoin("/", path)
        query = "&".join(sorted(filter(None, pu.query.split("&"))))
        return urllib.parse.urlunsplit((pu.scheme.lower(), netloc, path, query, ""))
    except Exception:
        return ""

def host_only(u: str) -> str:
    try:
        return urllib.parse.urlsplit(u).netloc.split(":")[0].lower()
    except Exception:
        return ""

def same_domain(a: str, b: str) -> bool:
    try:
        return host_only(a) == host_only(b)
    except Exception:
        return False

# include subdomains: *.root
def same_reg_domain(a: str, b: str) -> bool:
    try:
        ha, hb = host_only(a), host_only(b)
        # naive registrable domain: last two labels (good for .org/.com etc.)
        def root(h):
            parts = h.split('.')
            return '.'.join(parts[-2:]) if len(parts) >= 2 else h
        return root(ha) == root(hb)
    except Exception:
        return False

def sleep_polite(last_fetch_time: Dict[str, float], host: str, delay: float = 1.0):
    now = time.time()
    t = last_fetch_time.get(host, 0.0)
    wait = (t + delay) - now
    if wait > 0:
        time.sleep(wait)

def fetch(url: str, ctx: ssl.SSLContext, user_agent: str = "mini-search-bot/0.1 (+contact: you@example.com)", timeout: float = 12.0) -> Tuple[int, bytes, Dict[str, str], str]:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with contextlib.closing(urllib.request.urlopen(req, timeout=timeout, context=ctx)) as resp:
        code = resp.getcode() or 0
        data = resp.read()
        headers = {k.lower(): v for k, v in resp.headers.items()}
        final_url = resp.geturl()
        return code, data, headers, final_url

class LinkAndTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: List[str] = []
        self._texts: List[str] = []
        self._skip_stack: List[str] = []
        self._title: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip_stack.append(tag)
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)
        if tag == "title":
            self._title.append("")

    def handle_endtag(self, tag):
        if self._skip_stack and self._skip_stack[-1] == tag:
            self._skip_stack.pop()

    def handle_data(self, data):
        if self._skip_stack:
            return
        if self._title and (not any(self._title)):
            self._title[0] += data
        else:
            s = data.strip()
            if s:
                self._texts.append(s)

    @property
    def title(self) -> str:
        return (self._title[0].strip() if self._title else "")

    @property
    def text(self) -> str:
        return " ".join(self._texts)

def parse_html(raw: bytes, encoding_hint: str | None = None) -> Tuple[str, str, List[str]]:
    enc = (encoding_hint or "").split("charset=")[-1].strip() if encoding_hint else ""
    if not enc:
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            enc = "utf-16"
        else:
            enc = "utf-8"
    try:
        html_text = raw.decode(enc, errors="ignore")
    except LookupError:
        html_text = raw.decode("utf-8", errors="ignore")
    p = LinkAndTextExtractor()
    p.feed(html_text)
    return p.title or "", p.text, p.links

TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
def tokenize(s: str) -> List[str]:
    return [t.lower() for t in TOKEN_RE.findall(s)]

def try_seed_sitemap(start_url: str, ctx, user_agent: str, verbose: bool):
    # Try /sitemap.xml and enqueue <loc> links that match scope
    import xml.etree.ElementTree as ET
    base = urllib.parse.urlunsplit((urllib.parse.urlsplit(start_url).scheme, host_only(start_url), '', '', ''))
    sitemap = urllib.parse.urljoin(base, "/sitemap.xml")
    try:
        code, data, headers, final_url = fetch(sitemap, ctx=ctx, user_agent=user_agent)
        if 200 <= code < 300 and b"<loc>" in data[:200000]:
            if verbose:
                print(f"[sitemap] loaded {sitemap} ({len(data)} bytes)")
            # Strip any namespaces for simplicity
            try:
                tree = ET.fromstring(data.decode('utf-8', errors='ignore'))
            except Exception:
                return []
            urls = []
            for loc in tree.iter():
                tag = loc.tag.split('}')[-1]
                if tag.lower() == 'loc' and loc.text:
                    u = norm_url(loc.text.strip())
                    if u:
                        urls.append(u)
            if verbose:
                print(f"[sitemap] found {len(urls)} URLs")
            return urls[:5000]  # cap
    except Exception as e:
        if verbose:
            print(f"[sitemap] error: {e}")
    return []

@dataclasses.dataclass
class Document:
    url: str
    title: str
    length: int
    snippet: str

def crawl(start_url: str, max_pages: int, out_dir: str, user_agent: str, verbose: bool, insecure: bool, scope: str, seed_smap: bool):
    os.makedirs(out_dir, exist_ok=True)
    pages_dir = os.path.join(out_dir, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    start_url = norm_url(start_url)
    if not start_url:
        print("Invalid start URL")
        return

    start_host = host_only(start_url)
    ctx = make_ssl_context(insecure=insecure, verbose=verbose)

    # robots: fetch using our TLS context
    rp = urllib.robotparser.RobotFileParser()
    robots_url = urllib.parse.urljoin(f"{urllib.parse.urlsplit(start_url).scheme}://{start_host}", "/robots.txt")
    robots_ok = False
    try:
        code, data, headers, final_url = fetch(robots_url, ctx=ctx, user_agent=user_agent)
        if 200 <= code < 300 and same_domain(final_url, start_url):
            txt = data.decode("utf-8", errors="ignore")
            rp.parse(txt.splitlines())
            robots_ok = True
            if verbose:
                print(f"[crawl] robots: {robots_url} loaded=True")
        else:
            if verbose:
                print(f"[crawl] robots: load failed code={code} redirected_to={final_url}")
    except Exception as e:
        if verbose:
            print(f"[crawl] robots: error {e} (default allow)")

    def allowed(u: str) -> bool:
        if robots_ok:
            ok = rp.can_fetch("*", u)
            if verbose and not ok:
                print(f"[robots] disallow: {u}")
            return ok
        return True

    q = queue.Queue()
    q.put(start_url)
    if seed_smap:
        sm_urls = try_seed_sitemap(start_url, ctx=ctx, user_agent=user_agent, verbose=verbose)
        for u in sm_urls:
            q.put(u)
    seen: Set[str] = set()
    last_fetch_time: Dict[str, float] = {}

    fetched = 0
    while not q.empty() and fetched < max_pages:
        url = q.get()
        if url in seen:
            continue
        seen.add(url)

        allowed_host = same_domain if scope == 'host' else same_reg_domain
        if not allowed_host(url, start_url):
            if verbose:
                print(f"[skip] cross-domain: {url}")
            continue
        if not allowed(url):
            continue

        host = host_only(url)
        sleep_polite(last_fetch_time, host, delay=0.75)
        try:
            code, data, headers, final_url = fetch(url, ctx=ctx, user_agent=user_agent, timeout=12.0)
            last_fetch_time[host] = time.time()
        except Exception as e:
            if verbose:
                print(f"[error] fetch {url}: {e}")
            continue

        if not allowed_host(final_url, start_url):
            if verbose:
                print(f"[skip] redirected to other domain: {final_url}")
            continue

        ctype = headers.get("content-type", "")
        if "text/html" not in ctype:
            if verbose:
                print(f"[skip] non-HTML content-type for {url}: {ctype}")
            continue

        title, text, links = parse_html(data, headers.get("content-type"))
        if not text.strip():
            if verbose:
                print(f"[skip] empty text: {url}")
            continue

        doc = {
            "url": norm_url(final_url),
            "title": title,
            "text": text,
            "outlinks": [norm_url(h, base=final_url) for h in links if h],
        }
        with open(os.path.join(pages_dir, f"{fetched}.json"), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)

        fetched += 1
        if verbose:
            print(f"[ok] {fetched}: {doc['url']} (title='{title[:60]}')")
        random.shuffle(doc["outlinks"])
        enq = 0
        for h in doc["outlinks"]:
            if h and allowed_host(h, start_url) and (h not in seen) and allowed(h):
                q.put(h)
                enq += 1
        if verbose:
            print(f"[queue] enqueued {enq} outlinks from this page")

        if fetched % 50 == 0 and verbose:
            print(f"[crawl] fetched {fetched}/{max_pages}")

    with open(os.path.join(out_dir, "crawl_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"start_url": start_url, "fetched": fetched}, f)
    print(f"[crawl] done: {fetched} pages")

def build(out_dir: str):
    pages_dir = os.path.join(out_dir, "pages")
    if not os.path.isdir(pages_dir):
        print("[build] no pages/ directory found")
        return
    files = sorted([os.path.join(pages_dir, fn) for fn in os.listdir(pages_dir) if fn.endswith(".json")])
    if not files:
        print("[build] no page JSON files found")
        return

    postings: Dict[str, Dict[int, int]] = collections.defaultdict(lambda: collections.defaultdict(int))
    doclen: Dict[int, int] = {}
    docs: Dict[int, Document] = {}
    graph: Dict[int, List[int]] = collections.defaultdict(list)
    url_to_id: Dict[str, int] = {}

    for i, fp in enumerate(files):
        with open(fp, "r", encoding="utf-8") as f:
            d = json.load(f)
        url_to_id[d["url"]] = i

    for i, fp in enumerate(files):
        with open(fp, "r", encoding="utf-8") as f:
            d = json.load(f)
        title = d.get("title", "")
        text = d.get("text", "")
        toks = tokenize(title + " " + text)
        doclen[i] = len(toks)
        snippet = " ".join(toks[:30])
        docs[i] = Document(url=d["url"], title=title.strip() or d["url"], length=len(toks), snippet=snippet)

        cnt = collections.Counter(toks)
        for t, tf in cnt.items():
            postings[t][i] = tf

        outs = []
        for u in d.get("outlinks", []):
            uid = url_to_id.get(u)
            if uid is not None:
                outs.append(uid)
        graph[i] = outs

    N = max(doclen.keys(), default=-1) + 1
    df = {t: len(ds) for t, ds in postings.items()}
    idf = {t: math.log(1 + (N - df_t + 0.5) / (df_t + 0.5)) for t, df_t in df.items()}
    avgdl = (sum(doclen.values()) / N) if N else 0.0

    pr = pagerank(graph, N, gamma=0.85, tol=1e-6, max_iter=100)

    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump({
            "idf": idf,
            "avgdl": avgdl,
            "doclen": doclen,
            "docs": {k: dataclasses.asdict(v) for k, v in docs.items()},
        }, f)

    with open(os.path.join(out_dir, "postings.jsonl"), "w", encoding="utf-8") as f:
        for t, ds in postings.items():
            f.write(json.dumps({"t": t, "ds": ds}, ensure_ascii=False) + "\n")

    with open(os.path.join(out_dir, "pagerank.json"), "w", encoding="utf-8") as f:
        json.dump(pr, f)

    print(f"[build] N={N}, vocab={len(postings)} avgdl={avgdl:.2f}")

def pagerank(outlinks: Dict[int, List[int]], n: int, gamma: float = 0.85, tol: float = 1e-6, max_iter: int = 100) -> Dict[int, float]:
    N = n
    if N == 0:
        return {}
    pr = {i: 1.0 / N for i in range(N)}
    outdeg = {i: len(outlinks.get(i, [])) for i in range(N)}
    for _ in range(max_iter):
        sink_sum = sum(pr[i] for i in range(N) if outdeg.get(i, 0) == 0)
        base = (1.0 - gamma) / N
        sink_add = gamma * sink_sum / N
        new = {i: base + sink_add for i in range(N)}
        for j, outs in outlinks.items():
            if not outs:
                continue
            w = gamma * pr[j] / len(outs)
            for i in outs:
                new[i] += w
        delta = sum(abs(new[i] - pr[i]) for i in range(N))
        pr = new
        if delta < tol:
            break
    return pr

def bm25_scores(query_terms: List[str], idf: Dict[str, float], postings_iter: Iterable[Tuple[str, Dict[int, int]]], doclen: Dict[int, int], avgdl: float, k1: float = 1.2, b: float = 0.75) -> Dict[int, float]:
    scores: Dict[int, float] = collections.defaultdict(float)
    terms = [t for t in query_terms if t in idf]
    if not terms:
        return {}
    for term, plist in postings_iter:
        if term not in terms:
            continue
        idf_t = idf[term]
        for d, tf in plist.items():
            denom = tf + k1 * (1.0 + b * ((doclen[d] / (avgdl or 1.0)) - 1.0))
            scores[d] += idf_t * (tf * (k1 + 1.0)) / (denom or 1e-9)
    return scores

def load_postings(out_dir: str) -> Iterable[Tuple[str, Dict[int, int]]]:
    with open(os.path.join(out_dir, "postings.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            yield row["t"], {int(k): int(v) for k, v in row["ds"].items()}

def load_index(out_dir: str):
    with open(os.path.join(out_dir, "index.json"), "r", encoding="utf-8") as f:
        idx = json.load(f)
    with open(os.path.join(out_dir, "pagerank.json"), "r", encoding="utf-8") as f:
        pr = json.load(f)
    idx["doclen"] = {int(k): int(v) for k, v in idx["doclen"].items()}
    idx["docs"] = {int(k): Document(**v) for k, v in idx["docs"].items()}
    pr = {int(k): float(v) for k, v in pr.items()}
    return idx, pr

def hybrid_rank(query: str, out_dir: str, alpha: float, beta: float, k: int = 10, title_boost: float = 0.5):
    idx, pr = load_index(out_dir)
    qterms = tokenize(query)
    bm = bm25_scores(qterms, idx["idf"], load_postings(out_dir), idx["doclen"], idx["avgdl"])
    if not bm:
        return []
    if pr:
        vals = list(pr.values())
        mn, mx = min(vals), max(vals)
    else:
        mn, mx = 0.0, 1.0
    def pr_norm(d):
        if mx - mn < 1e-12:
            return 0.0
        return (pr.get(d, 0.0) - mn) / (mx - mn)

    # Calculate title match bonus
    def title_match_score(d):
        """Give bonus if query terms appear in title or URL"""
        doc = idx["docs"][d]
        title_lower = doc.title.lower()
        url_lower = doc.url.lower()
        title_tokens = set(tokenize(title_lower))

        matches = 0
        for qt in qterms:
            # Exact token match in title
            if qt in title_tokens:
                matches += 1
            # Substring match in title (e.g., "for" in "forloop")
            elif any(qt in token for token in title_tokens):
                matches += 0.8  # Slightly lower weight for substring
            # Substring match in URL path (e.g., "ForLoop" in URL)
            elif qt in url_lower:
                matches += 0.6  # Even lower for URL match

        if matches == 0:
            return 0.0
        # Full match: all query terms found = full boost
        # Partial match: some terms = proportional boost
        return title_boost * (matches / len(qterms))

    # Combine BM25, PageRank, and title boost
    scores = {d: bm[d] * (alpha + beta * pr_norm(d) + title_match_score(d)) for d in bm}
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
    return [(idx["docs"][d], s) for d, s in top]

def cmd_crawl(args):
    crawl(args.start, args.max_pages, args.out, user_agent=args.user_agent, verbose=args.verbose, insecure=args.insecure, scope=args.scope, seed_smap=args.seed_sitemap)

def cmd_build(args):
    build(args.data)

def cmd_search(args):
    alpha, beta = args.alpha, args.beta
    print(f"[search] data={args.data}  alpha={alpha}  beta={beta}")
    print("Type a query (or 'exit')")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q or q.lower() in {"exit", "quit"}:
            break
        results = hybrid_rank(q, args.data, alpha, beta, k=args.k)
        if not results:
            print("No results.")
            continue
        for rank, (doc, score) in enumerate(results, start=1):
            print(f"{rank}. {doc.title[:100]}")
            print(f"   {doc.url}")
            print(f"   score={score:.4f}")
            print(f"   {doc.snippet[:180]}...")
        print()

def main():
    ap = argparse.ArgumentParser(description="Mini search engine (crawl → index → PageRank → search)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_crawl = sub.add_parser("crawl", help="crawl a site and save raw pages")
    ap_crawl.add_argument("--start", required=True, help="start URL (e.g., https://www.python.org)")
    ap_crawl.add_argument("--max-pages", type=int, default=1000, help="maximum pages to fetch")
    ap_crawl.add_argument("--out", required=True, help="output directory (e.g., ./data)")
    ap_crawl.add_argument("--user-agent", type=str, default="mini-search-bot/1.0 (+contact: you@example.com)", help="override User-Agent header")
    ap_crawl.add_argument("--verbose", action="store_true", help="verbose logging")
    ap_crawl.add_argument("--insecure", action="store_true", help="DISABLE TLS verification (dev only)")
    ap_crawl.add_argument("--scope", choices=["host","domain"], default="host", help="crawl scope: host (exact host) or domain (include subdomains)")
    ap_crawl.add_argument("--seed-sitemap", dest="seed_sitemap", action="store_true", help="seed frontier from /sitemap.xml if available")
    ap_crawl.set_defaults(func=cmd_crawl)

    ap_build = sub.add_parser("build", help="build inverted index + pagerank from saved pages")
    ap_build.add_argument("--data", required=True, help="output directory used in crawl")
    ap_build.set_defaults(func=cmd_build)

    ap_search = sub.add_parser("search", help="interactive BM25×PageRank search")
    ap_search.add_argument("--data", required=True, help="output directory used in crawl/build")
    ap_search.add_argument("--alpha", type=float, default=0.2, help="floor for PR blending")
    ap_search.add_argument("--beta", type=float, default=0.8, help="weight for PageRank")
    ap_search.add_argument("--k", type=int, default=10, help="top-k results")
    ap_search.set_defaults(func=cmd_search)

    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
