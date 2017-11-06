from JumpScale9 import j
import sys
import os
import shutil
import platform
import time
import fnmatch
import importlib

class FSMethods():

    def getPythonLibSystem(self, jumpscale=False):
        PYTHONVERSION = platform.python_version()
        if j.core.platformtype.myplatform.isMac:
            destjs = "/usr/local/lib/python3.6/site-packages"
        elif j.core.platformtype.myplatform.isWindows:
            destjs = "/usr/lib/python3.4/site-packages"
        else:
            if PYTHONVERSION == '2':
                destjs = "/usr/local/lib/python/dist-packages"
            else:
                destjs = "/usr/local/lib/python3.5/dist-packages"

        if jumpscale:
            destjs += "/JumpScale/"

        j.sal.fs.createDir(destjs)
        return destjs

    textstrip = j.data.text.strip

    def copyTree(
            self,
            source,
            dest,
            keepsymlinks=False,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=[
                "*.egg-info",
                "*.dist-info"],
            ignorefiles=["*.egg-info"],
            rsync=True,
            ssh=False,
            sshport=22,
            recursive=True,
            rsyncdelete=False,
            createdir=False,
            executor=None):
        """
        if ssh format of source or dest is: remoteuser@remotehost:/remote/dir
        """
        if self.debug:
            self.logger.info(("copy %s %s" % (source, dest)))
        if not ssh and not self.exists(source, executor=executor):
            raise RuntimeError("copytree:Cannot find source:%s" % source)

        if executor and not rsync:
            raise RuntimeError("when executor used only rsync supported")
        if rsync:
            excl = ""
            for item in ignoredir:
                excl += "--exclude '%s/' " % item
            for item in ignorefiles:
                excl += "--exclude '%s' " % item
            excl += "--exclude '*.pyc' "
            excl += "--exclude '*.bak' "
            excl += "--exclude '*__pycache__*' "

            pre = ""
            if executor is None:
                if self.isDir(source):
                    if dest[-1] != "/":
                        dest += "/"
                    if source[-1] != "/":
                        source += "/"
                    # if ssh:
                    #     pass
                    #     # if dest.find(":")!=-1:
                    #     #     if dest.find("@")!=-1:
                    #     #         desthost=dest.split(":")[0].split("@", 1)[1].strip()
                    #     #     else:
                    #     #         desthost=dest.split(":")[0].strip()
                    #     #     dir_dest=dest.split(":",1)[1]
                    #     #     cmd="ssh -o StrictHostKeyChecking=no -p %s  %s 'mkdir -p %s'" % (sshport,sshport,dir_dest)
                    #     #     print cmd
                    #     #     self.executeInteractive(cmd)
                    # else:
                    #     self.createDir(dest)
                if dest.find(':') == -1:  # download
                    # self.createDir(self.getParent(dest))
                    dest = dest.split(':')[1] if ':' in dest else dest
            else:
                if not sys.platform.startswith("darwin"):
                    executor.prefab.system.package.ensure('rsync')
                if executor.prefab.core.dir_exists(source):
                    if dest[-1] != "/":
                        dest += "/"
                    if source[-1] != "/":
                        source += "/"

            dest = dest.replace("//", "/")
            source = source.replace("//", "/")

            if deletefirst:
                pre = "set -ex;rm -rf %s;mkdir -p %s;" % (dest, dest)
            elif createdir:
                pre = "set -ex;mkdir -p %s;" % dest

            cmd = "%srsync " % pre
            if keepsymlinks:
                #-l is keep symlinks, -L follow
                cmd += " -rlptgo --partial %s" % excl
            else:
                cmd += " -rLptgo --partial %s" % excl
            if not recursive:
                cmd += " --exclude \"*/\""
            # if self.debug:
            #     cmd += ' --progress'
            if rsyncdelete:
                cmd += " --delete"
            if ssh:
                cmd += " -e 'ssh -o StrictHostKeyChecking=no -p %s' " % sshport
            cmd += " '%s' '%s'" % (source, dest)
            # self.logger.info(cmd)
            if executor is not None:
                rc, out, err = executor.execute(cmd, showout=False)
            else:
                rc, out, err = self.execute(cmd, showout=False, outputStderr=False)
            # print(rc)
            # print(out)
            return
        else:
            old_debug = self.debug
            self.debug = False
            self._copyTree(
                source,
                dest,
                keepsymlinks,
                deletefirst,
                overwriteFiles,
                ignoredir=ignoredir,
                ignorefiles=ignorefiles)
            self.debug = old_debug

    def _copyTree(
            self,
            src,
            dst,
            keepsymlinks=False,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=[
                ".egg-info",
                "__pycache__"],
            ignorefiles=[".egg-info"]):
        """Recursively copy an entire directory tree rooted at src.
        The dst directory may already exist; if not,
        it will be created as well as missing parent directories
        @param src: string (source of directory tree to be copied)
        @param dst: string (path directory to be copied to...should not already exist)
        @param keepsymlinks: bool (True keeps symlinks instead of copying the content of the file)
        @param deletefirst: bool (Set to True if you want to erase destination first, be carefull, this can erase directories)
        @param overwriteFiles: if True will overwrite files, otherwise will not overwrite when destination exists
        """

        self.logger.info('Copy directory tree from %s to %s' % (src, dst), 6)
        if ((src is None) or (dst is None)):
            raise TypeError(
                'Not enough parameters passed in system.fs.copyTree to copy directory from %s to %s ' %
                (src, dst))
        if self.isDir(src):
            if ignoredir != []:
                for item in ignoredir:
                    if src.find(item) != -1:
                        return
            names = os.listdir(src)

            if not self.exists(dst):
                self.createDir(dst)

            errors = []
            for name in names:
                # is only for the name
                name2 = name

                srcname = self.joinPaths(src, name)
                dstname = self.joinPaths(dst, name2)
                if deletefirst and self.exists(dstname):
                    if self.isDir(dstname, False):
                        self.removeDirTree(dstname)
                    if self.isLink(dstname):
                        self.unlink(dstname)

                if keepsymlinks and self.isLink(srcname):
                    linkto = self.readLink(srcname)
                    # self.symlink(linkto, dstname)#, overwriteFiles)
                    try:
                        os.symlink(linkto, dstname)
                    except BaseException:
                        pass
                        # TODO: very ugly change
                elif self.isDir(srcname):
                    # print "1:%s %s"%(srcname,dstname)
                    self.copyTree(
                        srcname,
                        dstname,
                        keepsymlinks,
                        deletefirst,
                        overwriteFiles=overwriteFiles,
                        ignoredir=ignoredir)
                else:
                    # print "2:%s %s"%(srcname,dstname)
                    extt = self.getFileExtension(srcname)
                    if extt == "pyc" or extt == "egg-info":
                        continue
                    if ignorefiles != []:
                        for item in ignorefiles:
                            if srcname.find(item) != -1:
                                continue
                    j.sal.fs.copyFile(srcname, dstname, overwrite=overwriteFiles)
        else:
            raise RuntimeError(
                'Source path %s in system.fs.copyTree is not a directory' %
                src)

