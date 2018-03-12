from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
import os
import subprocess


def _post_install(libname, libpath):
    from JumpScale9 import j  # here its still the boostrap JumpScale9
    pssh = """
    # WORKAROUND till issue in ssh2 is fixed: https://github.com/ParallelSSH/ssh2-python/issues/23
    pip3 install http://home.maxux.net/wheelhouse/ssh2_python-0.10.0%2B4.g7dc3833.dirty-cp35-cp35m-manylinux1_x86_64.whl
    pip3 install parallel_ssh>=1.4.0
    """
    platformType = j.core.platformtype.get(j.tools.executorLocal)
    if(platformType.osname !=  "ubuntu"):
        psh = """
        pip3 install ssh2-python
        pip3 install parallel_ssh>1.4.0"""
        with open('/tmp/pssh.sh', 'w') as f:
            f.write(psh)
        res = subprocess.check_output(["bash", "/tmp/pssh.sh"])
    else:
        with open('/tmp/pssh.sh', 'w') as f:
            f.write(pssh)
        res = subprocess.check_output(["bash", "/tmp/pssh.sh"])

    # remove leftovers
    for item in j.sal.fs.find("/usr/local/bin/", fileregex="js9*"):
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
    name='JumpScale9',
    version='9.3.0',
    description='Automation framework for cloud workloads',
    long_description=long_description,
    url='https://github.com/Jumpscale/core9',
    author='GreenItGlobe',
    author_email='info@gig.tech',
    license='Apache',
    packages=find_packages(),

    # IF YOU CHANGE ANYTHING HERE, LET DESPIEGK NOW (DO NOT INSTALL ANYTHING WHICH NEEDS TO COMPILE)
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
        'npyscreen',
        'pyyaml',
        'pyserial>=3.4',
        'docker>=3',
        'fakeredis',
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
        'cmds/js9_doc',
    ],
)
