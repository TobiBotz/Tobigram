import concurrent.futures
import html as html_module
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import socket
import time
import urllib.request

try:
    from bs4 import BeautifulSoup

    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util import Retry

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

HOME = Path(__file__).resolve().parent
ROOT = HOME
while ROOT.parent != ROOT and not (ROOT / "pyproject.toml").exists():
    ROOT = ROOT.parent

CACHE_DIR = ROOT / "scratch" / "core_cache"
INDEX_PATH = ROOT / "scratch" / "methods.html"
OUT_PATH = HOME / "docs.json"

for d in ("methods", "constructors", "types"):
    (CACHE_DIR / d).mkdir(parents=True, exist_ok=True)

# Force IPv4 to prevent Windows IPv6 DNS/connect delays
orig_getaddrinfo = socket.getaddrinfo


def getaddrinfo_ipv4(*args, **kwargs):
    return [r for r in orig_getaddrinfo(*args, **kwargs) if r[0] == socket.AF_INET]


socket.getaddrinfo = getaddrinfo_ipv4


def camel(s: str) -> str:
    return "".join([i[0].upper() + i[1:] for i in s.split("_")])


if HAS_REQUESTS:

    def get_session():
        s = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(pool_connections=40, pool_maxsize=40, max_retries=retries)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        return s

    SESSION = get_session()

    def fetch_url(url: str, cache_file: Path) -> str:
        if cache_file.exists() and cache_file.stat().st_size > 0:
            with open(cache_file, encoding="utf-8") as f:
                return f.read()
        try:
            r = SESSION.get(url, timeout=12)
            if r.status_code == 200:
                text = r.text
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(text)
                return text
            elif r.status_code == 404:
                return ""
        except Exception:
            pass
        return ""

else:

    def fetch_url(url: str, cache_file: Path) -> str:
        if cache_file.exists() and cache_file.stat().st_size > 0:
            with open(cache_file, encoding="utf-8") as f:
                return f.read()
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(text)
                return text
        except Exception:
            pass
        return ""


class StdLibDocParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_dev = False
        self.dev_depth = 0
        self.first_p_done = False
        self.in_first_p = False
        self.p_buffer = []
        self.in_table = False
        self.in_tr = False
        self.current_row = []
        self.current_td = []
        self.rows = []
        self.usable_by = None
        self.active_tags = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        tag_id = attr_dict.get("id", "")
        tag_class = attr_dict.get("class", "")

        if tag_id == "dev_page_content":
            self.in_dev = True
            self.dev_depth = 1
            return

        if self.in_dev:
            self.dev_depth += 1
            if tag_id == "only-users-can-use-this-method":
                self.usable_by = "users"
            elif tag_id == "only-bots-can-use-this-method":
                self.usable_by = "bots"
            elif tag_id in ("both-users-and-bots-can-use-this-method", "bots-can-use-this-method"):
                self.usable_by = "users-bots"

            if tag == "p" and not self.first_p_done and not self.in_table:
                if "clearfix" not in tag_class:
                    self.in_first_p = True

            if self.in_first_p:
                if tag in ("code", "tt"):
                    self.p_buffer.append(" ``")
                elif tag == "a":
                    href = attr_dict.get("href", "")
                    if href.startswith("/"):
                        href = "https://core.telegram.org" + href
                    elif not href.startswith("http"):
                        href = "https://core.telegram.org/" + href
                    self.p_buffer.append(" `")
                    self.active_tags.append(("a", href))
                    return
                elif tag in ("strong", "b"):
                    self.p_buffer.append(" **")
                elif tag in ("em", "i"):
                    self.p_buffer.append(" *")

            if tag == "table" and "table" in tag_class:
                self.in_table = True
            elif self.in_table and tag == "tr":
                self.in_tr = True
                self.current_row = []
            elif self.in_tr and tag == "td":
                self.current_td = []

    def handle_endtag(self, tag):
        if self.in_first_p:
            if tag in ("code", "tt"):
                self.p_buffer.append("`` ")
            elif tag == "a":
                if self.active_tags and self.active_tags[-1][0] == "a":
                    _, href = self.active_tags.pop()
                    self.p_buffer.append(f" <{href}>`_ ")
            elif tag in ("strong", "b"):
                self.p_buffer.append("** ")
            elif tag in ("em", "i"):
                self.p_buffer.append("* ")
            elif tag == "p":
                self.in_first_p = False
                self.first_p_done = True

        if self.in_table:
            if tag == "td":
                self.current_row.append("".join(self.current_td).strip())
            elif tag == "tr":
                if len(self.current_row) >= 3:
                    self.rows.append(self.current_row)
                self.in_tr = False
            elif tag == "table":
                self.in_table = False

        if self.in_dev:
            self.dev_depth -= 1
            if self.dev_depth <= 0:
                self.in_dev = False

    def handle_data(self, data):
        if self.in_first_p:
            self.p_buffer.append(data)
        if self.in_tr:
            self.current_td.append(data)


