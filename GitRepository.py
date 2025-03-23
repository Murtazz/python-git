import os
import configparser

class GitRepository:
    """ A git repository """
    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, '.git')

        if not (force or os.path.isdir(self.gitdir)):
            raise NotADirectoryError(f"Not a Git repository {path}")

        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise FileNotFoundError("Configuration file missing")
        if not force:
            version = int(self.conf.get("core", "repositoryformatversion"))
            if version != 0:
                raise ValueError(f"Unsupported repositoryformatversion {version}")

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

def repo_default_config():
    """ Return a default configuration object """
    settings = configparser.ConfigParser()

    settings.add_section("core")
    settings.set("core", "repositoryformatversion", "0")
    settings.set("core", "filemode", "false")
    settings.set("core", "bare", "false")
    return settings

def repo_create(path):
    """ Create a new repository at path """
    repo = GitRepository(path, True)

    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise OSError(f"-----{path} is not a directory (¬_¬)")
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise OSError(f"-----{path} is not an empty directory (¬_¬)")
    else:
        os.makedirs(repo.worktree)

    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # .git/description
    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    # .git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    # .git/config
    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo
