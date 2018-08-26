#!/usr/bin/env python3
import argparse, sys
from pyralala import SongReader
from pyralala.export import Compiler, MarkdownCompiler

parser = argparse.ArgumentParser(description='Convert LaTeX songs files.')
parser.add_argument("file", help="The LaTeX song file to be converted.")
parser.add_argument("-o", "--out", help="Output file path.")
args = parser.parse_args()

try:
    reader = SongReader(args.file)
    reader.read()
except (TypeError, EOFError) as e:
    print(e)
    sys.exit(0)

try:
    out = open(args.out, "w")
except TypeError as e:
    out = sys.stdout
except (FileNotFoundError, PermissionError) as e:
    print(e)
    sys.exit(1)

compiler = MarkdownCompiler()
compiler.compile(reader.song)
compiler.write(out)