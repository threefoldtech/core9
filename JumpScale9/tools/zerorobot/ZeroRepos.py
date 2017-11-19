
from js9 import j
import sys
import inspect


class ZeroRepo():

    def __init__(self,path,gitrepo):
        self.path=path
        self.gitrepo=gitrepo




    



class ZeroRepos():
    def __init__(self):
        self.repos = {}

    def load(self, path=None,repo=None):
        if path is None:
            repos = j.clients.git.getGitReposListLocal()
            for key, repo in repos.items():
                if key.startswith("zerorobot"):
                    self.load(repo=repo,path=repos[key])
        else:
            from IPython import embed;embed(colors='Linux')
            self.repos[name] = ZeroRepo(path=path,gitrepo=repo) 