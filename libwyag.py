import argparse
import configparser
import grp
import pwd
import getpass
import re
import sys
import zlib
from datetime import datetime
from fnmatch import fnmatch
from math import ceil

from git_commands import *

argparser = argparse.ArgumentParser(description="The stupidest content tracker")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

# init
argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
argsp.add_argument("path",
                    metavar="directory",
                    nargs="?",
                    default=".",
                    help="Where to create the repository.")

# cat-file
argsp = argsubparsers.add_parser("cat-file", help="Provide content of repository objects")
argsp.add_argument("type",
                    metavar="type",
                    choices=["blob", "commit", "tag", "tree"],
                    help="Specify the type")
argsp.add_argument("object",
                    metavar="object",
                    help="The object to display")

# hash-object
argsp = argsubparsers.add_parser("hash-object", 
                                 help="Compute object ID and optionally creates a blob from a file")

argsp.add_argument("-t",
                    metavar="type",
                    dest="type",
                    choices=["blob", "commit", "tag", "tree"],
                    default="blob",
                    help="Specify the type")
argsp.add_argument("-w",
                    dest="write",
                    action="store_true",
                    help="Actually write the object into the database")
argsp.add_argument("path",
                    help="Read object from <file>")

# commit log
argsp = argsubparsers.add_parser("log", help="Display history of a given commit.")
argsp.add_argument("commit",
                    default="HEAD",
                    nargs="?",
                    help="Commit to start at.")

# ls-tree
argsp = argsubparsers.add_parser("ls-tree", help="Pretty-print a tree object")
argsp.add_argument("-r",
                    dest="recursive",
                    action="store_true",
                    help="Recurse into sub-trees")
argsp.add_argument("tree",
                   help="A tree-ish object.")

# checkout
argsp = argsubparsers.add_parser("checkout", help="Checkout a commit inside of a directory.")

argsp.add_argument("commit",
                   help="The commit or tree to checkout.")
argsp.add_argument("path",
                   help="The EMPTY directoy to checkout on.")

# show ref
argsp = argsubparsers.add_parser("show-ref", help="List References")

# tag
argsp = argsubparsers.add_parser("tag", help="List and create tags")

argsp.add_argument("-a", action="store_true", dest="create_tag_object", help="Create an annotated tag")

argsp.add_argument("name", nargs="?", help="The new tag's name")

argsp.add_argument("object", default="HEAD", nargs="?", help="The object the new tag will point to")

# rev-parse
argsp = argsubparsers.add_parser(
    "rev-parse",
    help="Parse revision (or other objects) identifiers")

argsp.add_argument("--wyag-type",
                    metavar="type",
                    dest="type",
                    choices=["commit", "tree", "tag", "blob"],
                    default=None,
                    help="Specify the expected type")

argsp.add_argument("name", help="The name to parse")

def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        # case "add"          : cmd_add(args) # TODO
        case "cat-file"     : cmd_cat_file(args)
        # case "check-ignore" : cmd_check_ignore(args) # TODO
        # case "checkout"     : cmd_checkout(args) # TODO
        # case "commit"       : cmd_commit(args) # TODO
        case "hash-object"  : cmd_hash_object(args)
        case "init"         : cmd_init(args)
        # case "log"          : cmd_log(args) # TODO
        # case "ls-files"     : cmd_ls_files(args) # TODO
        # case "ls-tree"      : cmd_ls_tree(args) # TODO
        # case "rev-parse"    : cmd_rev_parse(args) # TODO
        # case "rm"           : cmd_rm(args) # TODO
        # case "show-ref"     : cmd_show_ref(args) # TODO
        # case "status"       : cmd_status(args) # TODO
        # case "tag"          : cmd_tag(args) # TODO
        case _              : print("Bad command.")