def html_to_rst(soup_or_elem) -> str:
    if not soup_or_elem:
        return ""
    elem = BeautifulSoup(str(soup_or_elem), "html.parser")

    # 1. Convert code tags
    for c in elem.find_all(["code", "tt"]):
        txt = c.get_text().strip().replace("`", "")
        if txt:
            c.replace_with(f" ``{txt}`` ")
        else:
            c.decompose()

    # 2. Convert a tags to Sphinx external hyperlinks
    for a in elem.find_all("a"):
        href = a.get("href", "").strip()
        txt = a.get_text().strip().replace("`", "")
        if not txt or not href:
            continue
        if href.startswith("/"):
            href = "https://core.telegram.org" + href
        elif not href.startswith("http"):
            href = "https://core.telegram.org/" + href
        a.replace_with(f" `{txt} <{href}>`_ ")

    # 3. Convert strong/b
    for s in elem.find_all(["strong", "b"]):
        txt = s.get_text().strip().replace("*", "")
        if txt:
            s.replace_with(f" **{txt}** ")

    # 4. Convert em/i
    for e in elem.find_all(["em", "i"]):
        txt = e.get_text().strip().replace("*", "")
        if txt:
            e.replace_with(f" *{txt}* ")

    text = elem.get_text()
    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text).strip()
    # Fix whitespace before punctuation: " ." -> ".", " ," -> ","
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text


def parse_doc_page(html: str):
    if not html:
        return "", {}, None

    if HAS_BS4:
        soup = BeautifulSoup(html, "html.parser")
        dev = soup.find("div", id="dev_page_content")
        if not dev:
            return "", {}, None

        # Description
        desc = ""
        for p in dev.find_all("p", recursive=False):
            if p.find("div", class_="clearfix") or p.find("pre") or p.find("table"):
                continue
            rst_desc = html_to_rst(p)
            if rst_desc:
                desc = rst_desc
                break

        # Parameters
        params = {}
        table = dev.find("table", class_="table")
        if table:
            tbody = table.find("tbody") or table
            for tr in tbody.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) >= 3:
                    name = tds[0].get_text().strip()
                    p_desc = html_to_rst(tds[2])
                    params[name] = p_desc
                    if name == "self":
                        params["is_self"] = p_desc
                    if name == "from":
                        params["from_peer"] = p_desc

        usable_by = None
        if dev.find(id="only-users-can-use-this-method"):
            usable_by = "users"
        elif dev.find(id="only-bots-can-use-this-method"):
            usable_by = "bots"
        elif dev.find(id="both-users-and-bots-can-use-this-method") or dev.find(
            id="bots-can-use-this-method"
        ):
            usable_by = "users-bots"

        return desc, params, usable_by

    else:
        parser = StdLibDocParser()
        parser.feed(html)
        desc = "".join(parser.p_buffer)
        desc = re.sub(r"[ \t]+", " ", desc).strip()
        desc = re.sub(r"\s+([.,;:!?])", r"\1", desc)
        params = {}
        for row in parser.rows:
            name = row[0].strip()
            p_desc = re.sub(r"[ \t]+", " ", row[2]).strip()
            params[name] = p_desc
            if name == "self":
                params["is_self"] = p_desc
            if name == "from":
                params["from_peer"] = p_desc
        return desc, params, parser.usable_by


def parse_schema_combinators():
    schema_paths = [
        HOME / "source" / "auth_key.tl",
        HOME / "source" / "sys_msgs.tl",
        HOME / "source" / "main_api.tl",
    ]
    lines = []
    for sp in schema_paths:
        if sp.exists():
            with open(sp, encoding="utf-8") as f:
                lines.extend(f.readlines())

    methods = {}  # qualname: tl_name
    constructors = {}  # qualname: tl_name
    types = {}  # qualtype: tl_type

    section = "types"
    combinator_re = re.compile(r"^([\w.]+)#[0-9a-f]+\s(?:.*)=\s([\w<>.]+);$")

    for line in lines:
        line = line.strip()
        if line.startswith("---"):
            m = re.match(r"---(\w+)---", line)
            if m:
                section = m.group(1)
            continue

        m = combinator_re.match(line)
        if not m:
            continue

        tl_name, qualtype = m.groups()
        ns, name = tl_name.split(".") if "." in tl_name else ("", tl_name)
        qualname = ".".join([ns, camel(name)]).lstrip(".")

        t_ns, t_name = qualtype.split(".") if "." in qualtype else ("", qualtype)
        compiled_type = ".".join([t_ns, camel(t_name)]).lstrip(".")

        if section == "functions":
            methods[qualname] = tl_name
        else:
            constructors[qualname] = tl_name
            if compiled_type and not compiled_type.startswith("Vector"):
                types[compiled_type] = qualtype

    return methods, constructors, types


