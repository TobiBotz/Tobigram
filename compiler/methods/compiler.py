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

import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from jinja2 import Environment, FileSystemLoader

HOME = Path("compiler/methods")
TL_SOURCE = Path("compiler/api/source/main_api.tl")
OVERRIDES = HOME / "overrides.yaml"
TEMPLATES = HOME / "templates"
METHODS_DIR = Path("pyrogram/methods")

COMBINATOR_RE = re.compile(r"^([\w.]+)#([0-9a-f]+)\s(.*?)=\s([\w<>.]+);$", re.MULTILINE)
FLAGS_RE = re.compile(r"flags(\d?)\.(\d+)\?")
PARAM_RE = re.compile(r"([a-z_]+):([\w<>.]+)")


def parse_tl_functions(tl_path: Path) -> Dict[str, Dict]:
    text = tl_path.read_text(encoding="utf-8")
    functions = {}
    for match in COMBINATOR_RE.finditer(text):
        qualname, tl_id, args_str, return_type = match.groups()
        if not return_type or return_type == qualname:
            continue

        params = []
        args_str = args_str.strip()

        for p_match in PARAM_RE.finditer(args_str):
            name, ptype = p_match.groups()
            flag_match = FLAGS_RE.match(ptype)
            if flag_match:
                actual_type = ptype.split("?", 1)[1]
            else:
                actual_type = ptype
            params.append(
                {
                    "name": name,
                    "type": actual_type,
                    "tl_type": ptype,
                }
            )

        parts = qualname.split(".")
        namespace = parts[0] if len(parts) > 1 else ""
        short_name = parts[-1] if len(parts) > 1 else qualname

        functions[qualname] = {
            "qualname": qualname,
            "namespace": namespace,
            "short_name": short_name,
            "id": tl_id,
            "params": params,
            "return_type": return_type,
        }

        full_key = f"{namespace}.{short_name}" if namespace else short_name
        functions[full_key] = functions[qualname]

    return functions


def to_snake_case(name: str) -> str:
    name = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name)
    name = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", name)
    return name.lower()


def to_pascal_case(name: str) -> str:
    return "".join(word.capitalize() for word in name.split("_"))


def find_method_name(raw_name: str) -> str:
    return to_snake_case(raw_name)


DEFAULT_CATEGORY = {
    "messages": "messages",
    "bots": "bots",
    "channels": "chats",
    "users": "users",
    "account": "account",
    "contacts": "contacts",
    "stories": "stories",
    "payments": "payments",
    "phone": "phone",
    "folders": "folders",
    "auth": "auth",
    "help": "utilities",
    "langpack": "utilities",
    "upload": "advanced",
    "updates": "utilities",
}


def guess_category(raw_name: str, tl_info: Optional[Dict] = None) -> str:
    if tl_info and tl_info.get("namespace"):
        return DEFAULT_CATEGORY.get(tl_info["namespace"], "messages")
    return "messages"


INDENT = "                "


def map_raw_params(method_name: str, tl_params: List[Dict], override: Dict) -> str:
    lines = []
    extra_names = {p["name"] for p in override.get("extra_params", [])}
    param_mapping = override.get("param_mapping", {})

    for p in tl_params:
        name = p["name"]
        tl_type = p["type"]

        if name == "flags":
            continue

        mapped_name = param_mapping.get(name, name)

        if name in ("peer", "channel", "broadcast"):
            lines.append(f"{name}=await self.resolve_peer({mapped_name}),")
        elif name in ("bot", "user_id", "participant", "admin_id"):
            lines.append(f"{name}=await self.resolve_peer({mapped_name}),")
        elif name == "random_id":
            lines.append("random_id=self.rnd_id(),")
        elif name in (
            "noforwards",
            "no_webpage",
            "silent",
            "background",
            "clear_draft",
            "update_stickersets_order",
            "invert_media",
            "allow_paid_floodskip",
            "hide_via",
            "with_my_score",
            "drop_author",
            "drop_media_captions",
            "big",
            "add_to_recent",
        ):
            if tl_type == "true":
                val = "disable_notification or None"
                if name == "noforwards":
                    val = "protect_content or None"
                elif name == "no_webpage":
                    val = "disable_web_page_preview or None"
                lines.append(f"{name}={val},")
            else:
                lines.append(f"{name}={mapped_name},")
        elif name == "reply_to":
            lines.append("""reply_to=raw.types.InputReplyToMessage(
                    reply_to_msg_id=reply_to_message_id
                ) if reply_to_message_id else None,""")
        elif name == "message" and tl_type == "string":
            lines.append(f"message={mapped_name},")
        elif name == "schedule_date":
            lines.append(f"schedule_date=utils.datetime_to_timestamp({mapped_name}),")
        elif name == "reply_markup":
            lines.append(
                f"reply_markup=await {mapped_name}.write(self) if {mapped_name} else None,"
            )
        elif name == "send_as":
            lines.append(
                f"send_as=await self.resolve_peer({mapped_name}) if {mapped_name} else None,"
            )
        elif name in ("entities",):
            lines.append(f"entities={mapped_name},")
        elif name == "media":
            media_type = override.get("raw_media_type")
            media_mapping = override.get("media_mapping", {})
            if media_type and media_mapping:
                media_args = ", ".join(f"{k}={v}" for k, v in media_mapping.items())
                lines.append(f"""media=raw.types.{media_type}(
                    {media_args}
                ),""")
            else:
                custom_media = override.get("media_param")
                if custom_media:
                    lines.append(f"media={custom_media},")
                else:
                    lines.append("# TODO: [MANUAL] construct media")
                    lines.append("media=...,")
        elif name == "multi_media":
            lines.append(f"multi_media={mapped_name},")
        else:
            if mapped_name in extra_names:
                lines.append(f"{name}={mapped_name},")

    if override.get("supports_caption"):
        text_params_comment = (
            "# TODO: [MANUAL] replace with rich_text conditional: "
            "see send_message.py for pattern"
        )
        lines.append(text_params_comment)
        lines.append(
            "**await utils.parse_text_entities(self, caption, parse_mode, caption_entities)"
        )

    return "\n".join(lines)


