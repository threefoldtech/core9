from jumpscale import j
import os
import time
import subprocess


def test_zdb_backend():
    print('***********Testing zdb backend***********')
    # clone 0-db adnd start it
    path = '/tmp/testbackend/'
    j.sal.fs.removeDirTree(path)
    j.clients.git.pullGitRepo('https://github.com/threefoldtech/0-db', path)
    j.sal.process.execute('make', cwd=path)
    log = open('{}logs'.format(path), 'w')
    process = subprocess.Popen('bin/zdb', cwd=path, stdout=log, stderr=log)
    j.core.state.configSetInDict('myconfig', 'backend', 'db')
    j.core.state.configSetInDict('myconfig', 'backend_addr', 'localhost:9900')
    j.core.state.configSetInDict('myconfig', 'adminsecret', '')
    j.core.state.configSetInDict('myconfig', 'secrets', '')
    j.core.state.configSetInDict('myconfig', 'namespace', 'testzdbbackend')
    os.system('pytest test_backend.py -vs') # start it in a different process for the config changes to take effect
    process.kill()
    log.close()
    j.sal.fs.removeDirTree(path)


def test_file_backend():
    print('***********Testing file backend***********')
    j.core.state.configSetInDict('myconfig', 'backend', 'file')
    os.system('pytest test_backend.py -vs') # start it in a different process for the config changes to take effect


if __name__ == '__main__':
    initial_config = dict(j.core.state.configGet('myconfig'))
    try:
        test_zdb_backend()
        test_file_backend()
    except Exception as e:
        print(e)
    finally:
        print('Reseting config')
        j.core.state.configSet('myconfig', initial_config)
