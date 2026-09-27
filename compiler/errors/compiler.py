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

import csv
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOME = os.path.join(ROOT, "compiler/errors")
DEST = os.path.join(ROOT, "pyrogram/errors/exceptions")
NOTICE_PATH = os.path.join(ROOT, "NOTICE")


def snek(s):
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def caml(s):
    s = snek(s).split("_")
    return "".join([str(i.title()) for i in s])


def class_name(error_id):
    s = caml(re.sub(r"_X", "_", error_id))
    s = re.sub(r"^2", "Two", s)
    return re.sub(r" ", "", s)


def start():
    shutil.rmtree(DEST, ignore_errors=True)
    os.makedirs(DEST)

    files = sorted(os.listdir(os.path.join(HOME, "source")))
    owners = {}

    for i in files:
        code, name = re.search(r"(\d+)_([A-Z_]+)", i).groups()

        with open(os.path.join(HOME, "source", i), encoding="utf-8") as f_csv:
            for row in list(csv.reader(f_csv, delimiter="\t"))[1:]:
                if row:
                    owners[class_name(row[0])] = f"{name.lower()}_{code}"

    with open(NOTICE_PATH, encoding="utf-8") as f:
        notice = []

        for line in f:
            notice.append(f"# {line}".strip())

        notice = "\n".join(notice)

    with open(os.path.join(DEST, "all.py"), "w", encoding="utf-8") as f_all:
        f_all.write(notice + "\n\n")
        f_all.write("count = {count}\n\n")
        f_all.write("exceptions = {\n")

        count = 0

        for i in files:
            code, name = re.search(r"(\d+)_([A-Z_]+)", i).groups()
            module = "{}_{}".format(name.lower(), code)

            f_all.write(f"    {code}: {{\n")

            init = os.path.join(DEST, "__init__.py")

            if not os.path.exists(init):
                with open(init, "w", encoding="utf-8") as f_init:
                    f_init.write(notice + "\n\n")

            with open(init, "a", encoding="utf-8") as f_init:
                f_init.write(f"from .{name.lower()}_{code} import *\n")

            with (
                open(os.path.join(HOME, "source", i), encoding="utf-8") as f_csv,
                open(
                    os.path.join(DEST, f"{name.lower()}_{code}.py"), "w", encoding="utf-8"
                ) as f_class,
            ):
                reader = csv.reader(f_csv, delimiter="\t")

                super_class = caml(name)
                name = " ".join(
                    [str(i.capitalize()) for i in re.sub(r"_", " ", name).lower().split(" ")]
                )

                sub_classes = []
                imports = []
                seen = set()

                f_all.write(f'        "_": "{super_class}",\n')

                for j, row in enumerate(reader):
                    if j == 0:
                        continue

                    count += 1

                    if not row:  # Row is empty (blank line)
                        continue

                    error_id, error_message = row

                    sub_class = class_name(error_id)
                    bases = super_class

                    if owners[sub_class] != module:
                        imports.append("from .{} import {}".format(owners[sub_class], sub_class))
                        bases = "{}, {}".format(super_class, sub_class)
                        sub_class += code
                    elif sub_class in seen:
                        bases = sub_class
                        sub_class += "X"
                    else:
                        seen.add(sub_class)

                    f_all.write(f'        "{error_id}": "{sub_class}",\n')

                    sub_classes.append((sub_class, error_id, error_message, bases))

                with open(
                    os.path.join(HOME, "template", "class.txt"), encoding="utf-8"
                ) as f_class_template:
                    class_template = f_class_template.read()

                    with open(
                        os.path.join(HOME, "template", "sub_class.txt"), encoding="utf-8"
                    ) as f_sub_class_template:
                        sub_class_template = f_sub_class_template.read()

                    class_template = class_template.format(
                        notice=notice,
                        super_class=super_class,
                        code=code,
                        imports="".join(["\n" + k for k in imports]),
                        docstring=f'"""{name}"""',
                        sub_classes="".join(
                            [
                                sub_class_template.format(
                                    sub_class=k[0],
                                    super_class=k[3],
                                    id=f'"{k[1]}"',
                                    docstring=f'"""{k[2]}"""',
                                )
                                for k in sub_classes
                            ]
                        ),
                    )

                f_class.write(class_template)

            f_all.write("    },\n")

        f_all.write("}\n")

    with open(os.path.join(DEST, "all.py"), encoding="utf-8") as f:
        content = f.read()

    with open(os.path.join(DEST, "all.py"), "w", encoding="utf-8") as f:
        f.write(re.sub("{count}", str(count), content))


if "__main__" == __name__:
    start()
