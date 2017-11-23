# Prefab

Prefab makes it easy to automate server installations and create configuration recipes by wrapping common administrative tasks, such as installing packages and creating users and groups, in Python functions.

To use prefab you first need to get an executor that can be local or remote.

To get local a executor:
```
executor = j.tools.executorLocal
prefab = j.tools.prefab.get(executor)
```

Or to get a remote executor:
```
executor = j.tools.executor.getSSHBased(addr, port, login, passwd)
prefab = j.tools.prefab.get(executor)
```


## Examples

- Print the environment variables of a remote machine:
  ```
  executor = j.tools.executor.getSSHBased(addr, port, login, passwd)
  prefab = j.tools.prefab.get(executor)
  print (prefab.bash.envment)
  ```

- Install MongoDB:
  ```
  prefab.db.mongodb.install
  ```

- Copy a file:
  ```
  prefab.core.file_copy("/opt/code/file1", "/opt/code/file2")
  ```

For more information on Prefab check the [Prefab documentation](https://github.com/Jumpscale/prefab9/tree/master/docs).

```
!!!
title = "Prefab"
date = "2017-04-08"
tags = []
```
