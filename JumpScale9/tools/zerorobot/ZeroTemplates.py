
from js9 import j


class ZeroTemplate():
    def __init__(self):
        self._model = None
        self.guid = None

    @property
    def model(self):
        if self._model is None:
            if self.guid is None:
                self._model = j.tools.zerorobot.messages.Template()
            else:
                self_model = None
        return self._model

    def _loadFromPath(self, domain, path):
        self.model.name = j.sal.fs.getBaseName(path)
        from IPython import embed
        embed(colors='Linux')

    def _processTemplateActions(self, path):
        state = "start"
        C = j.sal.fs.fileGetContents(path)
        basename = j.sal.fs.getBaseName(path)
        name = basename.replace(".py", "").lower()
        out = "class %s():\n" % name
        for line in C.split("\n"):
            # if state=="method":
            #     if line.strip().find("def")==0:

            if state == "class":
                # now processing the methods
                if line.strip().find("def") == 0:
                    # state=="method"
                    pre = line.split("(", 1)[0]
                    pre = pre.replace("def ", "")
                    method_name = pre.strip()
                    out += "    @app.task(name='%s_%s')\n" % (name,
                                                              method_name)

                out += "%s\n" % line

            if line.strip().find("class") == 0:
                state = "class"
        out += "\n"
        return out


class ZeroTemplates:

    def load(self, path=None):
        if path is None:
            repos = j.clients.git.getGitReposListLocal()
            for key, val in repos.items():
                if key.startswith("zerorobot"):
                    self.load(repos[key])
        else:
            tpath = "%s/templates/" % path
            if j.sal.fs.exists(tpath):
                for tpath2 in j.sal.fs.listDirsInDir(tpath, recursive=True, dirNameOnly=False):
                    self._loadTemplate(domain, tpath2)

    def _loadTemplate(self, path):
        name = j.sal.fs.getBaseName(path)
        templ = ZeroTemplate()
        templ._loadFromPath(path)
        from IPython import embed
        embed(colors='Linux')
