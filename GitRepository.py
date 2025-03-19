import os
import configparser

from utils import *

class GitRepository:
    """ A git repository """
    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, '.git')

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception("Not a Git repository %s" % path)

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
