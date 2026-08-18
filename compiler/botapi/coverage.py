#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import ast
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / "compiler" / "botapi"
SPEC_PATH = HOME / "source" / "botapi.json"
MANIFEST_PATH = HOME / "manifest.yaml"
ALIASES_PATH = HOME / "aliases.yaml"
TL_SOURCE = ROOT / "compiler" / "api" / "source" / "main_api.tl"
METHODS_DIR = ROOT / "pyrogram" / "methods"
CLIENT_PATH = ROOT / "pyrogram" / "client.py"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "compiler" / "methods"))

IGNORED_PARAMS = {"self", "client", "args", "kwargs"}

DOC_SECTION_RE = re.compile(r"^\s{4}(\w[\w ]*):\s*$")
DOC_PARAM_RE = re.compile(r"^\s{8}(\w+(?:\s*,\s*\w+)*)\s*\(")


def load_spec() -> dict:
    with open(SPEC_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def to_snake_case(name: str) -> str:
    name = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name)
    name = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", name)

    return name.lower()


TYPES_DIR = ROOT / "pyrogram" / "types"


class Symbol:
    """A class or method as it is written, read without importing anything."""

    __slots__ = ("name", "params", "bases", "properties", "doc", "path", "raw_calls")

    def __init__(self, name, params, bases, properties, doc, path, raw_calls=()):
        self.name = name
        self.params = params
        self.bases = bases
        self.properties = properties
        self.doc = doc
        self.path = path
        self.raw_calls = set(raw_calls)


def signature_params(node) -> Set[str]:
    args = node.args
    names = [a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)]

    return {name for name in names if name not in IGNORED_PARAMS}


def is_property(node) -> bool:
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "property":
            return True

        if isinstance(decorator, ast.Attribute) and decorator.attr == "property":
            return True

    return False


def base_names(node) -> List[str]:
    names = []

    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)

    return names


def raw_calls_in(node) -> Set[str]:
    calls = set()

    for call in ast.walk(node):
        if not isinstance(call, ast.Call):
            continue

        parts = dotted(call.func)

        if parts and parts[0] == "raw" and len(parts) >= 3 and parts[1] == "functions":
            qualname = ".".join(parts[2:])
            namespace, _, short = qualname.rpartition(".")
            short = short[:1].lower() + short[1:]
            calls.add(f"{namespace}.{short}" if namespace else short)

    return calls


def documented_params(doc: Optional[str]) -> Optional[Set[str]]:
    """The parameters the reST ``Parameters:`` block claims exist."""
    if not doc:
        return None

    found = set()
    inside = False

    for line in doc.splitlines():
        section = DOC_SECTION_RE.match(line)

        if section:
            inside = section.group(1) == "Parameters"
            continue

        if inside:
            param = DOC_PARAM_RE.match(line)

            if param:
                found.update(name.strip() for name in param.group(1).split(","))

    return found if inside or found else None


def type_names(entries) -> Set[str]:
    """Type names referenced by a spec ``types`` list, unwrapping arrays."""
    names = set()

    for entry in entries or []:
        while entry.startswith("Array of "):
            entry = entry[len("Array of "):]

        names.add(entry)

    return names


def dotted(node: ast.Attribute) -> Optional[List[str]]:
    parts = []

    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if not isinstance(node, ast.Name):
        return None

    parts.append(node.id)

    return list(reversed(parts))


def index_types() -> Dict[str, Symbol]:
    """Every class under pyrogram/types, keyed by name."""
    index: Dict[str, Symbol] = {}

    for path in sorted(TYPES_DIR.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef) or node.name in index:
                continue

            params: Set[str] = set()
            properties: Set[str] = set()

            for child in node.body:
                if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue

                if child.name == "__init__":
                    params = signature_params(child)
                elif is_property(child):
                    properties.add(child.name)

            index[node.name] = Symbol(
                node.name, params, base_names(node), properties,
                ast.get_docstring(node, clean=False), path
            )

    return index


def index_methods() -> Dict[str, Symbol]:
    """Every public high-level client method, keyed by name.

    A handful of them (``get_file``, ``save_file``) live on Client itself rather
    than in a category package.
    """
    index: Dict[str, Symbol] = {}

    for path in [*sorted(METHODS_DIR.rglob("*.py")), CLIENT_PATH]:
        tree = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            if node.name.startswith("_") or node.name in index:
                continue

            index[node.name] = Symbol(
                node.name, signature_params(node), [], set(),
                ast.get_docstring(node, clean=False), path, raw_calls_in(node)
            )

    return index


