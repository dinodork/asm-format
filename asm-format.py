#!/usr/bin/python3

import argparse
import sys
import re
import os


class Formatter:

    def __init__(self, config, mnemonics):
        self.config = config
        self.mnemonics = mnemonics

    def format_file(self, infile):
        content = self.read_file(infile)
        self.write_formatted(content, sys.stdout)

    def format_file_inplace(self, infile):
        content = self.read_file(infile)
        with open(infile.name, "w") as outfile:
            self.write_formatted(content, outfile)

    def read_file(self, infile):
        content = infile.read()
        lines = content.split("\n")
        return [line.rstrip() for line in lines]

    def write_line_formatted(self, line, outfile):
        tokens = line.split()
        in_macro = False

        if len(tokens) == 0:
            print(file=outfile)
        else:
            if tokens[0] == "MACRO":
                in_macro = True
                print(line, file=outfile)
            elif tokens[0] == "ENDMACRO":
                in_macro = False
                print(line, file=outfile)
            elif not in_macro:
                if tokens[0].upper() in self.mnemonics:
                    mnemonic = (
                        tokens[0].upper()
                        if self.config["upperCaseMnemonics"]
                        else tokens[0].lower()
                    )
                    print(
                        " " * self.config["indent"]
                        + mnemonic
                        + line.strip()[len(mnemonic) :],
                        file=outfile,
                    )
                elif tokens[0][-1] == ":" and self.config["newlineAfterLabel"]:
                    print(tokens[0], file=outfile)
                    self.write_line_formatted(line[line.find(":")+1 :], outfile)
                else:
                    print(line, file=outfile)

    def write_formatted(self, lines, outfile):
        while len(lines) > 0 and lines[-1].strip() == "":
            lines.pop()

        for line in lines:
            self.write_line_formatted(line, outfile)


def main():

    parser = argparse.ArgumentParser(description="Formats assembler files.")
    parser.add_argument(
        "infiles", type=argparse.FileType("r"), default=sys.stdin, nargs="*"
    )

    parser.add_argument(
        "-i", "--in-place", help="Edit file in-place.", action="store_true"
    )

    args = parser.parse_args()
    with open(
        f"{os.path.dirname(os.path.realpath(__file__))}/architectures/z80/mnemonics.txt",
        "r",
    ) as z80_mnemonics_file:
        z80_mnemonics = z80_mnemonics_file.read().splitlines()
    config = {"indent": 2, "upperCaseMnemonics": True, "newlineAfterLabel": True}
    formatter = Formatter(config, z80_mnemonics)

    for infile in args.infiles:
        if args.in_place:
            formatter.format_file_inplace(infile)
        else:
            formatter.format_file(infile)


if __name__ == "__main__":
    main()
