#!/usr/bin/env python3
"""CLI tool to audit Tobigram methods and types against official Telegram API specifications.

Compares parameters and fields against:
1. Official Telegram Bot API spec (compiler/botapi/source/botapi.json)
2. Telegram MTProto TL Schema (compiler/api/source/main_api.tl)

Usage:
    python tools/check_api_params.py --method ban_chat_member
    python tools/check_api_params.py --method send_photo
    python tools/check_api_params.py --type Message
    python tools/check_api_params.py --all
    python tools/check_api_params.py --diff
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "compiler" / "botapi"))

from coverage import Coverage


def format_status(status_bool: bool) -> str:
    return "[MATCH]" if status_bool else "[GAP]"


def audit_method(cov: Coverage, name: str, verbose: bool = True) -> bool:
    # Match both camelCase (Bot API) and snake_case (Tobigram)
    spec_methods = cov.spec.get("methods", {})

    target_botapi = None
    if name in spec_methods:
        target_botapi = name
    else:
        # Search via tobigram_method or method_rename
        for m_name in spec_methods:
            symbol = cov.tobigram_method(m_name)
            if symbol and (symbol.name == name or m_name.lower() == name.lower().replace("_", "")):
                target_botapi = m_name
                break

    if not target_botapi:
        # Check if it's a pure MTProto method in Tobigram
        symbol = None
        for m_name in spec_methods:
            s = cov.tobigram_method(m_name)
            if s and s.name == name:
                symbol = s
                break
        if not symbol:
            print(f"[-] Method '{name}' not found in Bot API spec or mapped Tobigram methods.")
            return False

    botapi_name = target_botapi
    symbol = cov.tobigram_method(botapi_name) if botapi_name else None
    botapi_gaps = cov.method_botapi_gaps(botapi_name) if botapi_name else []
    mtproto_gaps = cov.method_mtproto_gaps(botapi_name) if botapi_name else []

    spec_method = spec_methods.get(botapi_name, {})
    official_params = [f["name"] for f in spec_method.get("fields", [])]
    tobigram_params = sorted(symbol.params) if symbol else []

    print(f"\n=======================================================")
    print(f"  Method Audit: {name} (Bot API: {botapi_name})")
    print(f"=======================================================")
    print(f"  Tobigram Method:   pyrogram.Client.{symbol.name if symbol else 'None'}")
    print(f"  Official Bot API:  https://core.telegram.org/bots/api#{botapi_name.lower() if botapi_name else ''}")
    print(f"  Official Params:   {', '.join(official_params) if official_params else 'None'}")
    print(f"  Tobigram Params:   {', '.join(tobigram_params) if tobigram_params else 'None'}")

    has_gaps = bool(botapi_gaps or mtproto_gaps)
    if not has_gaps:
        print(f"\n  Result: [OK] All parameters accounted for!")
    else:
        print(f"\n  Result: [WARNING] Missing / Gap parameters found:")
        if botapi_gaps:
            print(f"    - Missing from Bot API spec: {botapi_gaps}")
        if mtproto_gaps:
            print(f"    - Missing from MTProto TL schema: {mtproto_gaps}")

    return not has_gaps


def audit_type(cov: Coverage, name: str) -> bool:
    spec_types = cov.spec.get("types", {})
    target_type = None

    if name in spec_types:
        target_type = name
    else:
        for t_name in spec_types:
            sym = cov.tobigram_type(t_name)
            if sym and (sym.name == name or t_name.lower() == name.lower()):
                target_type = t_name
                break

    if not target_type:
        print(f"[-] Type '{name}' not found in Bot API spec.")
        return False

    spec_type = spec_types.get(target_type, {})
    official_fields = [f["name"] for f in spec_type.get("fields", [])]
    sym = cov.tobigram_type(target_type)
    gaps = cov.type_gaps(target_type)

    print(f"\n=======================================================")
    print(f"  Type Audit: {name} (Bot API: {target_type})")
    print(f"=======================================================")
    print(f"  Tobigram Class:    {sym.name if sym else 'None'}")
    print(f"  File Path:         {sym.path if sym else 'None'}")
    print(f"  Official Fields:   {', '.join(official_fields) if official_fields else 'None'}")
    print(f"  Missing Fields:    {', '.join(gaps) if gaps else 'None (100% matched)'}")
    return not bool(gaps)


def audit_all(cov: Coverage, diff_only: bool = False):
    spec_methods = cov.spec.get("methods", {})
    spec_types = cov.spec.get("types", {})

    print(f"\nAuditing against Official {cov.spec.get('version', 'Bot API')}...")
    print(f"Total Official Methods: {len(spec_methods)}")
    print(f"Total Official Types:   {len(spec_types)}\n")

    method_issues = []
    for m in sorted(spec_methods):
        b_gaps = cov.method_botapi_gaps(m)
        m_gaps = cov.method_mtproto_gaps(m)
        if b_gaps or m_gaps:
            method_issues.append((m, b_gaps, m_gaps))

    type_issues = []
    for t in sorted(spec_types):
        gaps = cov.type_gaps(t)
        if gaps:
            type_issues.append((t, gaps))

    print("-------------------------------------------------------")
    print(f"METHODS AUDIT SUMMARY: {len(spec_methods) - len(method_issues)}/{len(spec_methods)} fully aligned")
    print("-------------------------------------------------------")
    if method_issues:
        print(f"Found {len(method_issues)} methods with unmapped/missing parameters:")
        for m, b_gaps, m_gaps in method_issues:
            details = []
            if b_gaps:
                details.append(f"Bot API missing: {b_gaps}")
            if m_gaps:
                details.append(f"MTProto missing: {m_gaps}")
            print(f"  * {m}: {'; '.join(details)}")
    else:
        print("  All methods are 100% aligned!")

    print("\n-------------------------------------------------------")
    print(f"TYPES AUDIT SUMMARY: {len(spec_types) - len(type_issues)}/{len(spec_types)} fully aligned")
    print("-------------------------------------------------------")
    if type_issues:
        print(f"Found {len(type_issues)} types with missing fields:")
        for t, gaps in type_issues[:15]:
            print(f"  * {t}: missing {gaps}")
        if len(type_issues) > 15:
            print(f"  ... and {len(type_issues) - 15} more types.")
    else:
        print("  All types are 100% aligned!")


def main():
    parser = argparse.ArgumentParser(description="Audit Tobigram API parameters against official specs.")
    parser.add_argument("--method", "-m", help="Method name to audit (e.g., ban_chat_member, send_photo)")
    parser.add_argument("--type", "-t", help="Type name to audit (e.g., Message, Chat)")
    parser.add_argument("--all", "-a", action="store_true", help="Audit all official methods and types")
    parser.add_argument("--diff", "-d", action="store_true", help="Show only methods and types with gaps")

    args = parser.parse_args()
    cov = Coverage()

    if args.method:
        audit_method(cov, args.method)
    elif args.type:
        audit_type(cov, args.type)
    elif args.all or args.diff:
        audit_all(cov, diff_only=args.diff)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
