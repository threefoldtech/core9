function $funcname()
    local space = box.space['$name']
    local keys = {}
    for _, v in space:pairs() do
        table.insert(keys, v[1])
    end

    return keys
end

box.schema.func.create('$funcname', {if_not_exists = true})
box.schema.user.grant('$login', 'execute', 'function', '$funcname',{ if_not_exists= true})

