import os

def repo_file(repo, *path):
    """ Compute path under repo's gitdir """
    return os.path.join(repo.gitdir, *path)

def repo_dir(repo, *path, mkdir=False):

    """ Same as repo_file, but mkdir *path if absent.
    For example, repo_dir(r, \"refs\", \"remotes\", \"origin\") will
    create .git/refs/remotes/origin """

    path = repo_file(repo, *path)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            raise NotADirectoryError(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None
