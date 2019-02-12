from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
import os


def _post_install(libname, libpath):
    from Jumpscale import j  # here its still the boostrap Jumpscale

    # remove leftovers
    if not "PBASE" in os.environ:
        #should only be done when not in build dir
        for item in j.sal.fs.find("/usr/local/bin/", fileregex="js_*"):
            j.sal.fs.remove("/usr/local/bin/%s" % item)

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
    name='Jumpscale',
    version='9.5.0',
    description='Automation framework for cloud workloads',
    long_description=long_description,
    url='https://github.com/threefoldtech/jumpscale_core',
    author='ThreeFoldTech',
    author_email='info@threefold.tech',
    license='Apache',
    packages=find_packages(),

    # IF YOU CHANGE ANYTHING HERE, LET DESPIEGK NOW (DO NOT INSTALL ANYTHING WHICH NEEDS TO COMPILE)
    install_requires=[
        'GitPython>=2.1.3',
        'click>=6.7',
        'colored_traceback',
        'colorlog>=2.10.0',
        'httplib2>=0.10.3',
        'ipython<6.5.0,>=6.0.0',
        'libtmux>=0.7.1',
        'netaddr>=0.7.19',
        'path.py>=10.3.1',
        'pystache>=0.5.4',
        'python-dateutil>=2.6.0',
        'pytoml>=0.1.12',
        'toml',
        'redis<3.0.0',
        'requests>=2.13.0',
        'future>=0.16.0',
        'watchdog',
        'msgpack-python',
        'npyscreen',
        'pyyaml',
        'pyserial>=3.0'
        'docker>=3',
        'fakeredis',
        'ssh2-python',
        'parallel_ssh>=1.4.0',
        'psutil>=5.4.3',
        'Unidecode>=1.0.22',
        'bpython',
        'six>=1.12.0',
    ],
    cmdclass={
        'install': install,
        'develop': develop,
        'developement': develop
    },
    scripts=[
        'cmds/js_shell',
        'cmds/js_code',
        'cmds/js_docker',
        'cmds/js_doc',
    ],
)
