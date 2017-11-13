# How to add configurations and states
All configurations are now in one place `/root/js9host/cfg/jumpscale9.toml`
All states are also in one place `/root/js9host/cfg/state.toml`

## Getting config
```
In [1]: j.core.state.configGet('plugins')
Out[1]: {'JumpScale9': '/opt/code/github/jumpscale/core9/JumpScale9/'}
```

## Setting config
```
In [3]: j.core.state.configSet("test", "test config values")
In [4]: j.core.state.configGet('test')
Out[4]: 'test config values'
```


## Getting and setting states
the same as getting and setting config, but use the correct state methods (`stateGet()` and `stateSet()`)