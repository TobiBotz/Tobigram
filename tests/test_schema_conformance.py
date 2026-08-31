"""Every generated class must put on the wire exactly what the TL schema says.

A round-trip test only proves a class agrees with itself: a field written in the
wrong order, at the wrong width, or under the wrong flag bit still reads back
cleanly when read() repeats write()'s mistake. So these tests decode what each
class emits using nothing but the .tl definition, and the schema is the judge.
"""

import inspect
import re
import struct
import typing
from io import BytesIO
from pathlib import Path

import pytest

from pyrogram import raw
from pyrogram.raw.core import TLObject

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "compiler" / "api" / "source"

TL_SOURCES = [SOURCE / "auth_key.tl", SOURCE / "sys_msgs.tl", SOURCE / "main_api.tl"]

COMBINATOR_RE = re.compile(r"^([\w.]+)#([0-9a-f]+)\s(?:.*)=\s([\w<>.]+);$")
ARGS_RE = re.compile(r"[^{](\w+):([\w?!.<>#]+)")
FLAG_RE = re.compile(r"^flags(\d?)\.(\d+)\?(.+)$")

RENAME = {"self": "is_self", "from": "from_peer"}


def camel(name):
    """The generator's own name rule: p_q_inner_data -> PQInnerData."""
    return "".join(part[:1].upper() + part[1:] for part in name.split("_"))


def parse_schema():
    out = []

    for source in TL_SOURCES:
        section = "types"

        for line in source.read_text(encoding="utf-8").splitlines():
            line = line.strip()

            if line in ("---functions---", "---types---"):
                section = line.strip("-")
                continue

            if not line or line.startswith("//"):
                continue

            match = COMBINATOR_RE.match(line)

            if not match:
                continue

            qualname, constructor_id, _ = match.groups()
            args = [(RENAME.get(name, name), kind)
                    for name, kind in ARGS_RE.findall(line)]

            out.append((section, qualname, int(constructor_id, 16), args))

    return out


SCHEMA = parse_schema()


def python_qualname(section, qualname):
    if "." in qualname:
        namespace, name = qualname.rsplit(".", 1)
        return "{}.{}.{}".format(section, namespace, camel(name))

    return "{}.{}".format(section, camel(qualname))


def lookup(section, qualname):
    module = raw.functions if section == "functions" else raw.types
    parts = qualname.split(".")

    for part in parts[:-1]:
        module = getattr(module, part, None)

        if module is None:
            return None

    return getattr(module, camel(parts[-1]), None)


class Desync(Exception):
    """The bytes stopped lining up with the definition."""


def r_int(b):
    data = b.read(4)

    if len(data) != 4:
        raise Desync("ran out reading int")

    return struct.unpack("<i", data)[0]


def r_long(b):
    data = b.read(8)

    if len(data) != 8:
        raise Desync("ran out reading long")

    return struct.unpack("<q", data)[0]


def r_double(b):
    data = b.read(8)

    if len(data) != 8:
        raise Desync("ran out reading double")

    return struct.unpack("<d", data)[0]


def r_big(b, size):
    data = b.read(size)

    if len(data) != size:
        raise Desync("ran out reading int{}".format(size * 8))

    return int.from_bytes(data, "little")


def r_bytes(b):
    head = b.read(1)

    if not head:
        raise Desync("ran out reading string length")

    length = head[0]
    total = length + 1

    if length > 253:
        length = int.from_bytes(b.read(3), "little")
        total = length + 4

    body = b.read(length)

    if len(body) != length:
        raise Desync("ran out reading string body")

    b.read(-total % 4)

    return body


def r_bool(b):
    value = r_int(b) & 0xFFFFFFFF

    if value == 0x997275B5:
        return True

    if value == 0xBC799737:
        return False

    raise Desync("expected Bool, got {:08x}".format(value))


PRIMITIVES = {
    "int": r_int,
    "long": r_long,
    "double": r_double,
    "int128": lambda b: r_big(b, 16),
    "int256": lambda b: r_big(b, 32),
    "string": lambda b: r_bytes(b).decode("utf-8", "replace"),
    "bytes": r_bytes,
    "Bool": r_bool,
}


