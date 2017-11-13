local function set(key, data)
    box.space.$name:put{key, data}
    return
end

box.schema.func.create('set', {if_not_exists = true})
box.schema.user.grant('$login', 'execute', 'function','set',{ if_not_exists= true})

