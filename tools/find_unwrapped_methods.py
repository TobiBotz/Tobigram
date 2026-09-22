#!/usr/bin/env python3
"""Tool to find official Telegram methods and functions that are NOT YET implemented

in Tobigram's high-level Client API (pyrogram.Client.*).

Checks:
1. Telegram Bot API methods (core.telegram.org/bots/api) missing high-level wrappers.
2. Telegram MTProto functions (schema.tl) missing high-level wrappers.

Usage:
    python tools/find_unwrapped_methods.py
    python tools/find_unwrapped_methods.py --botapi
    python tools/find_unwrapped_methods.py --mtproto
    python tools/find_unwrapped_methods.py --namespace stories
    python tools/find_unwrapped_methods.py --namespace channels
    python tools/find_unwrapped_methods.py --search topic
    python tools/find_unwrapped_methods.py --details channels.getForumTopics
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "compiler" / "botapi"))

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from coverage import Coverage, to_snake_case


def load_tl_functions() -> dict[str, dict]:
    """Parse MTProto functions from TL schema."""
    tl_source = ROOT / "compiler" / "api" / "source" / "main_api.tl"
    spec = importlib.util.spec_from_file_location(
        "methods_compiler", ROOT / "compiler" / "methods" / "compiler.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_tl_functions(tl_source)


def get_unwrapped_botapi(cov: Coverage) -> list[dict]:
    """Find Bot API methods that have no high-level wrapper in pyrogram."""
    unwrapped = []
    spec_methods = cov.spec.get("methods", {})
    botapi = cov.aliases.get("botapi") or {}
    unsupported = botapi.get("method_unsupported") or {}

    for name, data in sorted(spec_methods.items()):
        if name in unsupported:
            continue
        symbol = cov.tobigram_method(name)
        desc = data.get("description")
        desc_str = desc[0] if isinstance(desc, list) and desc else (str(desc) if desc else "")
        if symbol is None:
            unwrapped.append(
                {
                    "name": name,
                    "snake_name": to_snake_case(name),
                    "description": desc_str,
                    "fields": [f["name"] for f in data.get("fields", [])],
                }
            )

    return unwrapped


def get_unwrapped_mtproto(cov: Coverage, tl_funcs: dict[str, dict]) -> list[dict]:
    """Find MTProto raw functions that are not invoked by any high-level client method."""
    covered_raw = set()
    for sym in cov.methods.values():
        covered_raw.update(sym.raw_calls)

    aliases = cov.aliases.get("mtproto", {}).get("raw_function", {})
    for high_level_name, raw_name in aliases.items():
        covered_raw.add(raw_name)

    unwrapped = []
    for full_name, data in sorted(tl_funcs.items()):
        if full_name not in covered_raw:
            parts = full_name.split(".", 1)
            namespace = parts[0] if len(parts) == 2 else "root"
            func_name = parts[1] if len(parts) == 2 else parts[0]

            unwrapped.append(
                {
                    "full_name": full_name,
                    "namespace": namespace,
                    "func_name": func_name,
                    "params": [p["name"] for p in data.get("params", [])],
                    "type": data.get("type", "Object"),
                }
            )

    return unwrapped


def categorize_botapi_method(name: str) -> str:
    """Categorize Bot API method by feature area."""
    n = name.lower()
    if "forumtopic" in n:
        return "Forum Topics"
    if "business" in n:
        return "Telegram Business"
    if "sticker" in n:
        return "Stickers & Custom Emoji"
    if "verification" in n or "verify" in n:
        return "Verification"
    if "webhook" in n:
        return "Webhooks"
    if "prepared" in n or "inlinemessage" in n:
        return "Mini Apps"
    if "story" in n:
        return "Stories"
    if "admin" in n or "profilephoto" in n or "bot" in n:
        return "Bot Management"
    if "chat" in n:
        return "Chats & Groups"
    return "Messages & General"


def display_botapi(unwrapped: list[dict], search: str | None = None):
    filtered = unwrapped
    if search:
        s = search.lower()
        filtered = [m for m in filtered if s in m["name"].lower() or s in m["description"].lower()]

    by_cat = defaultdict(list)
    for m in filtered:
        cat = categorize_botapi_method(m["name"])
        by_cat[cat].append(m)

    print(f"\n=======================================================")
    print(f"  BOT API METHODS NOT IN HIGH-LEVEL ({len(filtered)} methods)")
    print(f"=======================================================")

    for cat in sorted(by_cat):
        methods = by_cat[cat]
        print(f"\n--- [{cat}] ({len(methods)} methods) ---")
        for m in methods:
            params_str = ", ".join(m["fields"]) if m["fields"] else "None"
            print(f"  * {m['name']}  ->  suggested: client.{m['snake_name']}()")
            print(f"    Params: {params_str}")
            if m["description"]:
                print(f"    Desc:   {m['description'][:85]}...")


def display_mtproto(
    unwrapped: list[dict],
    namespace: str | None = None,
    search: str | None = None,
):
    filtered = unwrapped
    if namespace:
        filtered = [f for f in filtered if f["namespace"].lower() == namespace.lower()]
    if search:
        s = search.lower()
        filtered = [f for f in filtered if s in f["full_name"].lower()]

    by_ns = defaultdict(list)
    for f in filtered:
        by_ns[f["namespace"]].append(f)

    print(f"\n=======================================================")
    print(f"  MTPROTO RAW FUNCTIONS NOT IN HIGH-LEVEL ({len(filtered)} found)")
    print(f"=======================================================")

    for ns in sorted(by_ns):
        funcs = by_ns[ns]
        print(f"\n[Namespace: {ns}] ({len(funcs)} functions):")
        for f in funcs:
            params_str = ", ".join(f["params"]) if f["params"] else "None"
            print(f"  * {f['full_name']}({params_str}) -> {f['type']}")


def show_details(name: str, tl_funcs: dict[str, dict], cov: Coverage):
    print(f"\n=======================================================")
    print(f"  DETAILS FOR: {name}")
    print(f"=======================================================")

    # Check in Bot API
    spec_methods = cov.spec.get("methods", {})
    if name in spec_methods or to_snake_case(name) in [to_snake_case(m) for m in spec_methods]:
        bot_key = name if name in spec_methods else next(m for m in spec_methods if to_snake_case(m) == to_snake_case(name))
        data = spec_methods[bot_key]
        print(f"Source: Telegram Bot API ({bot_key})")
        d = data.get('description', '')
        d_str = ' '.join(d) if isinstance(d, list) else str(d)
        print(f"Description: {d_str}")
        print("Parameters:")
        for f in data.get("fields", []):
            req = "[Required]" if f.get("required") else "[Optional]"
            print(f"  - {f['name']} ({f.get('type')}): {req} {f.get('description', '')[:70]}")
        return

    # Check in MTProto
    matched = None
    for fn, data in tl_funcs.items():
        if fn.lower() == name.lower() or fn.split(".")[-1].lower() == name.lower():
            matched = (fn, data)
            break

    if matched:
        fn, data = matched
        print(f"Source: MTProto TL Schema ({fn})")
        print(f"Returns: {data.get('type')}")
        print("Parameters:")
        for p in data.get("params", []):
            print(f"  - {p['name']}: {p.get('type')}")
        return

    print(f"[-] '{name}' not found in Bot API or MTProto specifications.")


def main():
    parser = argparse.ArgumentParser(
        description="Find official Telegram methods not yet implemented in high-level Pyrogram/Tobigram."
    )
    parser.add_argument("--botapi", action="store_true", help="Show missing Bot API methods")
    parser.add_argument("--mtproto", action="store_true", help="Show unwrapped MTProto functions")
    parser.add_argument("--namespace", "-n", help="Filter MTProto by namespace (e.g. channels, messages, stories)")
    parser.add_argument("--search", "-s", help="Search keyword across missing methods")
    parser.add_argument("--details", "-d", help="Show parameter details for a specific missing function")

    args = parser.parse_args()
    cov = Coverage()
    tl_funcs = load_tl_functions()

    if args.details:
        show_details(args.details, tl_funcs, cov)
        return

    unwrapped_bot = get_unwrapped_botapi(cov)
    unwrapped_mt = get_unwrapped_mtproto(cov, tl_funcs)

    if args.namespace:
        display_mtproto(unwrapped_mt, namespace=args.namespace, search=args.search)
        return

    if args.botapi:
        display_botapi(unwrapped_bot, search=args.search)
        return

    if args.mtproto:
        display_mtproto(unwrapped_mt, search=args.search)
        return

    if args.search:
        display_botapi(unwrapped_bot, search=args.search)
        display_mtproto(unwrapped_mt, search=args.search)
        return

    # Default Overview Summary
    print("\n=======================================================")
    print("  OFFICIAL TELEGRAM METHODS MISSING HIGH-LEVEL WRAPPERS")
    print("=======================================================")
    print(f"Total High-Level Client Methods Implemented: {len(cov.methods)}")
    print(f"\n1. Bot API Methods without high-level wrapper: {len(unwrapped_bot)}")
    print(f"2. MTProto Functions without high-level wrapper: {len(unwrapped_mt)}")

    print("\nTop MTProto Namespaces with unwrapped functions:")
    by_ns = defaultdict(int)
    for f in unwrapped_mt:
        by_ns[f["namespace"]] += 1
    for ns, count in sorted(by_ns.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {ns:15} : {count} functions")

    print("\nQuick Usage Examples:")
    print("  python tools/find_unwrapped_methods.py --botapi")
    print("  python tools/find_unwrapped_methods.py --namespace stories")
    print("  python tools/find_unwrapped_methods.py --namespace channels")
    print("  python tools/find_unwrapped_methods.py --search topic")
    print("  python tools/find_unwrapped_methods.py --details channels.getForumTopics")


if __name__ == "__main__":
    main()
