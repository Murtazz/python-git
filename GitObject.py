import zlib
import hashlib
import os
import re
from GitRepository import repo_file
from git_commands import ref_resolve

class GitObject:
    def __init__(self, data=None):
        if data != None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self):
        raise Exception("Unimplemented!")
    def deserialize(self, data):
        raise Exception("Unimplemented!")
    
    def init(self):
        pass
    
class GitBlob(GitObject):
    fmt = b'blob'
    
    def serialize(self):
        return self.blobdata
    
    def deserialize(self, data):
        self.blobdata = data
        
class GitCommit(GitObject):
    fmt = b'commit'
    
    def deserialize(self, data):
        self.kvlm = kvlm_parse(data)
        
    def serialize(self):
        return kvlm_serialize(self.kvlm)
    
    def init(self):
        self.kvlm = dict()
   
class GitTreeLeaf(GitObject):
    def __init__(self, mode, path, sha):
        self.mode = mode
        self.path = path
        self.sha = sha
        
class GitTag(GitObject):
    fmt = b'tag'

class GitIndexEntry(object):
    def __init__(self, ctime=None, mtime=None, dev=None, ino=None,
                 mode_type=None, mode_perms=None, uid=None, gid=None,
                 fsize=None, sha=None, flag_assume_valid=None, 
                 flag_stage=None, name=None):
        # The last time a file's metadata changed. This is a pair
        # (timestamp in seconds, nanoseconds)
        self.ctime = ctime
        
        # The last time a file's data changed This is a pair
        # (timestamp in seconds, nanoseconds)
        self.mtime = mtime
        
        # The ID of device containing this file
        self.dev = dev
        
        # The file's inode number
        self.ino = ino
        
        # The object type, either b1000 (regular), b1010 (symlink)m
        # b1110 (gitlink)
        self.mode_type = mode_type
        
        # The permissions, an integer
        self.mode_perms = mode_perms
        
        # User ID of owner
        self.uid = uid

        # Group ID of owner
        self.gid = gid
        
        # Size of this object, in bytes
        self.fsize = fsize
        
        # The object's SHA
        self.sha = sha
        self.flag_assume_valid = flag_assume_valid
        self.flag_stage = flag_stage
        
        # Name of the object (full path this time!)
        self.name = name

class GitIndex(object):
    version = None
    entries = []
    # ext = None
    # sha = None
    
    def __init__(self, version=2, entries=None):
        if not entries:
            entries = list()
        self.version = version
        self.entries = entries
        
class GitIgnore(object):
    absolute = None
    scoped = None

    def __init__(self, absolute, scoped):
        self.absolute = absolute
        self.scoped = scoped
        
# --------------------- object helpers ---------------------
def object_read(repo, sha):
    """ Read object sha from Git repository repo. Return a 
    GitObject whose exact type depends on the object."""
    
    path = repo_file(repo, "objects", sha[0:2], sha[2:])
    
    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())
        
        x = raw.find(b' ')
        fmt = raw[0:x]
        
        y = raw.find(b'\x00', x)
        size = int(raw[x:y].decode('ascii'))
        
        if size != len(raw) - y - 1:
            raise Exception(f"Malformed object {sha}: bad length")
        match fmt:
            case b'commit' : c = GitCommit
            case b'tree'   : c = GitTree
            case b'tag'    : c = GitTag
            case b'blob'   : c = GitBlob
            case _: 
                raise Exception(f"Unknown type {fmt.decode('ascii')} for object {sha}")
        
        # Call constructor and return object
        return c(raw[y+1:])
    
def object_write(obj, repo=None):
    # Serialize object data
    data = obj.serialize()
    # Add header 
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    # Compute hash
    sha = hashlib.sha1(result).hexdigest()
    
    if repo:
        # Compute path
        path = repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=True)
        
        if not os.path.exists(path):
            with open(path, "wb") as f:
                # Compress and write
                f.write(zlib.compress(result))
    return sha

def object_find(repo, name, fmt=None, follow=True):
    sha = object_resolve(repo, name)

    if not sha:
        raise Exception(f"No such reference {name}.")

    if len(sha) > 1:
        raise Exception("Ambiguous reference {name}: Candidates are:\n - {'\n - '.join(sha)}.")

    sha = sha[0]

    if not fmt:
        return sha

    while True:
        obj = object_read(repo, sha)
        #     ^^^^^^^^^^^ < this is a bit agressive: we're reading
        # the full object just to get its type.  And we're doing
        # that in a loop, albeit normally short.  Don't expect
        # high performance here.

        if obj.fmt == fmt:
            return sha

        if not follow:
            return None

        # Follow tags
        if obj.fmt == b'tag':
            sha = obj.kvlm[b'object'].decode("ascii")
        elif obj.fmt == b'commit' and fmt == b'tree':
            sha = obj.kvlm[b'tree'].decode("ascii")
        else:
            return None

