require ("lfs")
lfs.mkdir("/tmp/lua")

package.path = '/tmp/lua/?.lua;' .. package.path


function file_write (name,content)
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



-- schemadef = {
--     player = {
--         type="record",
--         name="player_schema",
--         fields={
--             {name="id", type="long"},
--             {name="name", type="string"},
--             {
--                 name="location",
--                 type= {
--                     type="record",
--                     name="player_location",
--                     fields={
--                         {name="x", type="double"},
--                         {name="y", type="double"}
--                     }
--                 }
--             }
--         }
--     },
-- }

-- avro = require('avro_schema')

-- -- create models
-- ok_m, schema = avro.create(schemadef.player)

-- ok, methods = avro.compile(schema)

box.schema.space.create('tester',{if_not_exists= true, engine="memtx"}) --'vinyl'
box.space.tester:create_index('primary',{ type = 'hash', parts = {1, 'unsigned'}, if_not_exists= true})
box.space.tester:create_index('secondary', {type = 'tree', parts = {2, 'string'}, if_not_exists= true})

-- box.space.tester:upsert{444, "test_i",'{"Item": "widget", "Quantity": 15}'}

box.schema.func.create('write', {if_not_exists = true})
box.schema.user.create('guest1', {password = 'secret', if_not_exists= true})
box.schema.user.grant('guest1', 'execute', 'function', 'write',{ if_not_exists= true})
