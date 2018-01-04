from js9 import j
from testcases_base import TestcasesBase
import os, random, pytoml, unittest

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


    @classmethod
    def setUpClass(cls):
        cls.client = j.core.state
        cls.config_path = '/etc/jumpscale9.toml'
        cls.config_file_content = cls.get_config()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        test_config = {
            'key_1':'value_1',
            'key_2':'value_2',
            'dict1':{
                'd_key_1':'d_value_1',
                'd_key_2':True,
                'd_key_3':False
            }
        }
        self.update_config(test_config)

    def tearDown(self):
        self.reset_config()

    def test001_config(self):
        js_config = self.client.config
        self.assertDictEqual(js_config, self.config_file_content)

    def test002_config_get(self):
        # self.lg('Get value of an existing key')
        value = self.client.configGet('key_1')
        self.assertEqual(value, 'value_1')

        # self.lg('Get value of a non existing key')
        with self.assertRaises(j.exceptions.Input) as e:
            self.client.configGet('new_key')
        
        # self.lg('Get value of a non existing key with default value and set is false')
        value = self.client.configGet('new_key', defval='new_value')
        self.assertEqual(value, 'new_value')
        self.assertFalse(self.client.config.get('fake_key'))

        # self.lg('Get value of non existing key with default value and set is true')
        value = self.client.configGet('new_key', defval='new_value', set=True)
        self.assertEqual(value, 'new_value')
        self.assertEqual(self.client.config.get('new_key'), 'new_value')

    
    def test003_config_get_for_dict(self):
        pass

    def test004_config_get_for_dict_bool(self):
        pass

    def test005_config_set(self):
        pass

    def test006_config_set_in_dict(self):
        pass

    def test007_config_set_in_dict_bool(self):
        pass

    def test008_config_path(self):
        pass

    def test009_config_me_path(self):
        pass

    def test010_config_save(self):
        pass

    def test011_config_update(self):
        pass


if __name__ == '__main__':
    unittest.main()