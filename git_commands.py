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

def cmd_log(args):
    """ Display history of a given commit """
    repo = repo_find()
    print("digraph wyaglog{")
    print("    node [shape=rect];")
    
    log_graphviz(repo, object_find(repo, args.commit), set())
    
def log_graphviz(repo, sha, seen):
    """ Generate a graphviz file for the commit history """
    if sha in seen:
        return
    seen.add(sha)
    
    commit = object_read(repo, sha)
    message = commit.kvlm[None].decode('utf-8').strip()
    message = message.replace("\\", "\\\\")
    message = message.replace("\"", "\\\"")
    if "\n" in message:
        message = message[:message.index("\n")]
    
    print(f'    c_"{sha}" [label="{sha}: {message}"];')
    assert commit.fmt==b'commit'
    if not b'parent' in commit.kvlm.keys:
        # Base case: the initial commit
        return
    
    parents = commit.kvlm[b'parent']
    
    if type(parents) != list:
        parents = [ parents ]
        
    for p in parents:
        p = p.decode('ascii')
        print(f'    c_{sha} -> c_{p};')
        log_graphviz(repo, p, seen)