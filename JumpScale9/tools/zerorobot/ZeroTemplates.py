
from js9 import j

from google.protobuf import json_format

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

    def _loadFromPath(self, path):
        self.model.name = j.sal.fs.getBaseName(path)
        #load action files
        for item in j.sal.fs.listFilesInDir(path,False,"*.py"):
            self._processTemplateActions(item)

    def _processTemplateActions(self, path):
        state = "start"
        C = j.sal.fs.fileGetContents(path)
        basename = j.sal.fs.getBaseName(path)
        name = basename.replace(".py", "").lower()
        out = ""
        if C.find("class")!=-1:
            raise RuntimeError("action file not structured properly, needs to be list of defs, no class inside.")
        state=""
        for line in C.split("\n"):
            print(line)
            if state=="method":
                if line.strip().find("def")==0:
                    self._processTemplateAction(method_name,j.data.text.strip(method_content))
                    state=""
                    continue
                method_content+="%s\n"%line

            # now processing the methods
            if state=="" and line.strip().find("def") == 0:
                state="method"
                pre = line.split("(", 1)[0]
                pre = pre.replace("def ", "")
                method_name = pre.strip()
                method_content = line+"\n"
                continue

        if state=="method":
            self._processTemplateAction(method_name,method_content)

    def _processTemplateAction(self,method_name,method_content):
        if method_name in [name for item.name in self.model.actions]:
            raise j.exceptions.Input("method name:%s was already defined for:%s"%(method_name,self))
        
        print(678)
        from IPython import embed;embed(colors='Linux')
        p


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
