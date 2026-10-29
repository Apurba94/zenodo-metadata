"""Command-line interface for zenodo-metadata."""
import argparse
import json
import sys

from .core import UPLOAD_TYPES, build, validate


def _creator(s):
    parts = [p.strip() for p in s.split(";")]
    return {"name": parts[0], "orcid": parts[1] if len(parts) > 1 else "", "affiliation": parts[2] if len(parts) > 2 else ""}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="zenodo-metadata", description="Create or validate .zenodo.json files.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("title")
    n.add_argument("-c", "--creator", action="append", required=True, help="'Family, Given;ORCID;Affiliation'")
    n.add_argument("-d", "--description", required=True)
    n.add_argument("-t", "--type", choices=UPLOAD_TYPES, default="software")
    n.add_argument("--version")
    n.add_argument("--license", default="MIT")
    n.add_argument("-k", "--keyword", action="append", default=[])
    n.add_argument("--related", action="append", default=[], help="relation=identifier, e.g. isSupplementTo=10.1000/x")
    n.add_argument("--community", action="append", default=[])
    n.add_argument("-o", "--output", default=".zenodo.json")
    v = sub.add_parser("validate")
    v.add_argument("file", nargs="?", default=".zenodo.json")
    args = ap.parse_args(argv)
    if args.cmd == "new":
        related = [tuple(r.split("=", 1)) for r in args.related]
        md = build(args.title, [_creator(c) for c in args.creator], args.description, args.type, args.version,
                   args.license, args.keyword, related=related, communities=args.community)
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(md, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print("wrote " + args.output)
    else:
        with open(args.file, encoding="utf-8") as fh:
            md = json.load(fh)
    errors, warnings = validate(md)
    for e in errors:
        print("error: " + e, file=sys.stderr)
    for w in warnings:
        print("warning: " + w, file=sys.stderr)
    if args.cmd == "validate":
        print("%s: %s" % (args.file, "valid" if not errors else "INVALID"))
    return 1 if errors else 0