class ExecutorMethods():

    def executeBashScript(
            self,
            content="",
            path=None,
            die=True,
            remote=None,
            sshport=22,
            showout=True,
            outputStderr=True,
            sshkey="",
            timeout=600,
            executor=None):
        """
        @param remote can be ip addr or hostname of remote, if given will execute cmds there
        """
        if path is not None:
            content = j.sal.fs.readFile(path)
        if content[-1] != "\n":
            content += "\n"

        if remote is None:
            tmppath = self.getTmpPath("")
            content = "cd %s\n%s" % (tmppath, content)
        else:
            content = "cd /tmp\n%s" % content

        if die:
            content = "set -ex\n%s" % content

        path2 = self.getTmpPath("do.sh")
        j.sal.fs.writeFile(path2, content, strip=True)

        if remote is not None:
            tmppathdest = "/tmp/do.sh"
            if sshkey:
                if not self.SSHKeyGetPathFromAgent(sshkey, die=False) is None:
                    self.execute('ssh-add %s' % sshkey)
                sshkey = '-i %s ' % sshkey.replace('!', '\!')
            self.execute(
                "scp %s -oStrictHostKeyChecking=no -P %s %s root@%s:%s " %
                (sshkey, sshport, path2, remote, tmppathdest), die=die, executor=executor)
            rc, res, err = self.execute(
                "ssh %s -oStrictHostKeyChecking=no -A -p %s root@%s 'bash %s'" %
                (sshkey, sshport, remote, tmppathdest), die=die, timeout=timeout, executor=executor)
        else:
            rc, res, err = self.execute(
                "bash %s" %
                path2, die=die, showout=showout, outputStderr=outputStderr, timeout=timeout, executor=executor)
        return rc, res, err

    def executeCmds(
            self,
            cmdstr,
            showout=True,
            outputStderr=True,
            useShell=True,
            log=True,
            cwd=None,
            timeout=120,
            captureout=True,
            die=True,
            executor=None):
        rc_ = []
        out_ = ""
        for cmd in cmdstr.split("\n"):
            if cmd.strip() == "" or cmd[0] == "#":
                continue
            cmd = cmd.strip()
            rc, out, err = self.execute(cmd, showout, outputStderr, useShell, log, cwd,
                                        timeout, captureout, die, executor=executor)
            rc_.append(str(rc))
            out_ += out

        return rc_, out_

    def executeInteractive(self, command, die=True):
        exitcode = os.system(command)
        if exitcode != 0 and die:
            raise RuntimeError("Could not execute %s" % command)
        return exitcode

    def checkInstalled(self, cmdname):
        """
        @param cmdname is cmd to check e.g. curl
        """
        rc, out, err = self.execute(
            "which %s" %
            cmdname, die=False, showout=False, outputStderr=False)
        if rc == 0:
            return True
        else:
            return False

    def execute(
            self,
            command,
            showout=True,
            outputStderr=True,
            useShell=True,
            log=True,
            cwd=None,
            timeout=0,
            errors=[],
            ok=[],
            captureout=True,
            die=True,
            async=False,
            executor=None):
        """
        @param errors is array of statements if found then exit as error
        return rc,out,err
        """

        command = self.textstrip(command)
        if executor:
            return executor.execute(
                command,
                die=die,
                checkok=False,
                showout=True,
                timeout=timeout)
        else:
            return j.tools.executorLocal.execute(
                command,
                showout=showout,
                outputStderr=outputStderr,
                die=die)

    def psfind(self, name):
        rc, out, err = self.execute("ps ax | grep %s" % name, showout=False)
        for line in out.split("\n"):
            if line.strip() == "":
                continue
            if "grep" in line:
                continue
            return True
        return False

    def killall(self, name):
        rc, out, err = self.execute("ps ax | grep %s" % name, showout=False)
        for line in out.split("\n"):
            # print("L:%s" % line)
            if line.strip() == "":
                continue
            if "grep" in line:
                continue
            line = line.strip()
            pid = line.split(" ")[0]
            self.logger.info("kill:%s (%s)" % (name, pid))
            self.execute("kill -9 %s" % pid, showout=False)
        if self.psfind(name):
            raise RuntimeError("stop debug here")
            raise RuntimeError(
                "Could not kill:%s, is still, there check if its not autorestarting." %
                name)


class InstallTools(ExecutorMethods, FSMethods):
    def __init__(self, debug=False):

        self.__jslocation__ = "j.core.installtools"

        self._asyncLoaded = False
        self._deps = None
        self._config = None
        self.debug=False
        self.platformtype = j.core.platformtype

        self.logger = j.logger.get("installtools")

    def pip(self, items, force=False, executor=None):
        """
        @param items is string or list
        """
        if isinstance(items, list):
            pass
        elif isinstance(items, str):
            items = self.textstrip(items)
            items = [item.strip()
                     for item in items.split("\n") if item.strip() != ""]
        else:
            raise RuntimeError("input can only be string or list")

        for item in items:
            cmd = "pip3 install %s --upgrade" % item
            if executor is None:
                self.executeInteractive(cmd)
            else:
                executor.execute(cmd)

    def getTmpPath(self, filename):
        return "%s/jumpscaleinstall/%s" % ('/tmp', filename)

    @property
    def mascot(self):
        mascotpath = "%s/.mascot.txt" % os.environ["HOME"]
        if not j.sal.fs.exists(mascotpath):
            print("env has not been installed properly (missing mascot), please follow init instructions on https://github.com/Jumpscale/core9")
            sys.exit(1)
        return j.sal.fs.readFile(mascotpath)



    @property
    def epoch(self):
        '''
        Get epoch timestamp (number of seconds passed since January 1, 1970)
        '''
        return int(time.time())

    @property
    def whoami(self):
        if self._whoami is not None:
            return self._whoami
        rc, result, err = self.execute(
            "whoami", die=False, showout=False, outputStderr=False)
        if rc > 0:
            # could not start ssh-agent
            raise RuntimeError(
                "Could not call whoami,\nstdout:%s\nstderr:%s\n" %
                (result, err))
        else:
            self._whoami = result.strip()
        return self._whoami


do = InstallTools()
