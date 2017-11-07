require ("lfs")
lfs.mkdir("/tmp/lua")


function add_lua_script (name,content)
    local fio = require('fio')
    local errno = require('errno')  
    path = "/tmp/lua/".. name .. ".lua"  
    local f = fio.open(path, {'O_CREAT', 'O_WRONLY', 'O_APPEND'},
        tonumber('0666', 8))
    if not f then
        error("Failed to open file: "..errno.strerror())
    end
    f:write(content);
    f:close()
end



-- box.schema.func.create('add_lua_script', {if_not_exists = true})
-- box.schema.user.create('guest1', {password = 'secret', if_not_exists= true})
-- box.schema.user.grant('guest1', 'execute', 'function', 'add_lua_script',{ if_not_exists= true})