def build_signature_params(override: Dict) -> str:
    extra = override.get("extra_params", [])
    if not extra:
        return ""

    lines = []
    for p in extra:
        name = p["name"]
        ptype = p.get("type", "Any")
        default = p.get("default", "None")
        if isinstance(default, str) and default not in ("None",):
            default = f'"{default}"'
        lines.append(f"        {name}: {ptype} = {default},")
    return "\n" + "\n".join(lines)


def build_doc_params(override: Dict) -> List[Dict]:
    extra = override.get("extra_params", [])
    return [
        {"name": p["name"], "type": p.get("type", "str"), "doc": p.get("doc", "N/A")}
        for p in extra
    ]


def compute_import_flags(override: Dict) -> Dict[str, bool]:
    extra = override.get("extra_params", [])
    types_str = " ".join(p.get("type", "") for p in extra)
    return {
        "needs_list": "List[" in types_str,
        "needs_optional": any(p.get("default") is not None for p in extra)
        or override.get("response_pattern") != "none",
        "needs_datetime": "datetime" in types_str,
        "needs_enums": "enums." in types_str,
        "needs_utils": bool(override.get("supports_caption"))
        or "schedule_date" in types_str,
    }


class MethodGenerator:
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATES)),
            lstrip_blocks=True,
        )
        self.tl_functions: Dict[str, Dict] = {}
        self.overrides: Dict[str, Dict] = {}

    def load(self):
        tl_path = Path(str(TL_SOURCE))
        if tl_path.exists():
            self.tl_functions = parse_tl_functions(tl_path)
            print(f"Loaded {len(self.tl_functions)} TL function definitions")

        if OVERRIDES.exists():
            with open(OVERRIDES, encoding="utf-8") as f:
                self.overrides = yaml.safe_load(f) or {}
            print(f"Loaded {len(self.overrides)} method overrides")
        else:
            print(f"Warning: {OVERRIDES} not found")

    def generate(self):
        template = self.jinja_env.get_template("simple.py.j2")
        generated = []

        for raw_name, override in self.overrides.items():
            method_name = find_method_name(raw_name)
            class_name = to_pascal_case(method_name)
            category = override.get("category") or guess_category(raw_name)
            raw_func = override.get("raw_function", f"messages.{raw_name}")
            tl_info = self.tl_functions.get(raw_func)

            out_path = METHODS_DIR / category / f"{method_name}.py"
            if out_path.exists() and override.get("skip_if_exists", True):
                print(f"  SKIP {out_path}")
                continue

            if tl_info:
                raw_params_str = map_raw_params(
                    method_name, tl_info.get("params", []), override
                )
            else:
                raw_params_str = override.get("raw_params", "")
                if not raw_params_str:
                    print(f"  WARNING: no TL info for {raw_func}, skipping {raw_name}")
                    continue

            ctx = {
                "source": f"tl:{raw_func}",
                "class_name": class_name,
                "method_name": method_name,
                "return_type": override.get("return_type", "types.Message"),
                "usable_by": override.get("usable_by", "users-bots"),
                "doc_summary": override.get("doc_summary", f"{class_name}."),
                "response_pattern": override.get("response_pattern", "updates"),
                "has_text_parsing": override.get("has_text_parsing", False),
                "raw_function": raw_func,
                "additional_params": build_signature_params(override),
                "raw_params": INDENT + ("\n" + INDENT).join(raw_params_str.split("\n"))
                if raw_params_str
                else "",
                "doc_params": build_doc_params(override),
                "has_media_type": bool(override.get("raw_media_type")),
                "list_type": override.get("list_type", ""),
                **compute_import_flags(override),
            }

            try:
                rendered = template.render(**ctx)
            except Exception as e:
                print(f"  ERROR rendering {raw_name}: {e}")
                continue

            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(rendered, encoding="utf-8")
            print(f"  WRITE {out_path}")
            generated.append((category, class_name, method_name))

        self._update_init_files(generated)
        print(f"\nGenerated {len(generated)} method files")

    def _update_init_files(self, generated: list):
        grouped = {}
        for category, class_name, method_name in generated:
            grouped.setdefault(category, []).append((class_name, method_name))

        for category, items in grouped.items():
            init_path = METHODS_DIR / category / "__init__.py"
            if not init_path.exists():
                print(f"  WARNING: {init_path} not found")
                continue

            text = init_path.read_text(encoding="utf-8")
            new_imports = []
            for class_name, method_name in items:
                imp = f"from .{method_name} import {class_name}"
                if imp not in text:
                    new_imports.append(imp)

            if not new_imports:
                continue

            lines = text.splitlines(keepends=True)
            insert_at = 0
            for i, line in enumerate(lines):
                if line.startswith("from ."):
                    insert_at = i + 1

            insert_lines = [f"{imp}\n" for imp in new_imports]
            lines[insert_at:insert_at] = insert_lines
            init_path.write_text("".join(lines), encoding="utf-8")
            print(f"  UPDATE {init_path} ({len(new_imports)} import(s))")


if __name__ == "__main__":
    generator = MethodGenerator()
    generator.load()
    generator.generate()
