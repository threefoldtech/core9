# How to add configurations and states
All configurations are now in one place `/root/jumpscale/cfg/jumpscale.toml`

All states are also in one place `/root/jumpscale/cfg/state.toml`
for example, the state of specific module is it installed or not

## Getting config
```
In [1]: j.core.state.configGet('plugins')
Out[1]: {'Jumpscale': '/opt/code/github/threefoldtech/jumpscale_core/Jumpscale/'}
```

## Setting config
```
In [3]: j.core.state.configSet("test", "test config values")
In [4]: j.core.state.configGet('test')
Out[4]: 'test config values'
```


## Getting and setting states
the same as getting and setting config, but use the correct state methods (`stateGet()` and `stateSet()`)

## Getting state
```
In [1]: j.core.state.stateGet('PrefabPIP')
Out[8]: {'done': {'ensure': True}}
```

## Setting state
```
In [10]: j.core.state.stateSet("key", "value")
Out[10]: True

In [11]: j.core.state.stateGet("key")
Out[11]: 'value'
```

