from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
import os


def _post_install(libname, libpath):
    from JumpScale9 import j  # here its still the boostrap JumpScale9

    #NO LONGER NEEDED
    # # add this plugin to the config
    # c = {}  # first time need to make sure is empty
    # c[libname] = libpath
    # j.core.state.configSet('plugins', c)

    #remove leftovers
    for item in j.sal.fs.find("/usr/local/bin/",fileregex="js9*"):
         j.sal.fs.remove("/usr/local/bin/%s"%item)
    j.sal.fs.remove(j.sal.fs.joinPaths(j.dirs.HOMEDIR,".jumpscale9.toml"))
    
    j.tools.executorLocal.initEnv()
    j.tools.jsloader.generate()
    


class install(_install):

    def run(self):
        _install.run(self)
        libname = self.config_vars['dist_name']
        libpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), libname)
        self.execute(_post_install, (libname, libpath), msg="Running post install task")


class develop(_develop):

    def run(self):
        _develop.run(self)
        libname = self.config_vars['dist_name']
        libpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), libname)
        self.execute(_post_install, (libname, libpath), msg="Running post install task")


long_description = ""
try:
    from pypandoc import convert
    long_description = convert('README.md', 'rst')
except ImportError:
    long_description = ""


setup(
    name='JumpScale9',
    version='9.1.2',
    description='Automation framework for cloud workloads',
    long_description=long_description,
    url='https://github.com/Jumpscale/core9',
    author='GreenItGlobe',
    author_email='info@gig.tech',
    license='Apache',
    packages=find_packages(),

    # IF YOU CHANGE ANYTHING HERE, LET DESPIEGK NOW
    install_requires=[
        'GitPython>=2.1.3',
        'click>=6.7',
        'colored_traceback',
        'colorlog>=2.10.0',
        'httplib2>=0.10.3',
        'ipython>=6.0.0',
        'libtmux>=0.7.1',
        'netaddr>=0.7.19',
        'path.py>=10.3.1',
        'pystache>=0.5.4',
        'python-dateutil>=2.6.0',
        'pytoml>=0.1.12',
        'toml',
        'redis>=2.10.5',
        'requests>=2.13.0',
        'future>=0.16.0',
        'psutil',
        'watchdog',
        'msgpack-python',
        'colorlog',
        'npyscreen'
    ],
    cmdclass={
        'install': install,
        'develop': develop,
        'developement': develop
    },
    scripts=[
        'cmds/js9',
        'cmds/js9_code',
        'cmds/js9_docker',
        'cmds/js9_docs',
    ],
)
