#!/usr/bin/env python3

# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import sys


def main(frag: str, file: str):
    with open(frag) as fp:
        frag_lines = tuple(fp)
    lines: list[str] = []
    with open(file, "r+") as fp:
        needs_append = True
        for line in fp:
            if needs_append and line.startswith("##"):
                if frag_lines[0] != line:
                    lines.extend((*frag_lines, "\n"))
                needs_append = False
            lines.append(line)
        fp.seek(0)
        fp.writelines(lines)
        fp.truncate()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
