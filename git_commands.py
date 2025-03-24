from GitRepository import *
from GitObject import *
import sys

def cmd_init(args):
    """ Create a new repository """
    repo_create(args.path)

def cmd_cat_file(args):
    """ Provide content of repository objects """
    repo = repo_find()
    cat_file(repo, args.object, fmt=args.type.encode())

def cat_file(repo, obj, fmt=None):
    """ Provide content of repository objects """
    obj = object_read(repo, object_find(repo, obj, fmt=fmt))
    sys.stdout.buffer.write(obj.serialize())
    
def cmd_hash_object(args):
    """ Compute object ID and optionally creates a blob from a file """
    if args.write:
        repo = repo_find()
    else:
        repo = None
    
    with open(args.path, "rb") as fd:
        sha = object_hash(fd, args.type.encode(), repo)
        print(sha)
