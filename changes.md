
## a big cleanup just happened, oh my ...

- references to version of jumpscale are removed (no longer 9)
    - means all commands are now js_shell, js_init, ...
    - from jumpscale import j (no longer js9)
- bash tools removed
- docker support removed -> we now do everything in 0-OS (eat our own dogfood)
- less repositories to deal with (core,lib,prefab) 
- all 0-robot templates are now in 1 repo
  

  ## still to fix

lots of things which were on this readme

need to redo:
```markdown

[![Join the chat at https://gitter.im/Jumpscale/jumpscale_core](https://badges.gitter.im/Jumpscale/jumpscale_core.svg)](https://gitter.im/Jumpscale/jumpscale_core?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) ![travis](https://travis-ci.org/Jumpscale/core.svg?branch=master)


```