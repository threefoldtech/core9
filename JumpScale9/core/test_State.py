import pytest
import tempfile
from js9 import j

from .State import ClientConfig, State


class TestStateClientConfig:

    def setup_method(self):
        temp_dir = j.sal.fs.getTmpDirPath()
        j.core.state.configJSPath = temp_dir + "/jumpscale9.toml"
        j.core.state.configStatePath = temp_dir + "/state.toml"
        j.core.state.configMePath = temp_dir + "/me.toml"

        j.core.state._configState = {}
        j.core.state._configJS = {}
        j.core.state.configMe = {}

    def teardown_method(self):
        j.core.state.configJSPath = j.core.state.executor.stateOnSystem["path_jscfg"] + "/jumpscale9.toml"
        j.core.state.configStatePath = j.core.state.executor.stateOnSystem["path_jscfg"] + "/state.toml"
        j.core.state.configMePath = j.core.state.executor.stateOnSystem["path_jscfg"] + "/me.toml"
        j.core.state._configState = j.core.state.executor.stateOnSystem["cfg_state"]
        j.core.state._configJS = j.core.state.executor.stateOnSystem["cfg_js9"]
        j.core.state.configMe = j.core.state.executor.stateOnSystem["cfg_me"]

    def test_clientConfigSetGet(self):
        category = 'test'
        instance = 'foo'
        data = {'hello': 'world'}
        j.core.state.clientConfigSet(category, instance, data)

        cfg = j.core.state.clientConfigGet('test', 'foo')
        assert cfg.data == data
        assert cfg.category == category
        assert cfg.instance == instance
        assert cfg.key == "client_%s_%s" % (category, instance)

        # when getting from non existing instance, return an empty ClientConfig
        instance = 'nonexists'
        cfg = j.core.state.clientConfigGet(category, instance)
        assert cfg.data == {}
        assert cfg.category == category
        assert cfg.instance == instance
        assert cfg.key == "client_%s_%s" % (category, instance)

    def test_clientConfigSetGet_wrong_data_type(self):
        with pytest.raises(ValueError):
            j.core.state.clientConfigSet('test', 'foo', "string")
        with pytest.raises(ValueError):
            j.core.state.clientConfigSet('test', 'foo', 1)
        with pytest.raises(ValueError):
            j.core.state.clientConfigSet('test', 'foo', ['hello', 'world'])

    def test_clientConfigList(self):
        # set some config
        category = 'test'
        instance = 'foo'
        data = {'hello': 'world'}
        j.core.state.clientConfigSet(category, instance + "1", data)
        j.core.state.clientConfigSet(category, instance + "2", data)

        cfgs = j.core.state.clientConfigList(category)
        assert len(cfgs) == 2

        cfgs = j.core.state.clientConfigList('nonexists')
        assert len(cfgs) == 0
