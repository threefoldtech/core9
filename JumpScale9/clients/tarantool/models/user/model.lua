box.schema.space.create('user',{if_not_exists= true, engine="memtx"})

box.space.user:create_index('primary',{ type = 'hash', parts = {1, 'unsigned'}, if_not_exists= true})
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
    if id=0 then
        res = box.space.user:auto_increment({data})
        return res[0]
    else
        box.space.user:put{id,data}
        return id
    end                
end

box.schema.func.create('model_user_set', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function','model_user_set',{ if_not_exists= true})

function model_user_del(guid)
    --todo
    return True
end
box.schema.func.create('model_user_del', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_user_del',{ if_not_exists= true})

function model_user_find(query)
    --todo
    return True
end
box.schema.func.create('model_user_find', {if_not_exists = true})
box.schema.user.grant('user', 'execute', 'function', 'model_user_find',{ if_not_exists= true})

