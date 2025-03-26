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
