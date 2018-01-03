import os, shutil
from random import randint
from testcases_base import TestcasesBase
from js9 import j


class TestJSALFS(TestcasesBase):
    def test001_changeDir(self):
        """ JS-001

        **Test Scenario:**
        #. Get the current dir
        #. Change the current dir, should succeed
        """
        current_dir = os.getcwd()
        if current_dir == "/root":
            self.assertEqual(j.sal.fs.changeDir('/etc'), '/etc')
        else:
            self.assertEqual(j.sal.fs.changeDir('/root'), '/root')

    def test002_changeDir_longpath(self):
        """ JS-001

        **Test Scenario:**
        #. Create a long path
        #. Change the current dir to this long path, should succeed
        """
        long_path = '/root/test'
        for i in range(0, randint(1, 10)):
            long_path += '/test00%d' % i

        os.makedirs(long_path)
        self.assertEqual(j.sal.fs.changeDir(long_path), long_path)
        shutil.rmtree(long_path)

    def test002_changeDir_file(self):
        """ JS-001

        **Test Scenario:**
        #. Create a file
        #. Change the current dir to this file, should fail
        """
        file_name = "newfile%d.txt" % randint(1, 10000)
        os.mknod(file_name)
        current_dir = os.getcwd() + "newfile.txt"

        with self.assertRaises(ValueError):
            j.sal.fs.changeDir(current_dir)