def load_methods_index():
    if not INDEX_PATH.exists() or INDEX_PATH.stat().st_size == 0:
        try:
            INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
            fetch_url("https://core.telegram.org/methods", INDEX_PATH)
        except Exception:
            pass

    descriptions = {}
    if INDEX_PATH.exists() and INDEX_PATH.stat().st_size > 0:
        with open(INDEX_PATH, encoding="utf-8") as f:
            html = f.read()
        rows = re.findall(
            r'<tr>\s*<td><a href="/method/([^"]+)">(.*?)</a></td>\s*<td>(.*?)</td>\s*</tr>', html
        )
        for tl_name, disp, desc in rows:
            clean_desc = re.sub(r"<.*?>", "", desc).strip()
            clean_desc = re.sub(r"\s+", " ", clean_desc)
            clean_desc = html_module.unescape(clean_desc)
            ns, name = tl_name.split(".") if "." in tl_name else ("", tl_name)
            qualname = ".".join([ns, camel(name)]).lstrip(".")
            descriptions[qualname] = clean_desc
    return descriptions


def main():
    t0 = time.time()
    print("Parsing TL schema combinators...")
    methods, constructors, types = parse_schema_combinators()
    print(
        f"Found {len(methods)} methods, {len(constructors)} constructors, {len(types)} base types in schema."
    )

    method_index_descs = load_methods_index()
    print(f"Loaded {len(method_index_descs)} descriptions from core.telegram.org/methods index.")

    docs = {"type": {}, "constructor": {}, "method": {}}

    # Tasks to fetch: (category, key, url, cache_file)
    tasks = []
    for qualname, tl_name in methods.items():
        url = f"https://core.telegram.org/method/{tl_name}"
        cache_file = CACHE_DIR / "methods" / f"{tl_name}.html"
        tasks.append(("method", qualname, url, cache_file))

    for qualname, tl_name in constructors.items():
        url = f"https://core.telegram.org/constructor/{tl_name}"
        cache_file = CACHE_DIR / "constructors" / f"{tl_name}.html"
        tasks.append(("constructor", qualname, url, cache_file))

    for qualtype, tl_type in types.items():
        url = f"https://core.telegram.org/type/{tl_type}"
        cache_file = CACHE_DIR / "types" / f"{tl_type}.html"
        tasks.append(("type", qualtype, url, cache_file))

    total = len(tasks)
    print(f"Total items to fetch from core.telegram.org: {total}")

    def worker(task):
        cat, key, url, cache_file = task
        html = fetch_url(url, cache_file)
        desc, params, usable_by = parse_doc_page(html)
        return cat, key, desc, params, usable_by

    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as ex:
        futures = {ex.submit(worker, t): t for t in tasks}
        for f in concurrent.futures.as_completed(futures):
            cat, key, desc, params, usable_by = f.result()
            completed += 1
            if completed % 250 == 0 or completed == total:
                elapsed = time.time() - t0
                rate = completed / elapsed if elapsed > 0 else 0
                print(
                    f"Progress: {completed}/{total} ({completed * 100 // total}%) [{rate:.1f} items/sec]"
                )

            if cat == "method":
                # Fallback to methods index description if page didn't have one
                if not desc and key in method_index_descs:
                    desc = method_index_descs[key]
                docs["method"][key] = {"desc": desc, "params": params, "usable_by": usable_by}
            elif cat == "constructor":
                docs["constructor"][key] = {"desc": desc, "params": params}
            elif cat == "type":
                docs["type"][key] = {"desc": desc}

    # Save to docs.json
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)
    print(f"Saved {OUT_PATH} successfully ({OUT_PATH.stat().st_size // 1024} KB).")

    print(f"\nDone in {time.time() - t0:.1f}s!")
    print(
        f"Methods with descriptions: {sum(1 for v in docs['method'].values() if v.get('desc'))}/{len(docs['method'])}"
    )
    print(
        f"Methods with params: {sum(1 for v in docs['method'].values() if v.get('params'))}/{len(docs['method'])}"
    )
    print(
        f"Constructors with params: {sum(1 for v in docs['constructor'].values() if v.get('params'))}/{len(docs['constructor'])}"
    )
    print(
        f"Base types with descriptions: {sum(1 for v in docs['type'].values() if v.get('desc'))}/{len(docs['type'])}"
    )

    return docs


refresh = main

if __name__ == "__main__":
    main()
