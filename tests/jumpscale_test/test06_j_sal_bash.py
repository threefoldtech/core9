from js9 import j
import os, random, unittest
from testcases_base import TestcasesBase

class TestBASH(TestcasesBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bash = j.tools.bash.get()

    def test001_env(self):
        """ JS-038

        **Test Scenario:**
        #. Get all environment variables using bash.env.
        #. Check that all environment variables exsits.
        """
        self.assertDictEqual(self.bash.env.__dict__['_data'], os.environ.__dict__['_data'])
    
    @unittest.skip('https://github.com/Jumpscale/core9/issues/175')
    def test002_get_env(self):
        """ JS-039

        **Test Scenario:**
        #. Get specific environment variable and validate its value, should succeed.
        #. Get non-existing environment variable, should fail.
        """
        self.lg.info('Get specific environment variable and validate its value, should succeed')
        env_var = random.choice(list(self.bash.env.keys()))
        self.assertEqual(self.bash.envGet(env_var), os.getenv(env_var))

        self.lg.info('Get non-existing environment variable, should fail')
        with self.assertRaises(KeyError):
            self.bash.envGet(self.random_string())
    
    @unittest.skip('https://github.com/Jumpscale/core9/issues/175')
    def test003_set_env(self):
        """ JS-040

        **Test Scenario:**
        #. Set new environment variable.
        #. Check that the new environment variable is added, should succeed.
        #. Update existing environment variable's value, should succeed.
        """
        self.lg.info('Set new environment variable')
        key = self.random_string()
        value = self.random_string()
        self.bash.envSet(key, value)

        self.lg.info('Check that the new environment variable is added, should succeed')
        self.assertEqual(self.bash.envGet(key), value)
        self.assertEqual(self.bash.env[key], value)

        self.lg.info('Update existing environment variable\'s value, should succeed')
        new_value = self.random_string()
        self.bash.envSet(key, new_value)
        self.assertEqual(self.bash.envGet(key), value)
        self.assertEqual(self.bash.env[key], value) 

    def test004_delete_env(self):
        """ JS-041

        **Test Scenario:**
        #. Set new environment variable.
        #. Delete environment variable, should succeed.
        #. Delete non-existing environment variable, shoild fail.
        """
        self.lg.info('Set new environment variable')
        key = self.random_string()
        value = self.random_string()
        self.bash.envSet(key, value)

        self.lg.info('Delete environment variable, should succeed')
        self.bash.envDelete(key)

        with self.assertRaises(KeyError):
            self.bash.env[key]

        with self.assertRaises(KeyError):
            self.bash.envGet(key)
   
class TestPROFILEJS(TestcasesBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        bash = j.tools.bash.get()
        cls.profilejs = bash.profileJS

    def test01_env_set(self):
        """ JS-042

        **Test Scenario:**
        #. Set new environment variables.
        #. Check that the environment variable in profilejs, should succeed.
        #. Get the environment variable, should succeed.        
        """
        self.lg.info('Set new environment variables')
        key = self.random_string()
        value = self.random_string()
        self.profileJS.envSet(key, value)

        self.lg.info('Check that the environment variable in profilejs, should succeed')
        self.assertEqual(self.profileJS.envGet(key), value)
        self.assertIn('{0}="{1}"\nexport {0}'format(key, value), str(self.profileJS))

        self.lg.info('Get the environment variable, should succeed')
        self.assertEqual(self.profileJS.envGet(key))

    def test02_env_get(self):
        """ JS-043

        **Test Scenario:**
        #. Set new environment variables.
        #. Check that the environment variable in profilejs, should succeed.
        #. Get the environment variable, should succeed.        
        """
        pass

    def test03_env_delete(self):
        """ JS-044

        **Test Scenario:**
        #. Set new environment variable.
        #. Delete environment variable, should succeed.
        #. Delete non-existing environment variable, shoild fail.
        """
        pass