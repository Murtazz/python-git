import argparse
import configparser

# import grp
import win32security
import hashlib
import os

# import pwd
import win32net
import getpass

import re
import sys
import zlib
from datetime import datetime
from fnmatch import fnmatch
from math import ceil

argparser = argparse.ArgumentParser(description="The stupidest content tracker")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "add"          : cmd_add(args) # TODO
        case "cat-file"     : cmd_cat_file(args) # TODO
        case "check-ignore" : cmd_check_ignore(args) # TODO
        case "checkout"     : cmd_checkout(args) # TODO
        case "commit"       : cmd_commit(args) # TODO
        case "hash-object"  : cmd_hash_object(args) # TODO
        case "init"         : cmd_init(args) # TODO
        case "log"          : cmd_log(args) # TODO
        case "ls-files"     : cmd_ls_files(args) # TODO
        case "ls-tree"      : cmd_ls_tree(args) # TODO
        case "rev-parse"    : cmd_rev_parse(args) # TODO
        case "rm"           : cmd_rm(args) # TODO
        case "show-ref"     : cmd_show_ref(args) # TODO
        case "status"       : cmd_status(args) # TODO
        case "tag"          : cmd_tag(args) # TODO
        case _              : print("Bad command.") # TODO
