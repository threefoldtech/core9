from js9 import j
from testcases_base import TestcasesBase
import os, random, pytoml, unittest, uuid

class TestJSTATE(TestcasesBase):

    @classmethod
    def get_config(cls):
        with open(cls.config_path, 'r') as f:
            content = pytoml.load(f)
        return content

    @classmethod
    def reset_config(cls):
        with open(cls.config_path, 'w') as f:
            pytoml.dump(cls.config_file_content, f)
    
    @classmethod
    def update_config(cls, data):
        content = dict(cls.config_file_content)
        content.update(data)
        with open(cls.config_path, 'w') as f:
            pytoml.dump(content, f)
        return content

    @classmethod
    def setUpClass(cls):
        cls.client = j.core.state
        cls.config_path = '/root/js9host/cfg/jumpscale9.toml'
        cls.config_file_content = cls.get_config()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        super(TestJSTATE).setUp()
        #self.lg('Add test configration (setUp)')
        test_config = {
            'key_1':'value_1',
            'key_2':'value_2',
            'dict_1':{
                'd_key_1':'d_value_1',
                'd_key_2':True,
                'd_key_3':False
            }
        }
        self.client._configJS = self.update_config(test_config)

    def tearDown(self):
        #self.lg('Remove test configration (tearDown)')
        self.reset_config()
        super(TestJSTATE).tearDown()

    def test001_config_get(self):
        # self.lg('Get value of an existing key')
        value = self.client.configGet('key_1')
        self.assertEqual(value, 'value_1')

        # self.lg('Get the value of a non-existing key')
        with self.assertRaises(j.exceptions.Input) as e:
            self.client.configGet('new_key')
        
        # self.lg('Get the value of a non-existing key with default value and set is false')
        value = self.client.configGet('new_key', defval='new_value')
        self.assertEqual(value, 'new_value')

        with self.assertRaises(j.exceptions.Input) as e:
            self.client.configGet('new_value')

        # self.lg('Get the value of non existing key with default value and set is true')
        value = self.client.configGet('new_key', defval='new_value', set=True)
        self.assertEqual(value, 'new_value')
        self.assertEqual(self.client.configGet('new_key'), 'new_value')
    
    def test002_config_get_form_dict(self):
        # self.lg('Get the value of an existing key from existing dict')
        value = self.client.configGetFromDict('dict_1', 'd_key_1')
        self.assertEqual(value, 'd_value_1')

        # self.lg('Get the value of a non-existing key from non-existing dict')
        with self.assertRaises(RuntimeError) as e:
            self.client.configGetFromDict('new_dict', 'new_dict_key')

        self.assertEqual(self.client.configGet('new_dict'), {})

        # self.lg('Get the value of an non-existing key from existing dict with default value')
        value = self.client.configGetFromDict('new_dict', 'new_dict_key', default='new_dict_value')
        self.assertEqual(value, 'new_dict_value')

    @unittest.skip('https://github.com/Jumpscale/core9/issues/157')
    def test003_config_get_form_dict_bool(self):
        # self.lg('Get the value of an existing key from existing dict')
        value = self.client.configGetFromDictBool('dict_1', 'd_key_2')
        self.assertEqual(value, 'd_value_1')
        self.assertTrue(isinstance(value, bool))

        # self.lg('Get the value of a non-existing key from non-existing dict')
        with self.assertRaises(RuntimeError) as e:
            self.client.configGetFromDictBool('new_dict', 'new_dict_key')

        self.assertEqual(self.client.config.get('new_dict'), {})

        # self.lg('Get the value of an non-existing key from existing dict with default value')
        value = self.client.configGetFromDictBool('new_dict', 'new_dict_key', default=1)
        self.assertEqual(value, 'new_dict_value')
        self.assertTrue(isinstance(value, bool))

    def test004_config_set(self):
        # self.lg('Set new key, value with save equalt to true')
        key = str(uuid.uuid4()).replace('-', '')[10]
        value = str(uuid.uuid4()).replace('-', '')[10]
        self.assertTrue(self.client.configSet(key, value))
        self.assertEqual(self.get_config().get(key), value)

        # self.lg('Set new key, value with save equalt to false')
        key = str(uuid.uuid4()).replace('-', '')[10]
        value = str(uuid.uuid4()).replace('-', '')[10]
        self.assertTrue(self.client.configSet(key, value, save=False))
        self.assertFalse(self.get_config().get(key))

        # self.lg('Set existing key with new value and save equalt to true')
        self.assertTrue(self.client.configSet('key_1', 'new_value_1'))
        self.assertEqual(self.get_config().get('key_1'), 'new_value_1')

        # self.lg('Set new key with new value and save equalt to false')
        self.assertTrue(self.client.configSet('key_2', 'new_value_2', save=False))
        self.assertFalse(self.get_config().get('key_2'), 'value_2')

        # self.lg('Set existing key with the same value and save equalt to true')
        self.assertFalse(self.client.configSet('key_1', 'new_value_1'))
        self.assertEqual(self.get_config().get('key_1'), 'new_value_1')

        # self.lg('Set new key with the same value and save equalt to false')
        self.assertFalse(self.client.configSet('key_2', 'new_value_2', save=False))
        self.assertFalse(self.get_config().get('key_2'), 'value_2')


    def test005_config_set_in_dict(self):
        pass

    def test006_config_set_in_dict_bool(self):
        pass

    def test007_config_path(self):
        pass

    def test008_config_me_path(self):
        pass

    def test009_config_save(self):
        pass

    def test010_config_update(self):
        pass


if __name__ == '__main__':
    unittest.main()