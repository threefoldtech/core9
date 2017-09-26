from .GitClient import GitClient
from JumpScale9 import j
import os
import re


class GitFactory:

    def __init__(self):
        self.logger = j.logger.get('j.clients.git')
        self.__jslocation__ = "j.clients.git"


    def execute(self, *args, **kwargs):
        return j.do.execute(*args, **kwargs)

    def rewriteGitRepoUrl(self, url="", login=None, passwd=None, ssh="auto"):
        """
        Rewrite the url of a git repo with login and passwd if specified

        Args:
            url (str): the HTTP URL of the Git repository. ex: 'https://github.com/odoo/odoo'
            login (str): authentication login name
            passwd (str): authentication login password
            ssh = if True will build ssh url, if "auto" will check if there is ssh-agent available & keys are loaded,
                if yes will use ssh

        Returns:
            (repository_host, repository_type, repository_account, repository_name, repository_url, port)
        """

        if ssh == "auto" or ssh == "first":
            ssh = j.clients.ssh.SSHAgentAvailable()
        elif ssh or ssh is False:
            pass
        else:
            raise RuntimeError(
                "ssh needs to be auto, first or True or False: here:'%s'" %
                ssh)

        url=url.replace("ssh://","")


        port=None
        if ssh:
            try:
                port=int(url.split(":")[1].split("/")[0])
                url=url.replace(":%s/"%(port),":")
            except:
                pass
            

        url_pattern_ssh = re.compile('^(git@)(.*?):(.*?)/(.*?)/?$')
        sshmatch = url_pattern_ssh.match(url)
        url_pattern_ssh = re.compile('^(git@)(.*?)/(.*?)/(.*?)/?$')
        sshmatch2 = url_pattern_ssh.match(url)
        url_pattern_http = re.compile('^(https?://)(.*?)/(.*?)/(.*?)/?$')
        httpmatch = url_pattern_http.match(url)
        if sshmatch:
            match = sshmatch
        elif sshmatch2:
            match = sshmatch2
        elif httpmatch:
            match = httpmatch
        else:
            raise RuntimeError(
                "Url is invalid. Must be in the form of 'http(s)://hostname/account/repo' or 'git@hostname:account/repo'\nnow:%s"%url)

        protocol, repository_host, repository_account, repository_name = match.groups()

        if sshmatch2:
            from IPython import embed;embed(colors='Linux')
            s
            
        if protocol.startswith("git") and ssh is False:
            protocol = "https://"

        if not repository_name.endswith('.git'):
            repository_name += '.git'

        if login == 'ssh' or ssh:
            if port ==None:
                repository_url = 'ssh://git@%(host)s:%(account)s/%(name)s' % {
                    'host': repository_host,
                    'account': repository_account,
                    'name': repository_name,
                }
            else:
                repository_url = 'ssh://git@%(host)s:%(port)s/%(account)s/%(name)s' % {
                    'host': repository_host,
                    'port': port,
                    'account': repository_account,
                    'name': repository_name,
                }
            protocol = "ssh"

        elif login and login != 'guest':
            repository_url = '%(protocol)s%(login)s:%(password)s@%(host)s/%(account)s/%(repo)s' % {
                'protocol': protocol,
                'login': login,
                'password': passwd,
                'host': repository_host,
                'account': repository_account,
                'repo': repository_name,
            }

        else:
            repository_url = '%(protocol)s%(host)s/%(account)s/%(repo)s' % {
                'protocol': protocol,
                'host': repository_host,
                'account': repository_account,
                'repo': repository_name,
            }
        if repository_name.endswith(".git"):
            repository_name = repository_name[:-4]

        return protocol, repository_host, repository_account, repository_name, repository_url,port

    def getGitRepoArgs(
            self,
            url="",
            dest=None,
            login=None,
            passwd=None,
            reset=False,
            branch=None,
            ssh="auto",
            codeDir=None,
            executor=None):
        """
        Extracts and returns data useful in cloning a Git repository.

        Args:
            url (str): the HTTP/GIT URL of the Git repository to clone from. eg: 'https://github.com/odoo/odoo.git'
            dest (str): the local filesystem path to clone to
            login (str): authentication login name (only for http)
            passwd (str): authentication login password (only for http)
            reset (boolean): if True, any cached clone of the Git repository will be removed
            branch (str): branch to be used
            ssh if auto will check if ssh-agent loaded, if True will be forced to use ssh for git

        # Process for finding authentication credentials (NOT IMPLEMENTED YET)

        - first check there is an ssh-agent and there is a key attached to it, if yes then no login & passwd will be used & method will always be git
        - if not ssh-agent found
            - then we will check if url is github & ENV argument GITHUBUSER & GITHUBPASSWD is set
                - if env arguments set, we will use those & ignore login/passwd arguments
            - we will check if login/passwd specified in URL, if yes willl use those (so they get priority on login/passwd arguments)
            - we will see if login/passwd specified as arguments, if yes will use those
        - if we don't know login or passwd yet then
            - login/passwd will be fetched from local git repo directory (if it exists and reset==False)
        - if at this point still no login/passwd then we will try to build url with anonymous


        # Process for defining branch

        - if branch arg: None
            - check if git directory exists if yes take that branch
            - default to 'master'
        - if it exists, use the branch arg

        Returns:
            (repository_host, repository_type, repository_account, repository_name, dest, repository_url)

            - repository_type http or git

        Remark:
            url can be empty, then the git params will be fetched out of the git configuration at that path
        """

        if url == "":
            if dest is None:
                raise RuntimeError("dest cannot be None (url is also '')")
            if not j.do.exists(dest):
                raise RuntimeError(
                    "Could not find git repo path:%s, url was not specified so git destination needs to be specified." %
                    (dest))

        if login is None and url.find("github.com/") != -1:
            # can see if there if login & passwd in OS env
            # if yes fill it in
            if "GITHUBUSER" in os.environ:
                login = os.environ["GITHUBUSER"]
            if "GITHUBPASSWD" in os.environ:
                passwd = os.environ["GITHUBPASSWD"]

        protocol, repository_host, repository_account, repository_name, repository_url, port = self.rewriteGitRepoUrl(
            url=url, login=login, passwd=passwd, ssh=ssh)

        repository_type = repository_host.split(
            '.')[0] if '.' in repository_host else repository_host

        if not dest:
            if codeDir is None:
                if not executor:
                    codeDir = j.dirs.CODEDIR
                else:
                    codeDir = executor.prefab.core.dir_paths['CODEDIR']
            dest = '%(codedir)s/%(type)s/%(account)s/%(repo_name)s' % {
                'codedir': codeDir,
                'type': repository_type.lower(),
                'account': repository_account.lower(),
                'repo_name': repository_name,
            }

        if reset:
            self.delete(dest)

        # self.createDir(dest)

        return repository_host, repository_type, repository_account, repository_name, dest, repository_url, port

    def pullGitRepo(
            self,
            url="",
            dest=None,
            login=None,
            passwd=None,
            depth=None,
            ignorelocalchanges=False,
            reset=False,
            branch=None,
            tag=None,
            revision=None,
            ssh="auto",
            executor=None,
            codeDir=None,
            timeout=600):
        """
        will clone or update repo
        if dest is None then clone underneath: /opt/code/$type/$account/$repo
        will ignore changes !!!!!!!!!!!

        @param ssh ==True means will checkout ssh
        @param ssh =="first" means will checkout sss first if that does not work will go to http
        """
        if branch == "":
            branch = None
        if branch is not None and tag is not None:
            raise RuntimeError("only branch or tag can be set")

        if ssh == "first" or ssh == "auto":
            try:
                return self.pullGitRepo(
                    url,
                    dest,
                    login,
                    passwd,
                    depth,
                    ignorelocalchanges,
                    reset,
                    branch,
                    tag=tag,
                    revision=revision,
                    ssh=True,
                    executor=executor)
            except Exception as e:
                base, provider, account, repo, dest, url,port = self.getGitRepoArgs(
                    url, dest, login, passwd, reset=reset, ssh=False, codeDir=codeDir, executor=executor)
                return self.pullGitRepo(
                    url,
                    dest,
                    login,
                    passwd,
                    depth,
                    ignorelocalchanges,
                    reset,
                    branch,
                    tag=tag,
                    revision=revision,
                    ssh=False,
                    executor=executor)

        base, provider, account, repo, dest, url,port = self.getGitRepoArgs(
            url, dest, login, passwd, reset=reset, ssh=ssh, codeDir=codeDir, executor=executor)

        self.logger.info("%s:pull:%s ->%s" % (executor, url, dest))

        existsDir = j.do.exists(
            dest) if not executor else executor.exists(dest)

        checkdir = "%s/.git" % (dest)
        existsGit = j.do.exists(
            checkdir) if not executor else executor.exists(checkdir)

        if existsDir:
            if not existsGit:
                raise RuntimeError("found directory but .git not found in %s" % dest)
            # if we don't specify the branch, try to find the currently
            # checkedout branch
            cmd = 'cd %s; git rev-parse --abbrev-ref HEAD' % dest
            rc, out, err = self.execute(
                cmd, die=False, showout=False, executor=executor)
            if rc == 0:
                branchFound = out.strip()
            else:  # if we can't retreive current branch, use master as default
                branchFound = 'master'
                # raise RuntimeError("Cannot retrieve branch:\n%s\n" % cmd)
            if branch is not None and branch != branchFound and ignorelocalchanges is False:
                raise RuntimeError(
                    "Cannot pull repo '%s', branch on filesystem is not same as branch asked for.\n"
                    "Branch asked for: %s\n"
                    "Branch found: %s\n"
                    "To choose other branch do e.g:"
                    "export JSBRANCH='%s'\n" %
                    (repo, branch, branchFound, branchFound))

            if ignorelocalchanges:
                self.logger.info(
                    ("git pull, ignore changes %s -> %s" %
                     (url, dest)))
                cmd = "cd %s;git fetch" % dest
                if depth is not None:
                    cmd += " --depth %s" % depth
                    self.execute(cmd, executor=executor)
                if branch is not None:
                    self.logger.info("reset branch to:%s" % branch)
                    self.execute(
                        "cd %s;git fetch; git reset --hard origin/%s" %
                        (dest, branch), timeout=timeout, executor=executor)

            else:

                if branch is None and tag is None:
                    branch = branchFound

                # pull
                self.logger.info(("git pull %s -> %s" % (url, dest)))
                if url.find("http") != -1:
                    cmd = "mkdir -p %s;cd %s;git -c http.sslVerify=false pull origin %s" % (
                        dest, dest, branch)
                    self.logger.info(cmd)
                    self.execute(cmd, timeout=timeout, executor=executor)
                else:
                    try:
                        cmd = "cd %s;git pull origin %s" % (dest, branch)
                        self.logger.info(cmd)
                        self.execute(cmd, timeout=timeout, executor=executor)
                    except Exception as e:
                        protocol, host, account, repo_name, repo_url = self.rewriteGitRepoUrl(url=url, ssh=False)
                        cmd = "cd %s;git -c http.sslVerify=false pull %s %s" % (dest, repo_url, branch)
                        self.logger.info(cmd)
                        self.execute(cmd, timeout=timeout, executor=executor)

        else:
            self.logger.info(("git clone %s -> %s" % (url, dest)))
            # self.createDir(dest)
            extra = ""
            if depth is not None:
                extra = "--depth=%s" % depth
            if url.find("http") != -1:
                if branch is not None:
                    cmd = "mkdir -p %s;cd %s;git -c http.sslVerify=false clone %s -b %s %s %s" % (
                        j.sal.fs.getParent(dest), j.sal.fs.getParent(dest), extra, branch, url, dest)
                else:
                    cmd = "mkdir -p %s;cd %s;git -c http.sslVerify=false clone %s  %s %s" % (
                        j.sal.fs.getParent(dest), j.sal.fs.getParent(dest), extra, url, dest)
            else:
                if branch is not None:
                    cmd = "mkdir -p %s;cd %s;git clone %s -b %s %s %s" % (
                        j.sal.fs.getParent(dest), j.sal.fs.getParent(dest), extra, branch, url, dest)
                else:
                    cmd = "mkdir -p %s;cd %s;git clone %s  %s %s" % (
                        j.sal.fs.getParent(dest), j.sal.fs.getParent(dest), extra, url, dest)

            self.logger.info(cmd)

            # self.logger.info(str(executor)+" "+cmd)
            self.execute(cmd, timeout=timeout, executor=executor)

        if tag is not None:
            self.logger.info("reset tag to:%s" % tag)
            self.execute("cd %s;git checkout tags/%s" %
                         (dest, tag), timeout=timeout, executor=executor)

        if revision is not None:
            cmd = "mkdir -p %s;cd %s;git checkout %s" % (dest, dest, revision)
            self.logger.info(cmd)
            self.execute(cmd, timeout=timeout, executor=executor)

        return dest

    def getGitBranch(self, path):

        # if we don't specify the branch, try to find the currently checkedout
        # branch
        cmd = 'cd %s;git rev-parse --abbrev-ref HEAD' % path
        try:
            rc, out, err = self.execute(cmd, showout=False, outputStderr=False)
            if rc == 0:
                branch = out.strip()
            else:  # if we can't retreive current branch, use master as default
                branch = 'master'
        except BaseException:
            branch = 'master'

        return branch





    def parseUrl(self, url):
        """
        @return (repository_host, repository_type, repository_account, repository_name, repository_url,branch,gitpath, relpath,repository_port)

        example Input
        - https://github.com/Jumpscale/NOS/blob/master/specs/NOS_1.0.0.md
        - https://github.com/Jumpscale/jumpscale_core9/blob/8.1.2/lib/JumpScale/tools/docgenerator/macros/dot.py
        - https://github.com/Jumpscale/jumpscale_core9/tree/8.2.0/lib/JumpScale/tools/docgenerator/macros
        - https://github.com/Jumpscale/jumpscale_core9/tree/master/lib/JumpScale/tools/docgenerator/macros

        """

        repository_host, repository_type, repository_account, repository_name, repository_url = self.rewriteGitRepoUrl(
            url)

        url_end = ""
        if "tree" in repository_url:
            # means is a directory
            repository_url, url_end = repository_url.split("tree")
        elif "blob" in repository_url:
            # means is a directory
            repository_url, url_end = repository_url.split("blob")
        if url_end != "":
            url_end = url_end.strip("/")
            if url_end.find("/") == -1:
                path = ""
                branch = url_end
                if branch.endswith(".git"):
                    branch = branch[:-4]
            else:
                branch, path = url_end.split("/", 1)
                if path.endswith(".git"):
                    path = path[:-4]
        else:
            path = ""
            branch = ""

        a, b, c, d, dest, e,port = self.getGitRepoArgs(url)

        if "tree" in dest:
            # means is a directory
            gitpath, ee = dest.split("tree")
        elif "blob" in repository_url:
            # means is a directory
            gitpath, ee = dest.split("blob")
        else:
            gitpath = dest

        return (
            repository_host,
            repository_type,
            repository_account,
            repository_name,
            repository_url,
            branch,
            gitpath,
            path,
            port)

    def getContentInfoFromURL(self, url):
        """
        @return (giturl,gitpath,relativepath)

        example Input
        - https://github.com/Jumpscale/NOS/blob/master/specs/NOS_1.0.0.md
        - https://github.com/Jumpscale/jumpscale_core9/blob/8.1.2/lib/JumpScale/tools/docgenerator/macros/dot.py
        - https://github.com/Jumpscale/jumpscale_core9/tree/8.2.0/lib/JumpScale/tools/docgenerator/macros
        - https://github.com/Jumpscale/jumpscale_core9/tree/master/lib/JumpScale/tools/docgenerator/macros

        """
        repository_host, repository_type, repository_account, repository_name, repository_url, branch, gitpath, relpath, port = j.clients.git.parseUrl(
            url)
        rpath = j.sal.fs.joinPaths(gitpath, relpath)
        if not j.sal.fs.exists(rpath, followlinks=True):
            j.clients.git.pullGitRepo(repository_url, branch=branch)
        if not j.sal.fs.exists(rpath, followlinks=True):
            raise j.exceptions.Input(message="Did not find path in git:%s" %
                                     rpath, level=1, source="", tags="", msgpub="")

        return (repository_url, gitpath, relpath)

    def pullGitRepoSubPath(self, urlOrPath):
        """
        @return path of the content found

        will find the right branch & will do a pull

        example Input
        - https://github.com/Jumpscale/NOS/blob/master/specs/NOS_1.0.0.md
        - https://github.com/Jumpscale/jumpscale_core9/blob/8.1.2/lib/JumpScale/tools/docgenerator/macros/dot.py
        - https://github.com/Jumpscale/jumpscale_core9/tree/8.2.0/lib/JumpScale/tools/docgenerator/macros
        - https://github.com/Jumpscale/jumpscale_core9/tree/master/lib/JumpScale/tools/docgenerator/macros

        """
        if not j.sal.fs.exists(urlOrPath, followlinks=True):
            repository_url, gitpath, relativepath = self.getContentInfoFromURL(urlOrPath)
        else:
            repository_host, repository_type, repository_account, repository_name, repository_url, branch, gitpath, relativepath = j.clients.git.parseUrl(
                urlOrPath)
            j.clients.git.pullGitRepo(repository_url, branch=branch)  # to make sure we pull the info

        path = j.sal.fs.joinPaths(gitpath, relativepath)
        return path

    def getContentPathFromURLorPath(self, urlOrPath):
        """

        @return path of the content found, will also do a pull to make sure git repo is up to date

        example Input
        - https://github.com/Jumpscale/NOS/blob/master/specs/NOS_1.0.0.md
        - https://github.com/Jumpscale/jumpscale_core9/blob/8.1.2/lib/JumpScale/tools/docgenerator/macros/dot.py
        - https://github.com/Jumpscale/jumpscale_core9/tree/8.2.0/lib/JumpScale/tools/docgenerator/macros
        - https://github.com/Jumpscale/jumpscale_core9/tree/master/lib/JumpScale/tools/docgenerator/macros

        """
        if j.sal.fs.exists(urlOrPath, followlinks=True):

            return urlOrPath
        repository_url, gitpath, relativepath = self.getContentInfoFromURL(urlOrPath)
        path = j.sal.fs.joinPaths(gitpath, relativepath)
        return path

    def get(self, basedir="", check_path=True):
        """
        PLEASE USE SSH, see http://gig.gitbooks.io/jumpscale/content/Howto/how_to_use_git.html for more details
        """
        if basedir == "":
            basedir = j.sal.fs.getcwd()
        return GitClient(basedir, check_path=check_path)

    def find(self, account=None, name=None, interactive=False, returnGitClient=False):  # NOQA
        """
        walk over repo's known on system
        2 locations are checked
            ~/code
            /opt/code
        """
        if name is None:
            name = ""
        if account is None:
            account = ""

        accounts = []
        accounttofind = account

        def checkaccount(account):
            # print accounts
            # print "%s %s"%(account,accounttofind)
            if account not in accounts:
                if accounttofind.find("*") != -1:
                    if accounttofind == "*" or account.startswith(accounttofind.replace("*", "")):
                        accounts.append(account)
                elif accounttofind != "":
                    if account.lower().strip() == accounttofind.lower().strip():
                        accounts.append(account)
                else:
                    accounts.append(account)
            # print accountsunt in accounts
            return account in accounts

        def _getRepos(codeDir, account=None, name=None):  # NOQA
            """
            @param interactive if interactive then will ask to select repo's out of the list
            @para returnGitClient if True will return gitclients as result

            returns (if returnGitClient)
            [[type,account,reponame,path]]

            the type today is git or github today
            all std git repo's go to git

            ```
            #example
            [['github', 'docker', 'docker-py', '/opt/code/github/docker/docker-py'],
            ['github', 'jumpscale', 'docs', '/opt/code/github/jumpscale/docs']]
            ```

            """
            repos = []
            for top in j.sal.fs.listDirsInDir(codeDir, recursive=False,
                                              dirNameOnly=True, findDirectorySymlinks=True):
                for account in j.sal.fs.listDirsInDir("%s/%s" % (j.dirs.CODEDIR, top), recursive=False,
                                                      dirNameOnly=True, findDirectorySymlinks=True):
                    if checkaccount(account):
                        accountdir = "%s/%s/%s" % (j.dirs.CODEDIR,
                                                   top, account)
                        if j.sal.fs.exists(path="%s/.git" % accountdir):
                            raise j.exceptions.RuntimeError(
                                "there should be no .git at %s level" % accountdir)
                        else:
                            for reponame in j.sal.fs.listDirsInDir("%s/%s/%s" % (j.dirs.CODEDIR, top, account),
                                                                   recursive=False, dirNameOnly=True,
                                                                   findDirectorySymlinks=True):
                                repodir = "%s/%s/%s/%s" % (
                                    j.dirs.CODEDIR, top, account, reponame)
                                if j.sal.fs.exists(path="%s/.git" % repodir):
                                    if name.find("*") != -1:
                                        if name == "*" or reponame.startswith(name.replace("*", "")):
                                            repos.append(
                                                [top, account, reponame, repodir])
                                    elif name != "":
                                        if reponame.lower().strip() == name.lower().strip():
                                            repos.append(
                                                [top, account, reponame, repodir])
                                    else:
                                        repos.append(
                                            [top, account, reponame, repodir])
            return repos

        j.sal.fs.createDir(j.sal.fs.joinPaths(os.getenv("HOME"), "code"))
        repos = _getRepos(j.dirs.CODEDIR, account, name)

        accounts.sort()

        if interactive:
            result = []
            if len(repos) > 20:
                print("Select account to choose from, too many choices.")
                accounts = j.tools.console.askChoiceMultiple(accounts)

            repos = [item for item in repos if item[1] in accounts]

            # only ask if * in name or name not specified
            if name.find("*") == -1 or name is None:
                repos = j.tools.console.askArrayRow(repos)

        result = []
        if returnGitClient:
            for top, account, reponame, repodir in repos:
                cl = self.get(repodir)
                result.append(cl)
        else:
            result = repos

        return result

    def findGitPath(self, path):
        while path != "":
            if j.sal.fs.exists(path=j.sal.fs.joinPaths(path, ".git")):
                return path
            path = j.sal.fs.getParent(path)
        raise j.exceptions.Input("Cannot find git path in:%s" % path)

    def parseGitConfig(self, repopath):
        """
        @param repopath is root path of git repo
        @return (giturl,account,reponame,branch,login,passwd)
        login will be ssh if ssh is used
        login & passwd is only for https
        """
        path = j.sal.fs.joinPaths(repopath, ".git", "config")
        if not j.sal.fs.exists(path=path):
            raise RuntimeError("cannot find %s" % path)
        config = j.sal.fs.readFile(path)
        state = "start"
        for line in config.split("\n"):
            line2 = line.lower().strip()
            if state == "remote":
                if line.startswith("url"):
                    url = line.split("=", 1)[1]
                    url = url.strip().strip("\"").strip()
            if line2.find("[remote") != -1:
                state = "remote"
            if line2.find("[branch"):
                branch = line.split(" \"")[1].strip("]\" ").strip("]\" ").strip("]\" ")

    def getGitReposListLocal(self, provider="", account="", name="", errorIfNone=True):
        repos = {}
        for top in j.sal.fs.listDirsInDir(
                j.dirs.CODEDIR,
                recursive=False,
                dirNameOnly=True,
                findDirectorySymlinks=True):
            if provider != "" and provider != top:
                continue
            for accountfound in j.sal.fs.listDirsInDir("%s/%s" % (j.dirs.CODEDIR, top),
                                                       recursive=False, dirNameOnly=True, findDirectorySymlinks=True):
                if account != "" and account != accountfound:
                    continue
                accountfounddir = "/%s/%s/%s" % (j.dirs.CODEDIR, top, accountfound)
                for reponame in j.sal.fs.listDirsInDir(
                    "%s/%s/%s" %
                    (j.dirs.CODEDIR,
                     top,
                     accountfound),
                    recursive=False,
                    dirNameOnly=True,
                        findDirectorySymlinks=True):
                    if name != "" and name != reponame:
                        continue
                    repodir = "%s/%s/%s/%s" % (j.dirs.CODEDIR, top, accountfound, reponame)
                    if j.sal.fs.exists(path="%s/.git" % repodir):
                        repos[reponame] = repodir
        if len(list(repos.keys())) == 0:
            raise RuntimeError("Cannot find git repo '%s':'%s':'%s'" % (provider, account, name))
        return repos

    def pushGitRepos(self, message, name="", update=True, provider="", account=""):
        """
        if name specified then will look under code dir if repo with path can be found
        if not or more than 1 there will be error
        @param provider e.g. git, github
        """
        # TODO: make sure we use gitlab or github account if properly filled in
        repos = self.getGitReposListLocal(provider, account, name)
        for name, path in list(repos.items()):
            print(("push git repo:%s" % path))
            cmd = "cd %s;git add . -A" % (path)
            j.sal.process.executeInteractive(cmd)
            cmd = "cd %s;git commit -m \"%s\"" % (path, message)
            j.sal.process.executeInteractive(cmd)
            branch = self.getGitBranch(path)
            if update:
                cmd = "cd %s;git pull origin %s" % (path, branch)
                j.sal.process.executeInteractive(cmd)
            cmd = "cd %s;git push origin %s" % (path, branch)
            j.sal.process.executeInteractive(cmd)

    def updateGitRepos(self, provider="", account="", name="", message=""):
        repos = self.getGitReposListLocal(provider, account, name)
        for name, path in list(repos.items()):
            print(("push git repo:%s" % path))
            branch = self.getGitBranch(path)
            cmd = "cd %s;git add . -A" % (path)
            j.sal.process.executeInteractive(cmd)
            cmd = "cd %s;git commit -m \"%s\"" % (path, message)
            j.sal.process.executeInteractive(cmd)
            cmd = "cd %s;git pull origin %s" % (path, branch)
            j.sal.process.executeInteractive(cmd)

    def changeLoginPasswdGitRepos(self, provider="", account="", name="",
                                  login="", passwd="", ssh=True, pushmessage=""):
        """
        walk over all git repo's found in account & change login/passwd
        """
        if ssh is False:
            for reponame, repopath in list(self.getGitReposListLocal(provider, account, name).items()):
                import re
                configpath = "%s/.git/config" % repopath
                text = j.sal.fs.readFile(configpath)
                text2 = text
                for item in re.findall(re.compile(r'//.*@%s' % provider), text):
                    newitem = "//%s:%s@%s" % (login, passwd, provider)
                    text2 = text.replace(item, newitem)
                if text2.strip() != text:
                    j.sal.fs.writeFile(configpath, text2)
        else:
            for reponame, repopath in list(self.getGitReposListLocal(provider, account, name).items()):
                configpath = "%s/.git/config" % repopath
                text = j.sal.fs.readFile(configpath)
                text2 = ""
                change = False
                for line in text.split("\n"):
                    if line.replace(" ", "").find("url=") != -1:
                        # print line
                        if line.find("@git") == -1:
                            # print 'REPLACE'
                            provider2 = line.split("//", 1)[1].split("/", 1)[0].strip()
                            account2 = line.split("//", 1)[1].split("/", 2)[1]
                            name2 = line.split("//", 1)[1].split("/", 2)[2].replace(".git", "")
                            line = "\turl = git@%s:%s/%s.git" % (provider2, account2, name2)
                            change = True
                        # print line
                    text2 += "%s\n" % line

                if change:
                    # print text
                    # print "===="
                    # print text2
                    # print "++++"
                    print(("changed login/passwd/git on %s" % configpath))
                    j.sal.fs.writeFile(configpath, text2)

        if pushmessage != "":
            self.pushGitRepos(pushmessage, name=name, update=True, provider=provider, account=account)
