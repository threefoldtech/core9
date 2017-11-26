
from js9 import j


class ZeroDomains:

    def init(self, name, giturl):
        d = ZeroDomain()

    def load(self, path=None):
        if path == None:
            repos = j.clients.git.getGitReposListLocal()
            for key, val in repos.items():
                if key.startswith("zerorobot"):
                    self.load(repos[key])
        else:
            tpath = "%s/templates/" % path
            if j.sal.fs.exists(tpath):
                for tpath2 in j.sal.fs.listDirsInDir(tpath, recursive=True, dirNameOnly=False):
                    self._loadTemplate(tpath2)

    def _loadTemplate(self, path):
        name = j.sal.fs.getBaseName(path)
        templ = ZeroTemplate()
        templ._loadFromPath(path)
        from IPython import embed
        embed(colors='Linux')
