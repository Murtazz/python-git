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