def read_typed(b, kind):
    if kind in PRIMITIVES:
        return PRIMITIVES[kind](b)

    if kind == "Object":
        return TLObject.read(b)

    if kind.lower().startswith("vector<"):
        inner = kind[kind.index("<") + 1:-1]
        constructor_id = r_int(b) & 0xFFFFFFFF

        if constructor_id != 0x1CB5C415:
            raise Desync("expected a vector, got {:08x}".format(constructor_id))

        count = r_int(b)

        if not 0 <= count <= 10000:
            raise Desync("implausible vector count {}".format(count))

        return [read_typed(b, inner) for _ in range(count)]

    return TLObject.read(b)


def decode(b, args, constructor_id):
    got = r_int(b) & 0xFFFFFFFF

    if got != constructor_id:
        raise Desync("constructor id {:08x}, schema says {:08x}".format(
            got, constructor_id))

    flags = {}
    values = {}

    for name, kind in args:
        if kind == "#" and name.startswith("flags"):
            flags[name[len("flags"):]] = r_int(b)
            continue

        match = FLAG_RE.match(kind)

        if match:
            group, bit, inner = match.group(1), int(match.group(2)), match.group(3)

            if group not in flags:
                raise Desync("{} reads flags{} before it was declared".format(
                    name, group))

            present = bool(flags[group] & (1 << bit))
            values[name] = present if inner == "true" else (
                read_typed(b, inner) if present else None)
            continue

        if kind.startswith("!"):
            values[name] = TLObject.read(b)
            continue

        values[name] = read_typed(b, kind)

    return values


class Unbuildable(Exception):
    pass


counter = [0]


def fresh():
    counter[0] += 1

    return counter[0] % 1000000 + 7


BUILTINS = {"bytes": bytes, "int": int, "str": str, "bool": bool, "float": float}

VALUES = {
    int: fresh,
    str: lambda: "s{}".format(fresh()),
    bytes: lambda: "b{}".format(fresh()).encode(),
    bool: lambda: True,
    float: lambda: 1.5,
}


def unwrap(annotation):
    if inspect.ismemberdescriptor(annotation) and annotation.__name__ in BUILTINS:
        return "prim", BUILTINS[annotation.__name__]

    if isinstance(annotation, str):
        return "base", annotation

    if isinstance(annotation, typing.ForwardRef):
        return "base", annotation.__forward_arg__

    origin = typing.get_origin(annotation)

    if origin is typing.Union:
        args = [a for a in typing.get_args(annotation) if a is not type(None)]

        if len(args) == 1:
            return unwrap(args[0])

    if origin is list:
        return "list", typing.get_args(annotation)[0]

    if annotation in VALUES:
        return "prim", annotation

    if annotation is typing.Any or annotation is TLObject:
        return "any", None

    raise Unbuildable("annotation {!r}".format(annotation))


def params_of(cls):
    return [p for name, p in inspect.signature(cls.__init__).parameters.items()
            if name != "self"]


def base_key(name):
    return name[len("raw.base."):] if name.startswith("raw.base.") else name


def concretes_by_base():
    """base name -> its constructors, read off the generated Union lines."""
    union_re = re.compile(r"^(\w+) = Union\[(.+)\]$", re.M)
    alias_re = re.compile(r"^(\w+) = raw\.types\.([\w.]+)$", re.M)
    out = {}

    import pkgutil

    for module in pkgutil.walk_packages(raw.base.__path__, raw.base.__name__ + "."):
        __import__(module.name)
        source = inspect.getsource(__import__("sys").modules[module.name])
        short = module.name[len("pyrogram.raw.base."):]
        namespace = short.rsplit(".", 1)[0] + "." if "." in short else ""

        for name, body in union_re.findall(source):
            out[namespace + name] = [
                part.strip()[len("raw.types."):] for part in body.split(",")]

        for name, target in alias_re.findall(source):
            out.setdefault(namespace + name, [target])

    return out


def resolve(name):
    module = raw.types
    parts = name.split(".")

    for part in parts[:-1]:
        module = getattr(module, part, None)

        if module is None:
            return None

    return getattr(module, parts[-1], None)


BASES = concretes_by_base()

SIMPLEST = {}
_pending = dict(BASES)