def object_resolve(repo, name):
    """ Resolve name to an object hash in repo.
    
    This function is aware of:
    - the HEAD literal
    - short and long hashes
    - tags
    - branches
    - remote branches
    """
    candidates = list()
    hashRE = re.compile(r"^([0-9a-Fa-f]{4,40})$")
    
    # empty string? Abort.    
    if not name.strip():
        return None
    
    if name == "HEAD":
        return { ref_resolve(repo, "HEAD") }
    
    if hashRE.match(name):
        
        name = name.lower()
        prefix = name[0:2]
        path = repo_file(repo, "objects", prefix, mkdir=False)
        
        if path:
            rem = name[2:]
            for f in os.listdir(path):
                if f.startswith(rem):
                    candidates.append(prefix + f)
    # try for refrerences
    as_tag = ref_resolve(repo, "refs/tags/" + name)
    if as_tag: # did we find a tag?
        candidates.append(as_tag)
    
    as_branch = ref_resolve(repo, "refs/heads/" + name)
    if as_branch: # did we find a branch?
        candidates.append(as_branch)
    
    return candidates
        
def object_hash(fd, fmt, repo=None):
    """ Hash object, writing it to repo if provided."""
    data = fd.read()
    
    match fmt:
        case b'commit' : obj = GitCommit(data)
        case b'tree'   : obj = GitTree(data)
        case b'tag'    : obj = GitTag(data)
        case b'blob'   : obj = GitBlob(data)
        case _: raise Exception(f"Unknown type {fmt}")
    
    return object_write(obj, repo)

def kvlm_parse(raw, start=0, dct=None):
    if not dct:
        dct = dict()
    
    spc = raw.find(b' ', start)
    n1 = raw.find(b'\n', start)
    
    # If spc is not found or if spc is found after n1, then n1 is the key
    if spc < 0 or n1 < spc:
        assert n1 == start
        dct[None] = raw[start+1:]
        return dct

    key = raw[start:spc]
    
    # Find the end of the line
    end = start
    
    while True:
        end = raw.find(b'\n', end+1)
        if raw[end+1] != ord(' '): break
        
    # Grab the value
    # Also, drop the leading space
    value = raw[spc+1:end].replace(b'\n ', b'\n')
    
    # Dont overwrite existing keys
    if key in dct:
        if type(dct[key]) == list:
            dct[key].append(value)
        else:
            dct[key] = [ dct[key], value ]
    else:
        dct[key] = value
    
    return kvlm_parse(raw, start=end+1, dct=dct)

def kvlm_serialize(kvlm):
    ret = b''
    
    # output fields
    for k in kvlm.keys():
        # Skip the null key
        if k == None: continue
        
        val = kvlm[k]
        
        # Normalize to a list
        if type(val) != list:
            val = [ val ]
        
        for v in val:
            ret += k + b' ' + v.replace(b'\n', b'\n ') + b'\n'
    
    ret += '\n' + kvlm[None]
    return ret

def tree_serialize(obj):
    obj.items.sort(key=tree_leaf_sort_key)
    ret = b''
    for i in obj.items():
        ret += i.mode
        ret += b' '
        ret += i.path.encode("utf8")
        ret += b'\x00'
        sha = int(i.sha, 16)
        ret += sha.to_bytes(20, byteorder="big")
    return ret

class GitTree(GitObject):
    fmt = b'tree'
    def deserialize(self, data):
        self.items = tree_parse(data)
    def serialize(self):
        return tree_serialize(self)
    def init(self):
        self.items = list()

def tree_parse_one(raw, start=0):
    # find the space terminator of the mode
    x = raw.find(b' ', start)
    assert x-start == 5 or x-start == 6
    
    # read the mode
    mode = raw[start:x]
    if len(mode) == 5:
        mode = b"0" + mode
    
    # find the NULL terminator of the path
    y = raw.find(b'\x00', x)
    # and read the path
    path = raw[x+1:y]
    
    # read the SHA
    raw_sha = int.from_bytes(raw[y+1:y+21], "big")
    # and convert to hex string, padded to 40 chars
    # with zeros if necessary
    sha = format(raw_sha, "040x")
    return y+21, GitTreeLeaf(mode, path, sha)

def tree_parse(raw, start=0):
    pos = 0
    max = len(raw)
    ret = list()
    while pos < max:
        pos, data = tree_parse_one(raw, pos)
        ret.append(data)
    return ret

def tree_leaf_sort_key(leaf):
    if leaf.mode.startswith(b"10"):
        return leaf.path
    else:
        return leaf.path