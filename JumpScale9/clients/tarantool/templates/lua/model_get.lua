local function get(key)
    return box.space.$name:get(key)
end

box.schema.func.create('get', {if_not_exists = true})
box.schema.user.grant('$login', 'execute', 'function', 'get',{ if_not_exists= true})

