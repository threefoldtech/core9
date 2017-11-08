box.cfg()

box.schema.space.create('user',{if_not_exists= true, engine="memtx"})

box.space.user:create_index('primary',{ parts = {1, 'unsigned'}, if_not_exists= true})
-- box.space.user:create_index('secondary', {type = 'tree', parts = {2, 'string'}, if_not_exists= true})

box.schema.user.create('user', {password = 'secret', if_not_exists= true})

function model_user_get(id)
    return box.space.user:get(id)
end

box.schema.func.create('model_user_get', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_user_get',{ if_not_exists= true})

function model_user_get_json(id)
    bdata= box.space.user:get(id)
    return model_capnp_user.User.parse(bdata)
end

box.schema.func.create('model_user_get_json', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_user_get_json',{ if_not_exists= true})

function model_user_set(id,data)
    obj=model_capnp_user.User.parse(data) --deserialze capnp
    if id==0 then
        res = box.space.user:auto_increment({data})
        return res[1]
    else
        box.space.user:put{id,data}
        return id
    end                
end

function model_user_del(id)
    return box.space.user:delete(id)
end
box.schema.func.create('model_user_del', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_user_del',{ if_not_exists= true})

function model_user_find(query)
    --todo
    return True
end
box.schema.func.create('model_user_find', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_user_find',{ if_not_exists= true})

data={
    id=10,
    description="a description",
    name="aname"
}

package.path = '/opt/code/github/jumpscale/core9/JumpScale9/clients/tarantool/systemscripts/?.lua;' .. package.path
package.path = '/tmp/lua/?.lua;' .. package.path

model_capnp_user=require("model_capnp_user")

bdata=model_capnp_user.User.serialize(data)
print(model_capnp_user.User.parse(bdata)["name"])

print(model_user_set(0,"s"))

-- print (model_user_set(0,bdata))