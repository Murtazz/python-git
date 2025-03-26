import zlib
import hashlib
import os
from GitRepository import repo_file

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

# TODO
def object_find(repo, name, fmt=None, follow=True):
    return name

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