for _ in range(60):
    _progress = False

    for _base in list(_pending):
        _best = None

        for _name in _pending[_base]:
            _cls = resolve(_name)

            if _cls is None:
                continue

            _needs = set()

            for _param in params_of(_cls):
                if _param.default is not inspect.Parameter.empty:
                    continue

                try:
                    _kind, _payload = unwrap(_param.annotation)
                except Unbuildable:
                    _needs.add("?")
                    continue

                if _kind == "base":
                    _needs.add(base_key(_payload))
                elif _kind == "list":
                    try:
                        _k2, _p2 = unwrap(_payload)
                    except Unbuildable:
                        _needs.add("?")
                        continue

                    if _k2 == "base":
                        _needs.add(base_key(_p2))

            if not all(n in SIMPLEST for n in _needs):
                continue

            _score = (len(_needs), len(params_of(_cls)))

            if _best is None or _score < _best[0]:
                _best = (_score, _cls)

        if _best is not None:
            SIMPLEST[_base] = _best[1]
            del _pending[_base]
            _progress = True

    if not _progress:
        break

for _base, _names in _pending.items():
    _found = [resolve(n) for n in _names]
    _found = [c for c in _found if c is not None]

    if _found:
        SIMPLEST[_base] = min(_found, key=lambda c: len(params_of(c)))


def synth(annotation, depth):
    if depth > 12:
        raise Unbuildable("nested too deep")

    kind, payload = unwrap(annotation)

    if kind == "prim":
        return VALUES[payload]()

    if kind == "any":
        return raw.functions.help.GetConfig()

    if kind == "base":
        cls = SIMPLEST.get(base_key(payload))

        if cls is None:
            raise Unbuildable("no constructor for {}".format(payload))

        return build(cls, full=False, depth=depth + 1)

    inner_kind, inner = unwrap(payload)

    if inner_kind == "prim":
        return [VALUES[inner]() for _ in range(2)]

    if inner_kind == "any":
        return [raw.functions.help.GetConfig()]

    cls = SIMPLEST.get(base_key(inner))

    if cls is None:
        raise Unbuildable("no constructor for {}".format(inner))

    return [build(cls, full=False, depth=depth + 1)]


def build(cls, full, depth=0):
    kwargs = {}

    for param in params_of(cls):
        if param.default is not inspect.Parameter.empty and not full:
            continue

        kwargs[param.name] = synth(param.annotation, depth)

    return cls(**kwargs)


def matches(sent, got):
    if isinstance(sent, list):
        return (isinstance(got, list) and len(sent) == len(got)
                and all(matches(a, b) for a, b in zip(sent, got)))

    if isinstance(sent, TLObject):
        return isinstance(got, TLObject) and type(sent) is type(got)

    if isinstance(sent, float):
        return abs(sent - got) < 1e-9

    return sent == got


def test_the_schema_was_read():
    assert len(SCHEMA) > 2000, "main_api.tl should hold thousands of combinators"


@pytest.mark.parametrize("full", [False, True], ids=["required", "every-field"])
@pytest.mark.parametrize(
    "section,qualname,constructor_id,args",
    SCHEMA,
    ids=[python_qualname(s, q) for s, q, _, _ in SCHEMA],
)
def test_a_class_writes_what_the_schema_declares(
        section, qualname, constructor_id, args, full):
    cls = lookup(section, qualname)

    assert cls is not None, "{} has no generated class".format(qualname)
    assert cls.ID & 0xFFFFFFFF == constructor_id, (
        "{} carries id {:08x}, the schema says {:08x}".format(
            qualname, cls.ID & 0xFFFFFFFF, constructor_id))

    try:
        specimen = build(cls, full=full)
    except Unbuildable as reason:
        pytest.fail("could not build a {}: {}".format(qualname, reason))

    payload = specimen.write()
    stream = BytesIO(payload)
    values = decode(stream, args, constructor_id)

    assert stream.tell() == len(payload), (
        "{} wrote {} bytes the schema does not account for".format(
            qualname, len(payload) - stream.tell()))

    for name, _ in args:
        if name not in values:
            continue

        sent = getattr(specimen, name)
        got = values[name]

        if sent is None and got in (False, None, []):
            continue

        assert matches(sent, got), (
            "{}.{} was set to {!r} but the wire holds {!r}".format(
                qualname, name, sent, got))


BY_NAME = {q: (c, a) for _, q, c, a in SCHEMA}