def tl_functions() -> Dict[str, dict]:
    from compiler import parse_tl_functions

    return parse_tl_functions(TL_SOURCE)


class Finding:
    __slots__ = ("kind", "entity", "detail")

    def __init__(self, kind: str, entity: str, detail: str):
        self.kind = kind
        self.entity = entity
        self.detail = detail

    def __str__(self) -> str:
        return f"[{self.kind}] {self.entity}: {self.detail}"


class Coverage:
    def __init__(self):
        self.spec = load_spec()
        self.manifest = load_yaml(MANIFEST_PATH)
        self.aliases = load_yaml(ALIASES_PATH)
        self._types = None
        self._methods = None
        self._tl = None

    # ------------------------------------------------------------------ data

    @property
    def types(self) -> Dict[str, Symbol]:
        if self._types is None:
            self._types = index_types()

        return self._types

    @property
    def methods(self) -> Dict[str, Symbol]:
        if self._methods is None:
            self._methods = index_methods()

        return self._methods

    @property
    def tl(self) -> Dict[str, dict]:
        if self._tl is None:
            self._tl = tl_functions()

        return self._tl

    def _alias(self, section: str, key: str, entity: str, field: str, scope=(), have=()) -> str:
        """What the field is called on the wzgram side.

        A name the target already carries verbatim wins over any alias: the
        global TL table renames `effect` to `effect_id` for send_message, but
        forward_messages exposes `effect` itself, and aliasing it there would
        report a parameter that is present as missing.
        """
        if field in have:
            return field

        table = (self.aliases.get(section) or {}).get(key) or {}

        for name in (entity, *scope, "*"):
            entry = table.get(name) or {}

            if field in entry:
                return entry[field]

        return field

    def _unsupported(self, section: str, key: str, entity: str, field: str, scope=()) -> bool:
        table = (self.aliases.get(section) or {}).get(key) or {}

        return any(field in (table.get(name) or {}) for name in (entity, *scope, "*"))

    # ----------------------------------------------------------- resolution

    def wzgram_type(self, name: str) -> Optional[Symbol]:
        botapi = self.aliases.get("botapi") or {}

        if name in (botapi.get("type_unsupported") or {}):
            return None

        renamed = (botapi.get("type_rename") or {}).get(name, name)

        return self.types.get(renamed)

    def wzgram_method(self, name: str) -> Optional[Symbol]:
        botapi = self.aliases.get("botapi") or {}

        if name in (botapi.get("method_unsupported") or {}):
            return None

        renamed = (botapi.get("method_rename") or {}).get(name)

        return self.methods.get(renamed or to_snake_case(name))

    def inherited_params(self, symbol: Symbol) -> Set[str]:
        seen, pending, params = set(), list(symbol.bases), set(symbol.params)

        while pending:
            name = pending.pop()

            if name in seen:
                continue

            seen.add(name)
            base = self.types.get(name)

            if base is not None:
                params |= base.params
                pending.extend(base.bases)

        return params

    def derives_from_object(self, symbol: Symbol) -> bool:
        seen, pending = set(), list(symbol.bases)

        while pending:
            name = pending.pop()

            if name in seen:
                continue

            seen.add(name)

            if name == "Object":
                return True

            base = self.types.get(name)

            if base is not None:
                pending.extend(base.bases)

        return False

    # ---------------------------------------------------------------- gaps

    def type_gaps(self, name: str) -> Optional[List[str]]:
        """Bot API fields the wzgram type does not expose. None if unresolvable."""
        spec_type = self.spec["types"].get(name)

        if spec_type is None:
            return None

        symbol = self.wzgram_type(name)

        if symbol is None:
            return None

        have = symbol.params
        gaps = []

        for field in spec_type.get("fields") or []:
            field_name = field["name"]

            if self._unsupported("botapi", "field_unsupported", name, field_name):
                continue

            if self._alias("botapi", "field_rename", name, field_name, have=have) not in have:
                gaps.append(field_name)

        return gaps

    def method_botapi_gaps(self, name: str) -> Optional[List[str]]:
        spec_method = self.spec["methods"].get(name)

        if spec_method is None:
            return None

        symbol = self.wzgram_method(name)

        if symbol is None:
            return None

        have = symbol.params
        gaps = []

        for field in spec_method.get("fields") or []:
            field_name = field["name"]

            if self._unsupported("botapi", "method_field_unsupported", name, field_name):
                continue

            if self._alias("botapi", "method_field_rename", name, field_name, have=have) not in have:
                gaps.append(field_name)

        return gaps

    def method_mtproto_gaps(self, name: str) -> Optional[List[str]]:
        """TL parameters the high-level method does not expose.

        Resolution goes through wzgram_method so both axes agree on what counts
        as implemented; looking the method up directly would still check one a
        method_unsupported entry has excluded.
        """
        symbol = self.wzgram_method(name)

        if symbol is None:
            return None

        method = symbol.name
        have = symbol.params
        mtproto = self.aliases.get("mtproto") or {}
        pinned = (mtproto.get("raw_function") or {}).get(method)

        if pinned:
            candidates = [pinned]
        else:
            calls = symbol.raw_calls

            if len(calls) != 1:
                return None

            candidates = list(calls)

        info = self.tl.get(candidates[0])

        if info is None:
            return None

        internal = set(mtproto.get("internal") or [])
        scope = (candidates[0],)
        gaps = []

        for param in info["params"]:
            field_name = param["name"]

            if field_name in internal:
                continue

            if self._unsupported("mtproto", "field_unsupported", method, field_name, scope):
                continue

            if self._alias("mtproto", "field_rename", method, field_name, scope, have) not in have:
                gaps.append(field_name)

        return gaps

    def type_field_stats(self, name: str) -> Optional[Tuple[int, List[str]]]:
        """(fields considered, fields missing) for a Bot API type."""
        gaps = self.type_gaps(name)

        if gaps is None:
            return None

        spec_type = self.spec["types"][name]
        considered = sum(
            0 if self._unsupported("botapi", "field_unsupported", name, f["name"]) else 1
            for f in spec_type.get("fields") or []
        )

        return considered, gaps

    def method_field_stats(self, name: str) -> Optional[Tuple[int, List[str]]]:
        gaps = self.method_botapi_gaps(name)

        if gaps is None:
            return None

        spec_method = self.spec["methods"][name]
        considered = sum(
            0 if self._unsupported("botapi", "method_field_unsupported", name, f["name"]) else 1
            for f in spec_method.get("fields") or []
        )

        return considered, gaps

    def implemented(self, kind: str) -> List[str]:
        entry = self.manifest.get(kind) or {}

        return sorted(set(entry.get("supported") or []) | set(entry.get("pending") or {}))

    def required_types(self) -> Set[str]:
        """Types reachable from the methods wzgram implements.

        A Bot API type only matters if an implemented method returns it or takes
        it, directly or through another required type. Judging coverage against
        the whole spec counts types nothing can ever reach.
        """
        pending = []

        for name in self.implemented("methods"):
            spec_method = self.spec["methods"].get(name) or {}
            pending.extend(type_names(spec_method.get("returns")))

            for field in spec_method.get("fields") or []:
                pending.extend(type_names(field["types"]))

        seen: Set[str] = set()

        while pending:
            name = pending.pop()

            if name in seen or name not in self.spec["types"]:
                continue

            seen.add(name)
            spec_type = self.spec["types"][name]
            pending.extend(spec_type.get("subtypes") or [])

            for field in spec_type.get("fields") or []:
                pending.extend(type_names(field["types"]))

        return seen

    def absorbed_by_union(self, name: str) -> bool:
        """Whether a Bot API union member is folded into a flat wzgram class.

        Bot API splits a union into one type per member and tells them apart with
        a type string; wzgram keeps a single class and an enum, so ChatMember
        covers all six ChatMember* members. Deciding this from the parent rather
        than a hand-written list keeps it right as Bot API adds members.
        """
        spec_type = self.spec["types"].get(name) or {}

        return any(
            self.wzgram_type(parent) is not None
            for parent in spec_type.get("subtype_of") or []
        )

    def report(self) -> dict:
        methods = self.implemented("methods")
        considered = missing = 0

        for name in methods:
            stats = self.method_field_stats(name)

            if stats:
                considered += stats[0]
                missing += len(stats[1])

        tl_considered = tl_missing = 0

        for name in methods:
            gaps = self.method_mtproto_gaps(name)

            if gaps is None:
                continue

            symbol = self.wzgram_method(name)
            tl_considered += len(symbol.params) + len(gaps)
            tl_missing += len(gaps)

        required = {
            name for name in self.required_types()
            if name not in ((self.aliases.get("botapi") or {}).get("type_unsupported") or {})
            and not self.absorbed_by_union(name)
        }
        implemented_types = set(self.implemented("types"))
        type_considered = type_missing = 0

        for name in sorted(required & implemented_types):
            stats = self.type_field_stats(name)

            if stats:
                type_considered += stats[0]
                type_missing += len(stats[1])

        return {
            "methods": {
                "implemented": len(methods),
                "total": len(self.spec["methods"]),
                "params": (considered - missing, considered),
                "tl_params": (tl_considered - tl_missing, tl_considered),
                "incomplete": sum(1 for n in methods if self.method_field_stats(n) and self.method_field_stats(n)[1]),
            },
            "types": {
                "required": len(required),
                "implemented": len(required & implemented_types),
                "absent": sorted(required - implemented_types),
                "params": (type_considered - type_missing, type_considered),
                "unreachable": len(set(self.spec["types"]) - required),
            },
        }

    # --------------------------------------------------------------- checks

    def check_docstrings(self) -> List[Finding]:
        findings = []

        for name in sorted(self.types):
            symbol = self.types[name]

            if not self.derives_from_object(symbol):
                continue

            have = symbol.params
            documented = documented_params(symbol.doc)

            if not have or documented is None:
                continue

            exposed = self.inherited_params(symbol) | symbol.properties

            undocumented = have - documented

            if undocumented:
                findings.append(Finding(
                    "docstring", name,
                    "in __init__ but missing from the Parameters: block: "
                    + ", ".join(sorted(undocumented))
                ))

            phantom = documented - exposed

            if phantom:
                findings.append(Finding(
                    "docstring", name,
                    "documented but not accepted by __init__: "
                    + ", ".join(sorted(phantom))
                ))

        return findings

    def check_manifest(self) -> List[Finding]:
        findings = []

        for kind in ("types", "methods"):
            entry = self.manifest.get(kind) or {}
            supported = entry.get("supported") or []
            pending = entry.get("pending") or {}

            both = set(supported) & set(pending)

            if both:
                findings.append(Finding(
                    "manifest", kind,
                    "listed as supported and pending at once: " + ", ".join(sorted(both))
                ))

            for name in supported:
                findings.extend(self._check_entity(kind, name, recorded=None))

            for name, recorded in pending.items():
                recorded = recorded or {}
                unknown = set(recorded) - {"botapi", "mtproto"}

                if kind == "types":
                    unknown |= set(recorded) & {"mtproto"}

                if unknown:
                    findings.append(Finding(
                        "manifest", f"{kind}/{name}",
                        "records gaps on an axis that is never checked: "
                        + ", ".join(sorted(unknown))
                    ))

                findings.extend(self._check_entity(kind, name, recorded=recorded))

        return findings

    def _gaps_for(self, kind: str, name: str) -> Tuple[Optional[List[str]], Optional[List[str]]]:
        if kind == "types":
            return self.type_gaps(name), None

        return self.method_botapi_gaps(name), self.method_mtproto_gaps(name)

    def _check_entity(self, kind: str, name: str, recorded: Optional[dict]) -> List[Finding]:
        botapi, mtproto = self._gaps_for(kind, name)

        if botapi is None and mtproto is None:
            return [Finding(
                "manifest", f"{kind}/{name}",
                "cannot be resolved; remove it from the manifest or add an alias"
            )]

        findings = []

        for axis, gaps in (("botapi", botapi), ("mtproto", mtproto)):
            if gaps is None:
                continue

            if recorded is None:
                if gaps:
                    findings.append(Finding(
                        axis, f"{kind}/{name}",
                        "supported but missing " + ", ".join(sorted(gaps))
                    ))

                continue

            known = set(recorded.get(axis) or [])
            new = set(gaps) - known

            if new:
                findings.append(Finding(
                    axis, f"{kind}/{name}",
                    "new gap since the manifest was recorded: " + ", ".join(sorted(new))
                ))

            stale = known - set(gaps)

            if stale:
                findings.append(Finding(
                    axis, f"{kind}/{name}",
                    "recorded gap no longer missing, update the manifest: "
                    + ", ".join(sorted(stale))
                ))

        if recorded is not None and not any(recorded.get(a) for a in ("botapi", "mtproto")):
            findings.append(Finding(
                "manifest", f"{kind}/{name}",
                "has no remaining gaps; promote it to supported"
            ))

        return findings

    def check(self) -> List[Finding]:
        return self.check_manifest() + self.check_docstrings()
