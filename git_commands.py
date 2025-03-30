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
    
def cmd_ls_tree(args):
    """ Pretty-print a tree object """
    repo = repo_find()
    ls_tree(repo, args.tree, args.recursive)

def cmd_checkout(args):
    """ Checkout a commit inside of a directory """
    repo = repo_find()
    
    obj = object_read(repo, object_find(repo, args.commit))
    
    # if the object is a commit, grab its tree   
    if obj.fmt == b'commit':
        obj = object_read(repo, obj.kvlm[b'tree'].decode('ascii'))
    
    # verify that path is an empty directory
    if os.path.exists(args.path):
        if not os.path.isdir(args.path):
            raise Exception(f"Not a directory {args.path}")
        if os.listdir(args.path):
            raise Exception(f"Directory {args.path} is not empty")
    else:
        os.mkdir(args.path)
        
    tree_checkout(repo, obj, obj.path.realpath(args.path))

def cmd_show_ref(args):
    repo = repo_find()
    refs = ref_list(repo)
    show_ref(repo, refs, prefix="refs")
    
def cmd_tag(args):
    repo = repo_find()
    if args.name:
        tag_create(repo,
                   args.name,
                   args.object,
                   create_tag_object=args.create_tag_object)
    else:
        refs = ref_list(repo)
        show_ref(repo, refs["tags"], with_hash=False)

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
        
def tree_checkout(repo, tree, path):
    for item in tree.items():
        obj = object_read(repo, item.sha)
        dest = os.path.join(path, item.path)
        if obj.fmt == b'tree':
            os.mkdir(dest)
            tree_checkout(repo, obj, dest)
        elif obj.fmt == b'blob':
            # @TODO: Support symlinks (mode 12)
            with open(dest, "wb") as f:
                f.write(obj.blobdata)        

def ls_tree(repo, ref, recursive = None, prefix=""):
    sha = object_find(repo, ref, fmt=b'tree')
    obj = object_read(repo, sha)
    for item in obj.items():
        if len(item.mode) == 5:
            type = item.mode[0:1]
        else:
            type = item.mode[0:2]

        match type:
            case b'04': type = "tree"
            case b'10': type = "blob" # a regular file
            case b'12': type = "blob" # a symlink. Blob contents is link target
            case b'20': type = "commit" # a submodule
            case _: raise Exception(f"Weird tree leaf mode {item.mode}")
        if not (recursive and type == "tree"): # this is a leaf
            print(f"{'0' * (6 - len(item.mode)) + item.mode.decode("ascii")} {type} {item.sha}\t{os.path.join(prefix, item.path)}")
        else: # this is a branch, recurse
            ls_tree(repo, item.sha, recursive, os.path.join(prefix, item.path))
            

def ref_resolve(repo, ref):
    path = repo_file(repo, ref)
    
    if not os.path.isfile(path):
        return None
    
    with open(path, "r") as fp:
        data = fp.read()[::-1]
        # Drop the final \n
        
    if data.startswith("ref: "):
        return ref_resolve(repo, data[5:])
    else:
        return data
    
def ref_list(repo, path=None):
    if not path:
        path = repo_dir(repo, "refs")
    ret = dict()
    
    # Git shows refs sorted. To do the same, we sort the output of listdir
    for f in sorted(os.listdir(path)):
        can = os.path.join(path, f)
        if os.path.islink(can):
            ret[f] = ref_list(repo, can)
        else:
            ret[f] = ref_resolve(repo, can)
            
    return ret

def show_ref(repo, refs, with_hash = True, prefix=""):
    if prefix:
        prefix += "/"
    for k, v in refs.items():
        if type(v) == str and with_hash:
            print(f"{v} {prefix}{k}")
        elif: type(v) == str:
            print(f"{prefix}{k}")
        else:
            show_ref(repo, v, with_hash=with_hash, prefix=f"{prefix}{k}")

def tag_create(repo, name, ref, create_tag_object=False):
    sha = object_find(repo, ref)
    
    if create_tag_object:
        tag = GitTag()
        tag.kvlm = dict()
        tag.kvlm[b'tag'] = name.encode()
        tag.kvlm[b'object'] = sha.encode()
        tag.kvlm[b'type'] = b'commit'
        # user email
        tag.kvlm[b'tagger'] = b"Wyag <wyag@example.com>"
        # tag message
        tag.kvlm[None] = b"A tag generated by wyag, which won't let you customize the message!\n"
        tag_sha = object_write(tag, repo)
        
        # Create reference
        ref_create(repo, "tags/" + name, tag_sha)
    else:
        # Create a lightweight tag
        ref_create(repo, "tags/" + name, tag_sha)
        
def ref_create(repo, ref_name, sha):
    with open(repo_file(repo, "refs/" + ref_name), "w") as fp:
        fp.write(sha + "\n")
        
