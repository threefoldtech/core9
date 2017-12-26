# JSLoader

#### Introduction
**j** namespace was made to provide jumpscale modules with no need to import anything or to know how does these modules comunicate,
 It also make it much easyer to add new module from your own repo  
what JSLoader provides is a service to collect all modules and plugins needed and make it available through **j** 
##### Example  
  
```python
j.secondary_namespace.module...
```
#### How to
To add new module to be loaded by the JSLoader:
* create your module
* add \_\_jslocation__ field to your factory like ```self.__jslocation__ = "j.clients.newclient"``` 
* add your new module to JumpScale configurations:
  you can do this manually by adding your new module to jumpscale9.toml file located in ```<host_dir>/cfg/jumpscale9.toml``` in plugins section
  **or**  you can do this using js9 like this
    ```python
    plugins = j.core.state.configGet('plugins')
    plugins["pluginName"] = "plugin/path"
    j.core.state.configSet('plugins',plugins)
    ```
    **Note:** plugin name should contain "*JumpScale9*"
* run ```js9_init``` or from js9 call ```j.tools.JSloader.generate()```

#### Add new secondary namespace
 to add new secondary namespace like ```j.secondary_namespace``` you will need to add new field to Jumpsacle9 class in ```core9/JumpScale9/__init__.py``` 
#### Restrictions
* Module path should contain "*jumpscale9*"
* Class file name can't start with '_', lower case letter, 'jsloader' or 'actioncontroller'
