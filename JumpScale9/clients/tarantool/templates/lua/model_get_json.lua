function $funcname(key)
    local res = model_$name_get(key)
    if res == nil then
        return nil
    else
        return model_capnp_$name.$Name.parse(res[3])
    end
end

box.schema.func.create('$funcname', {if_not_exists = true})
box.schema.user.grant('$login', 'execute', 'function', '$funcname',{ if_not_exists= true})

