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
from pathlib import Path

HOME = Path(__file__).parent
SOURCE = HOME / "source"

for p in sorted(SOURCE.glob("*.tsv")):
    with open(p, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        dct = {row[0]: row[1] for row in reader if row and row[0] != "id"}
        keys = sorted(dct)

    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write("id\tmessage\n")

        for i, item in enumerate(keys, start=1):
            f.write(f"{item}\t{dct[item]}\n")