def test_the_decoder_notices_a_wrong_constructor_id():
    constructor_id, args = BY_NAME["updateDeleteMessages"]
    honest = build(lookup("types", "updateDeleteMessages"), full=False).write()

    with pytest.raises(Desync, match="constructor id"):
        decode(BytesIO(b"\xef\xbe\xad\xde" + honest[4:]), args, constructor_id)


def test_the_decoder_notices_a_field_of_the_wrong_width():
    from pyrogram.raw.core.primitives import Int, Long

    constructor_id, args = BY_NAME["updateDeleteMessages"]
    payload = (Int(constructor_id, False) + b"\x15\xc4\xb5\x1c" + Int(1) + Int(9)
               + Long(77) + Int(88))
    stream = BytesIO(payload)
    decode(stream, args, constructor_id)

    assert stream.tell() != len(payload), "the extra four bytes should be left over"


def test_the_decoder_notices_a_missing_field():
    from pyrogram.raw.core.primitives import Int

    constructor_id, args = BY_NAME["updateDeleteMessages"]
    payload = Int(constructor_id, False) + b"\x15\xc4\xb5\x1c" + Int(1) + Int(9) + Int(77)

    with pytest.raises(Desync, match="ran out"):
        decode(BytesIO(payload), args, constructor_id)


def test_the_decoder_notices_a_value_hung_on_the_wrong_flag_bit():
    from pyrogram.raw.core.primitives import Int, String

    constructor_id, args = BY_NAME["inputMediaPhotoExternal"]

    honest = Int(constructor_id, False) + Int(1 << 0) + String("u") + Int(30)
    stream = BytesIO(honest)
    values = decode(stream, args, constructor_id)

    assert values["ttl_seconds"] == 30
    assert stream.tell() == len(honest)

    moved = Int(constructor_id, False) + Int(1 << 1) + String("u") + Int(30)
    stream = BytesIO(moved)
    decode(stream, args, constructor_id)

    assert stream.tell() != len(moved), "the orphaned value should be left over"


def test_every_generated_class_has_a_schema_entry_and_the_reverse():
    """A class with no definition behind it is a leftover from an older layer."""
    import pkgutil
    import sys as _sys

    generated = set()

    for package, section in ((raw.types, "types"), (raw.functions, "functions")):
        for module in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            __import__(module.name)

            for value in vars(_sys.modules[module.name]).values():
                if (inspect.isclass(value) and issubclass(value, TLObject)
                        and value is not TLObject and hasattr(value, "ID")
                        and value.__module__ == module.name):
                    generated.add(value.QUALNAME)

    declared = {python_qualname(section, qualname)
                for section, qualname, _, _ in SCHEMA}

    assert not generated - declared, (
        "generated classes with no schema line: {}".format(
            sorted(generated - declared)[:10]))
    assert not declared - generated, (
        "schema lines with no generated class: {}".format(
            sorted(declared - generated)[:10]))


def test_a_vector_of_primitives_always_carries_its_element_type():
    """The invariant `Vector.read` leans on when no element type is given.

    Told nothing about its elements, `Vector.read` treats them as objects,
    which is only right because the generator names the type for every vector
    of numbers or strings. A layer that broke that would decode silently wrong,
    so check it rather than trust it.
    """
    primitives = {"int", "long", "double", "int128", "int256",
                  "string", "bytes", "Bool"}
    untyped = []

    for section, qualname, _, args in SCHEMA:
        cls = lookup(section, qualname)

        if cls is None:
            continue

        for name, kind in args:
            match = FLAG_RE.match(kind)
            inner_of = match.group(3) if match else kind

            if not inner_of.lower().startswith("vector<"):
                continue

            if inner_of[inner_of.index("<") + 1:-1] not in primitives:
                continue

            body = inspect.getsource(cls).split("def read(", 1)[1].split("def write(", 1)[0]
            line = re.search(r"^\s*{} = (.+?)$".format(re.escape(name)), body, re.M)

            if line and not re.search(r"TLObject\.read\(b,\s*\w+\)", line.group(1)):
                untyped.append("{}.{} reads {}".format(qualname, name, line.group(1)))

    assert not untyped, (
        "these vectors of primitives are read with no element type, so "
        "Vector.read would take them for objects: {}".format(untyped[:10]))
