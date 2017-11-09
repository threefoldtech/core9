function $funcname(key)
    local count = box.space.$name:count(key)
    return count ~= 0
end

box.schema.func.create('$funcname', {if_not_exists = true})
box.schema.user.grant('$login', 'execute', 'function', '$funcname',{ if_not_exists= true})

