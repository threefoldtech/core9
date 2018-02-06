import uuid, docker, os
from io import BytesIO
from tarfile import TarFile, TarInfo
from js9 import j
from .ExecutorBase import *
from docker.models.containers import Container

class ExecutorDocker(ExecutorBase):

    def __init__(self, container, debug=False, checkok=True):

        ExecutorBase.__init__(self, debug=debug, checkok=checkok)

        if not isinstance(container, Container):
            raise ValueError("Expected container variable as instance of running docker container")

        # Check if docker container is running and if the base image has bash installed
        result = container.exec_run('bash -c "echo test"')
        if result.exit_code != 0:
            raise ValueError("Container does not have bash installed! Need bash for using prefab")
        self.container = container
        self.type = "docker"

        self.cache = j.data.cache.get(id="executor:%s" % self.id)
        self.cache.reset()

        self._id = None

        self._logger = j.logger.get("executordocker%s" % self.container.id)

    @classmethod
    def from_local_container(cls, id_or_name):
        dockerd = docker.from_env()
        for con in dockerd.containers.list():
            if id_or_name in (con.id, con.name):
                return cls(con)
        raise KeyError("Container with id or name '%s' not found!" % id_or_name)

    @property
    def logger(self):
        return self._logger

    def exists(self, path):
        if path == "/env.sh":
            raise RuntimeError("SS")

        result = self.container.exec_run('bash -c "test -e %s"' % path)
        if result.exit_code > 0:
            return False
        else:
            return True        

    @property
    def id(self):
        return self.container.id

    def file_read(self, path):
        file_name = os.path.basename(path)
        data, _ = self.container.get_archive(path)
        buf = BytesIO()
        for chunk in data:
            buf.write(chunk)
        buf.seek(0)
        with TarFile(mode='r', fileobj=buf) as tarf:
            for tari in tarf:
                if tari.name == file_name:
                    reader = tarf.extractfile(tari)
                    return reader.read().decode("utf8")

    def file_write(self, path, content, mode=None, owner=None, group=None, append=False,hide=False):
        if append and self.exists(path):
            content = self.file_read(path) + content
        file_name = os.path.basename(path)
        dir_name = os.path.dirname(path)
        buf = BytesIO()
        with TarFile("write_file", mode='w', fileobj=buf) as tarf:
            cmdf = BytesIO()
            length = cmdf.write(content.encode('utf8'))
            cmdf.seek(0)
            tari = TarInfo(name=file_name)
            tari.size = length
            if not mode is None:
                tari.mode = mode
            if not owner is None:
                tari.owner = owner
            if not group is None:
                tari.group = group
            tarf.addfile(tari, cmdf)
        self.container.put_archive(dir_name, buf.getvalue())

    def executeRaw(self, cmd, die=True, showout=False):
        cmd_file = j.sal.fs.joinPaths("/", str(uuid.uuid4()))
        try:
            self.file_write(cmd_file, cmd)
            result = self.container.exec_run("bash %s 2> %s.stderr" % (cmd_file, cmd_file), stderr=False)
            output = result.output.decode("utf8")
            if self.exists("%s.stderr" % cmd_file):
                err_output = self.file_read("%s.stderr" % cmd_file).decode('utf8')
            else:
                err_output = ""
            if die and result.exit_code != 0:
                raise RuntimeError("Error in:\n%s\n***\n%s\n%s" % (cmd, output, err_output))
            if showout:
                self.logger.info(output)
                if err_output:
                    self.logger.info(err_output)
            return result.exit_code, output, err_output
        finally:
            self.container.exec_run('bash -c "rm %s; rm %s.stderr"' % (cmd_file, cmd_file))

    def execute(self, cmds, die=True, checkok=False, showout=True, timeout=0, env={}, asScript=False, hide=False):
        """
        return (rc,out,err)
        """
        if hide:
            showout = False

        cmds2 = self._transformCmds(cmds, die, checkok=checkok, env=env)

        # online command, we use prefab
        if showout:
            self.logger.info("EXECUTE %s %s" % (self.id, cmds))
        else:
            if not hide:
                self.logger.debug("EXECUTE %s %s" % (self.id, cmds))

        rc, out, err = self.executeRaw(cmds2, die=die, showout=showout)

        if hide is False:
            self.logger.debug("EXECUTE OK")

        if checkok and die:
            out = self.docheckok(cmds, out)

        return rc, out, err

    def upload(self, source, dest, dest_prefix="", recursive=True, createdir=True,
               rsyncdelete=True, ignoredir=['.egg-info', '.dist-info', '__pycache__', ".git"], keepsymlinks=False):
        if dest_prefix != "":
            dest = j.sal.fs.joinPaths(dest_prefix, dest)
        if dest[0] != "/":
            raise j.exceptions.RuntimeError("need / in beginning of dest path")
        tmpdir = j.sal.fs.joinPaths("/tmp", str(uuid.uuid4()))
        try:
            j.sal.fs.copyDirTree(
                source,
                tmpdir,
                keepsymlinks=keepsymlinks,
                deletefirst=False,
                overwriteFiles=True,
                ignoredir=ignoredir,
                ignorefiles=[".egg-info"],
                rsync=True,
                ssh=False,
                recursive=recursive,
                createdir=True,
                rsyncdelete=rsyncdelete)
            archiveid = str(uuid.uuid4())
            j.sal.process.execute("tar -cvf %s.tar *" % archiveid, showout=False, cwd=tmpdir)
            with open(j.sal.fs.joinPaths(tmpdir, "%s.tar" % archiveid), 'rb') as fileh:
                data = fileh.read()
            if createdir:
                self.executeRaw("mkdir -p %s" % dest)
                self.container.put_archive(dest, data)
        finally:
            j.sal.fs.removeDirTree(tmpdir)

    def download(self, source, dest, source_prefix="", recursive=True):
        if source_prefix != "":
            source = j.sal.fs.joinPaths(source_prefix, source)
        if source[0] != "/":
            raise j.exceptions.RuntimeError(
                "need / in beginning of source path")
        tmptar = j.sal.fs.joinPaths("/tmp", "%s.tar" % str(uuid.uuid4()))
        tmpdir = j.sal.fs.joinPaths("/tmp", str(uuid.uuid4()))
        try:
            data, _ = self.container.get_archive(source)
            with open(tmptar, 'wb') as fileh:
                for chunk in data:
                    fileh.write(chunk)
            j.sal.process.execute("tar -xvf %s" % tmptar, showout=False, cwd=tmpdir)
            j.sal.fs.copyDirTree(
                tmpdir,
                dest,
                keepsymlinks=True,
                deletefirst=False,
                overwriteFiles=True,
                ignoredir=[
                    ".egg-info",
                    ".dist-info"],
                ignorefiles=[".egg-info"],
                rsync=True,
                recursive=recursive)
        finally:
            j.sal.fs.remove(tmptar)
            j.sal.fs.removeDirTree(tmpdir)

    def __repr__(self):
        return ("Executor docker: %s" % self.id)

    __str__ = __repr__
