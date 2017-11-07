
box.schema.space.create('$name',{if_not_exists= true, engine="memtx"}) --'vinyl'
box.space.$name:create_index('primary',{ type = 'hash', parts = {1, 'unsigned'}, if_not_exists= true})
box.space.$name:create_index('secondary', {type = 'tree', parts = {2, 'string'}, if_not_exists= true})

box.schema.user.create('$login', {password = '$passwd', if_not_exists= true})

function model_user_set(obj)

end

function model_user_del(guid)
    
end

function model_user_find(guid)
    
end