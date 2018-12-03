
class dependencies():

    def __init__(self, do):
        self.do = do

    def base(self):
        url = "https://raw.githubusercontent.com/uiri/toml/master/toml.py"
        from IPython import embed
        print("DEBUG NOW base")
        embed()
        raise RuntimeError("stop debug here")

    def all(self, executor=None):
        C = """
        uvloop
        redis
        paramiko
        #watchdog
        gitpython
        click
        pymux
        uvloop
        pyyaml
        ipdb
        requests
        netaddr
        ipython
        path.py
        colored-traceback
        pudb
        colorlog
        msgpack-python
        pyblake2
        brotli
        pysodium
        ipfsapi
        curio
        asyncssh
        autopep8
        pytoml
        sanic
        jsonschema
        peewee
        docker
        toml
        pystache
        python-jose
        python-dateutil
        """
        self.do.pip(C, executor=executor)
        self.do.execute("pip3 install https://github.com/tony/libtmux/archive/master.zip --upgrade")
        #self.do.execute("apt-get install -y python-colorlog")
        self.capnp(executor=executor)

    def capnp(self, executor=None):
        C = '''
        set -ex
        cd /tmp
        curl -O https://capnproto.org/capnproto-c++-0.5.3.tar.gz
        rm -rf capnproto-c++-0.5.3
        tar zxf capnproto-c++-0.5.3.tar.gz
        cd capnproto-c++-0.5.3
        sed -i /'define KJ_HAS_BACKTRACE'/d src/kj/exception.c++
        ./configure
        make -j6 check
        sudo make install
        cd ..
        rm -rf capnproto-c++-0.5.3
        rm -f capnproto-c++-*
        '''
        if self.do.isAlpine():
            self.do.executeBashScript(C, executor=executor)
        self.do.pip("cython", executor=executor)
        self.do.pip("pycapnp", executor=executor)

    def osx(self, all=False):
        # self.do.execute("sudo chflags nohidden /opt")
        for item in ["tmux", "psutils"]:
            self.do.execute("brew unlink %s;brew install %s;brew link --overwrite %s" % (item, item))
            cmds = "tmux psutils"
        for item in ["libtiff", "libjpeg", "jpeg", "webp", "little-cms2"]:
            self.do.execute("brew unlink %s;brew install %s;brew link --overwrite %s" % (item, item))

    def portal(self, executor=None):
        C = """
        mongoengine
        """
        self.do.pip(C, executor=executor)

    def flist(self, executor=None):
        self.do.execute("apt-get install -y librocksdb-dev libhiredis-dev libbz2-dev", executor=executor)
        self.do.pip("pyrocksdb g8storclient", executor=executor)

    # OBSOLETE
    # """
    # all
    # hiredis
    # ptpython
    # ptpdb
    #  pip3 install --upgrade http://carey.geek.nz/code/python-fcrypt/fcrypt-1.3.1.tar.gz
    #  dulwich
    #  git
    #  xonsh
    # """
